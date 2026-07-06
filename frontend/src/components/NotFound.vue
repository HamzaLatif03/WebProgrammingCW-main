<!-- NotFound.vue -->
<template>
    <div class="container mt-5 text-center">
      <h1 class="mb-4">404 - Page Not Found</h1>
      <p class="mb-4">The page you're looking for doesn't exist.</p>
      <p class="mb-4">Please check the URL and try again.</p>
      <router-link to="/" class="btn btn-primary">
        Return to Home
      </router-link>
    </div>
  </template>
  
  <script>
  export default {
    name: 'NotFound'
  }
  </script>