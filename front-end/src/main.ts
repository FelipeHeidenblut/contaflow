import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import './assets/main.css'

import Vue3Toastify from 'vue3-toastify'
import 'vue3-toastify/dist/index.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// Configuração global do Toastify
app.use(Vue3Toastify, {
  autoClose: 3000, // Os alertas somem em 3 segundos
  position: 'top-right', // Aparecem no canto superior direito
})

app.mount('#app')
