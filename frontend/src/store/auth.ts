import { defineStore } from 'pinia'
import { Router } from 'vue-router'

interface AuthState {
 user: User | null
 isAuthenticated: boolean
}

interface User {
 username: string
 email: string
 name: string
}

export const useAuthStore = defineStore('auth', {
   state: (): AuthState => {
       const storedState = localStorage.getItem('authState')
       return storedState ? JSON.parse(storedState) : {
           user: null,
           isAuthenticated: false
       }
   },
   actions: {
       async setCsrfToken(): Promise<void> {
           await fetch('/api/set-csrf-token', {
               method: 'GET',
               credentials: 'include'
           })
       },

       async login(username: string, password: string, router: Router | null = null): Promise<void> {
           const response = await fetch('/api/login', {
               method: 'POST',
               headers: {
                   'Content-Type': 'application/json',
                   'X-CSRFToken': getCSRFToken()
               },
               body: JSON.stringify({ username, password }),
               credentials: 'include'
           })
           const data = await response.json()
           if (data.success) {
               this.isAuthenticated = true
               this.saveState()
               if (router){
                   await router.push({name: "home"})
               }
           } else {
               this.user = null
               this.isAuthenticated = false
               this.saveState()
           }
       },

       async logout(_router: Router | null = null): Promise<void> {
           try {
               const response = await fetch('/api/logout/', {
                   method: 'POST',
                   headers: {
                       'X-CSRFToken': getCSRFToken()
                   },
                   credentials: 'include'
               })
               if (response.ok) {
                   this.user = null
                   this.isAuthenticated = false
                   this.saveState()
                   window.location.href = '/api/login'
               }
           } catch (error) {
               console.error('Logout failed', error)
               throw error
           }
       },

       async fetchUser(): Promise<void> {
           try {
               const response = await fetch('/api/user', {
                   credentials: 'include',
                   headers: {
                       'Content-Type': 'application/json',
                       'X-CSRFToken': getCSRFToken()
                   },
               })
               if (response.ok) {
                   const data = await response.json()
                   this.user = data
                   this.isAuthenticated = true
               }
               else{
                   this.user = null
                   this.isAuthenticated = false
               }
           } catch (error) {
               console.error('Failed to fetch user', error)
               this.user = null
               this.isAuthenticated = false
           }
           this.saveState()
       },

       saveState(): void {
           localStorage.setItem('authState', JSON.stringify({
               user: this.user,
               isAuthenticated: this.isAuthenticated
           }))
       }
   }
})

export function getCSRFToken(): string {
   const name = 'csrftoken'
   let cookieValue: string | null = null
   if (document.cookie && document.cookie !== '') {
       const cookies = document.cookie.split(';')
       for (let i = 0; i < cookies.length; i++) {
           const cookie = cookies[i].trim()
           if (cookie.substring(0, name.length + 1) === (name + '=')) {
               cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
               break
           }
       }
   }
   if (cookieValue === null) {
       throw new Error('Missing CSRF cookie.')
   }
   return cookieValue
}