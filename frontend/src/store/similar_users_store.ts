import { defineStore } from "pinia";
import type { User } from "../types";

export const useSimilarUsersStore = defineStore("similarUsers", {
    state: () => ({
        similarUsers: [] as User[],
        totalPages: 0,
        loading: false,
        error: null as string | null,
    }),
    actions: {
        async fetchSimilarUsers(minAge?: number, maxAge?: number, page: number = 1) {
            this.loading = true;
            try {
                // Construct query parameters
                const params = new URLSearchParams();
                if (minAge !== undefined) params.append('min_age', minAge.toString());
                if (maxAge !== undefined) params.append('max_age', maxAge.toString());
                params.append('page', page.toString());
                
                const url = `/api/similar-users/?${params.toString()}`;
                
                const response = await fetch(url, {
                    credentials: 'include',
                    headers: {
                        'X-CSRFToken': document.querySelector<HTMLMetaElement>('meta[name="csrf-token"]')?.content || '',
                    }
                });
                
                if (!response.ok) {
                    throw new Error(`Failed to fetch similar users: ${response.status}`);
                }
                
                const data = await response.json();
                this.similarUsers = Array.isArray(data) ? data : data.similar_users || [];
                this.totalPages = data.total_pages || 0;
                console.log(this.totalPages, data.total_pages);
            } catch (error) {
                this.error = error instanceof Error ? error.message : 'An error occurred';
                console.error('Error fetching similar users:', error);
            } finally {
                this.loading = false;
            }
        },
    },
});