import { defineStore } from 'pinia';
import { FriendRelationship } from '../types';

let csrfToken: string | null = null;

async function fetchCsrfToken() {
  try {
    await fetch(`/api/set-csrf-token/`, { 
      credentials: 'include'
    });
    const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
    csrfToken = cookie ? cookie.split('=')[1] : null;
  } catch (error) {
    console.error('Error fetching CSRF token:', error);
  }
}

export const useFriendStore = defineStore('friend', {
  state: () => ({
    relationships: [] as FriendRelationship[],
    loading: false,
    error: null as string | null,
    currentUserId: null as number | null,
  }),

  actions: {
    async fetchRelationships() {
      if (!csrfToken) {
        await fetchCsrfToken();
      }
      
      this.loading = true;
      try {
        const response = await fetch(`/api/friendrelationships/`, {
          credentials: 'include',
          headers: {
            'X-CSRFToken': csrfToken || '',
          }
        });
        
        if (!response.ok) {
          throw new Error(`Failed to fetch relationships: ${response.status}`);
        }
        
        const data = await response.json();
        this.relationships = data.relationships || [];
        this.currentUserId = data.current_user_id;
      } 
      catch (error) {
        this.error = error instanceof Error ? error.message : 'An error occurred';
        console.error('Error fetching relationships:', error);
      } 
      finally {
        this.loading = false;
      }
    },

    async sendFriendRequest(receiverId: number) {
      if (!csrfToken) {
        await fetchCsrfToken();
      }

      try {
        console.log('Sending request with token:', csrfToken); 
        console.log('Sending to receiver:', receiverId); 

        const response = await fetch(`/api/friendrelationships/`, {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken || '',
          },
          body: JSON.stringify({ receiver_id: receiverId }),
        });

        if (!response.ok) {
          const errorData = await response.json(); 
          console.error('Server error response:', errorData); 
          throw new Error(`Failed to add relationship: ${response.status}`);
        }

        const newRelationship = await response.json();
        console.log('New relationship created:', newRelationship); 
        this.relationships.push(newRelationship);
      } catch (error) {
        this.error = error instanceof Error ? error.message : 'An error occurred';
        console.error('Error adding relationship:', error);
        throw error; 
      }
    },

    async updateFriendRequest(relationshipId: number, status: 'accepted' | 'rejected') {
      if (!csrfToken) {
        await fetchCsrfToken();
      }

      try {
        const response = await fetch(`/api/friendrelationships/${relationshipId}/`, {
          method: 'PUT',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken || '',
          },
          body: JSON.stringify({ status }),
        });

        if (!response.ok) {
          throw new Error(`Failed to update relationship: ${response.status}`);
        }

        const updatedRelationship = await response.json();
        const index = this.relationships.findIndex(r => r.id === relationshipId);
        if (index !== -1) {
          this.relationships[index] = updatedRelationship;
        }
      } catch (error) {
        this.error = error instanceof Error ? error.message : 'An error occurred';
        console.error('Error updating relationship:', error);
      }
    }
  },
});