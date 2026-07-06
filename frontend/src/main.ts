import { createApp } from 'vue'
import { createPinia } from 'pinia';
import App from './App.vue'
import router from './router'
import {useAuthStore} from './store/auth.ts'

import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap';

const app = createApp(App)

app.use(createPinia())
app.use(router)

const auth_store = useAuthStore()
auth_store.setCsrfToken()

app.mount('#app')
