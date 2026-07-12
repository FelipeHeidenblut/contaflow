import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            // Separa o Supabase em um arquivo próprio
            if (id.includes('@supabase')) return 'supabase'
            // Separa o Vue/Pinia em outro
            if (id.includes('vue') || id.includes('pinia')) return 'vue-core'
            // O resto das bibliotecas
            return 'vendor'
          }
        }
      }
    }
  }
})
