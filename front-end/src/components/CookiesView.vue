<template>
  <div
    v-if="isVisible"
    class="fixed bottom-0 left-0 w-full bg-[#19341a] border-t border-white/10 shadow-2xl z-[100] p-5 sm:p-6"
  >
    <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-5">
      <div class="text-white/70 text-sm leading-relaxed flex items-start gap-3">
        <!-- Ícone de Cookie -->
        <svg class="w-6 h-6 text-[#ff8a65] flex-shrink-0 mt-0.5 hidden sm:block" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"></path></svg>
        <p>
          Nós utilizamos cookies e tecnologias semelhantes para garantir que você tenha a melhor
          experiência no <strong class="text-white">ContablyTask</strong>, além de analisar nosso tráfego para melhorias
          contínuas. Ao continuar navegando, você concorda com a nossa
          <a href="/privacidade" class="text-[#ff8a65] hover:text-[#f07047] underline font-semibold">Política de Privacidade</a>.
        </p>
      </div>

      <div class="flex shrink-0 gap-3 w-full sm:w-auto justify-end">
        <button
          @click="decline"
          class="flex-1 sm:flex-none px-5 py-2.5 text-sm font-semibold text-white/50 hover:text-white border border-white/10 rounded-xl hover:bg-white/5 transition-all"
        >
          Recusar Opcionais
        </button>
        <button
          @click="accept"
          class="flex-1 sm:flex-none px-6 py-2.5 text-sm font-semibold bg-[#ff8a65] text-white rounded-xl hover:bg-[#f07047] transition-all shadow-md shadow-[#ff8a65]/30"
        >
          Aceitar e Fechar
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const isVisible = ref(false)

onMounted(() => {
  // Quando a página carrega, procuramos se ele já tomou a decisão antes
  const consent = localStorage.getItem('cf_cookie_consent')

  // Se não tem registro, mostramos o banner
  if (!consent) {
    isVisible.value = true
  }
})

const accept = () => {
  // Salva a decisão no navegador do usuário
  localStorage.setItem('cf_cookie_consent', 'accepted')
  isVisible.value = false

  // No futuro, se você colocar o Google Analytics, o código de ativação iria aqui!
}

const decline = () => {
  // Salva a recusa. O sistema continua funcionando, mas sem rastreamento de marketing
  localStorage.setItem('cf_cookie_consent', 'declined')
  isVisible.value = false
}
</script>