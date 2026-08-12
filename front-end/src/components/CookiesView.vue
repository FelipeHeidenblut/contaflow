<template>
  <div
    v-if="isVisible"
    role="dialog"
    aria-label="Preferências de cookies"
    class="fixed bottom-0 left-0 z-[100] w-full border-t border-white/15 bg-[var(--ct-navy)] p-4 sm:p-5"
  >
    <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-5">
      <div class="text-white/70 text-sm leading-relaxed flex items-start gap-3">
        <!-- Ícone de Cookie -->
        <svg
          class="mt-0.5 hidden h-6 w-6 flex-shrink-0 text-[var(--ct-accent)] sm:block"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"
          ></path>
        </svg>
        <p>
          Usamos cookies essenciais para o funcionamento da plataforma e opcionais para entender o
          uso do <strong class="text-white">ContablyTask</strong>. Consulte nossa
          <a
            href="/privacidade"
            class="font-semibold text-[var(--ct-accent)] underline hover:text-white"
            >Política de Privacidade</a
          >.
        </p>
      </div>

      <div class="flex shrink-0 gap-3 w-full sm:w-auto justify-end">
        <button
          @click="decline"
          class="flex-1 rounded-lg border border-white/15 px-5 py-2.5 text-sm font-semibold text-white/60 transition-colors hover:bg-white/5 hover:text-white sm:flex-none"
        >
          Somente essenciais
        </button>
        <button
          @click="accept"
          class="flex-1 rounded-lg bg-[var(--ct-primary)] px-6 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[var(--ct-primary-hover)] sm:flex-none"
        >
          Aceitar opcionais
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { loadGoogleAnalytics } from '../services/analytics'

const isVisible = ref(false)
const enableAnalytics = () => {
  void loadGoogleAnalytics().catch(() => {
    // O rastreamento é opcional e nunca deve interferir na navegação do usuário.
  })
}

onMounted(() => {
  // Quando a página carrega, procuramos se ele já tomou a decisão antes
  const consent = localStorage.getItem('cf_cookie_consent')

  // Se não tem registro, mostramos o banner
  if (!consent) {
    isVisible.value = true
  } else if (consent === 'accepted') {
    enableAnalytics()
  }
})

const accept = () => {
  // Salva a decisão no navegador do usuário
  localStorage.setItem('cf_cookie_consent', 'accepted')
  isVisible.value = false
  enableAnalytics()
}

const decline = () => {
  // Salva a recusa. O sistema continua funcionando, mas sem rastreamento de marketing
  localStorage.setItem('cf_cookie_consent', 'declined')
  isVisible.value = false
}
</script>
