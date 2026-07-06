import { defineStore } from 'pinia';
import type { User } from '../types';
import { getCSRFToken } from './auth';

export const useUserStore = defineStore('user', {
  state: () => ({
    currentUser: null as User | null,
    loading: false,
    error: null as string | null,
  }),

  actions: {
    async fetchCurrentUser() {
      this.loading = true;
      try {
        const response = await fetch(`/api/user-info/`, {
          credentials: 'include',
          headers: {
            'X-CSRFToken': document.querySelector<HTMLMetaElement>('meta[name="csrf-token"]')?.content || '',
          }
        });
        
        if (!response.ok) {
          throw new Error(`Failed to fetch current user: ${response.status}`);
        }

        this.currentUser = await response.json();
      } catch (error) {
        this.error = error instanceof Error ? error.message : 'An error occurred';
        console.error('Error fetching current user:', error);
      } finally {
        this.loading = false;
      }
    },

    async updateProfile(userData: Partial<User>) {
      try {
        const response = await fetch(`/api/user-info/`, {
          method: 'PUT',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
          },
          body: JSON.stringify(userData),
        });

        if (!response.ok) {
          throw new Error(`Failed to update profile: ${response.status}`);
        }

        const updatedProfile = await response.json();
        this.currentUser = updatedProfile;
      } catch (error) {
        this.error = error instanceof Error ? error.message : 'An error occurred';
        console.error('Error updating profile:', error);
      }
    },
  },
});