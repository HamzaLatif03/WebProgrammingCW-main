<template>
    <main class="container pt-4">
        <nav class="flex items-center justify-between mb-4">
            <div class="d-flex align-items-center w-100">
                <!-- Left side navigation links -->
                <div class="d-flex gap-2">
                    <router-link class="btn btn-primary" :to="{name: 'hobbies'}">
                        Hobbies
                    </router-link>

                    <router-link class="btn btn-primary" :to="{name: 'Profile Page'}">
                        Profile
                    </router-link>
                </div>
                
                <!-- Right side username and auth buttons -->
                <div class="d-flex align-items-center gap-2 ms-auto">
                    <p class="mb-0 me-3">
                        Username: {{ authStore.isAuthenticated ? authStore.user?.username : 'Not logged in' }}
                    </p>
                    
                    <button 
                        v-if="!authStore.isAuthenticated"
                        
                        class="btn btn-primary"
                    >
                        Login
                    </button>
                    
                    <button 
                        v-else
                        @click="handleLogout" 
                        class="btn btn-danger"
                    >
                        Logout
                    </button>
                </div>
            </div>
        </nav>
        <hr class="border-bottom mb-4">
        <RouterView class="flex-shrink-0" />
    </main>
</template>

<script setup lang="ts">
import { RouterView } from "vue-router";
import { useAuthStore } from './store/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

const handleLogout = () => {
    authStore.logout(router);
};

// const redirectToLogin = () => {
//     window.location.href = '/api/login';
// };
</script>