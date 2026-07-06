import { defineStore } from 'pinia';
import type { Hobby } from '../types';
import { getCSRFToken } from './auth';

export const useHobbyStore = defineStore('hobby', {
  state: () => ({
    hobbies: [] as Hobby[],
    loading: false,
    error: null as string | null,
  }),

  actions: {
    async fetchHobbies() {
      this.loading = true;
      try {
        const response = await fetch(`/api/hobbies/`, {
          credentials: 'include',
          headers: {
            'X-CSRFToken': document.querySelector<HTMLMetaElement>('meta[name="csrf-token"]')?.content || '',
          }
        });
        
        if (!response.ok) {
          throw new Error(`Failed to fetch hobbies: ${response.status}`);
        }
        
        const data = await response.json();
        this.hobbies = Array.isArray(data) ? data : data.hobbies || [];
      } catch (error) {
        this.error = error instanceof Error ? error.message : 'An error occurred';
        console.error('Error fetching hobbies:', error);
      } finally {
        this.loading = false;
      }
    },

    async addHobby(hobby: Partial<Hobby>) {
      try {
        const response = await fetch(`/api/hobbies/`, {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
          },
          body: JSON.stringify(hobby),
        });

        if (!response.ok) {
          throw new Error(`Failed to add hobby: ${response.status}`);
        }

        const newHobby = await response.json();
        this.hobbies.push(newHobby);
      } catch (error) {
        this.error = error instanceof Error ? error.message : 'An error occurred';
        console.error('Error adding hobby:', error);
      }
    },
  },
});