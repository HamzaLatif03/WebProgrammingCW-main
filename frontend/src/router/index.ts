// Example of how to use Vue Router

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth.ts'

// 1. Define route components.
// These can be imported from other files
import Home from '../pages/Home.vue';
import ProfilePage from '../pages/ProfilePage.vue';
import NotFound from '../components/NotFound.vue';


let base = (import.meta.env.MODE == 'development') ? import.meta.env.BASE_URL : ''

// 2. Define some routes
// Each route should map to a component.
// We'll talk about nested routes later.
const router = createRouter({
    history: createWebHistory(base),
    routes: [
        { path: '/', name: 'hobbies', component: Home, meta: { requiresAuth: true } },
        { path: '/profile-page/', name: 'Profile Page', component: ProfilePage , meta: { requiresAuth: true } },
        {
          path: '/home',
          redirect: '/'
        },
        
        {
          path: '/:pathMatch(.*)*',
          name: 'NotFound',
          component: NotFound
      }


    ]
})

// Global navigation guard
router.beforeEach(async (to, _from, next) => {
    const authStore = useAuthStore()
    
    if (to.meta.requiresAuth) {
      await authStore.fetchUser()  // Check authentication status
      
      if (!authStore.isAuthenticated) {
        // Redirect to login with return URL
        window.location.href = `/api/login?next=${to.fullPath}`
        return
      }
    }
    next()
  })
export default router
