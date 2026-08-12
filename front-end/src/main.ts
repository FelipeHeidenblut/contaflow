import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import './assets/main.css'

import Vue3Toastify from 'vue3-toastify'
import 'vue3-toastify/dist/index.css'

const app = createApp(App)
const focusTrapCleanups = new WeakMap<HTMLElement, () => void>()

app.directive('focus-trap', {
  mounted(element: HTMLElement) {
    const previousFocus = document.activeElement as HTMLElement | null
    const selector =
      'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    const handler = (event: KeyboardEvent) => {
      const dialogs = Array.from(document.querySelectorAll<HTMLElement>('[role="dialog"]'))
      if (dialogs.at(-1) !== element) return
      const focusable = Array.from(element.querySelectorAll<HTMLElement>(selector))
      if (event.key === 'Escape') {
        element.querySelector<HTMLElement>('[aria-label^="Fechar"]')?.click()
        return
      }
      if (event.key !== 'Tab' || !focusable.length) return
      const first = focusable[0]
      const last = focusable[focusable.length - 1]
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault()
        last?.focus()
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault()
        first?.focus()
      }
    }
    focusTrapCleanups.set(element, () => {
      document.removeEventListener('keydown', handler)
      previousFocus?.focus()
    })
    document.addEventListener('keydown', handler)
    requestAnimationFrame(() =>
      (
        element.querySelector<HTMLElement>('[autofocus]') ||
        element.querySelector<HTMLElement>(selector) ||
        element
      ).focus(),
    )
  },
  beforeUnmount(element: HTMLElement) {
    focusTrapCleanups.get(element)?.()
    focusTrapCleanups.delete(element)
  },
})

app.use(createPinia())
app.use(router)

// Configuração global do Toastify
app.use(Vue3Toastify, {
  autoClose: 3000, // Os alertas somem em 3 segundos
  position: 'top-right', // Aparecem no canto superior direito
})

app.mount('#app')
