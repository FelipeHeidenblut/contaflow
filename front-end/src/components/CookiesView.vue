<template>
  <div
    v-if="isVisible"
    class="fixed bottom-0 left-0 w-full bg-gray-900 border-t border-gray-700 shadow-2xl z-[100] p-4 sm:p-6"
  >
    <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
      <div class="text-gray-300 text-sm leading-relaxed">
        <p>
          Nós utilizamos cookies e tecnologias semelhantes para garantir que você tenha a melhor
          experiência no <strong>ContaFlow</strong>, além de analisar nosso tráfego para melhorias
          contínuas. Ao continuar navegando, você concorda com a nossa
          <a href="/privacidade" class="text-indigo-400 hover:text-indigo-300 underline"
            >Política de Privacidade</a
          >.
        </p>
      </div>

      <div class="flex shrink-0 gap-3 w-full sm:w-auto justify-end">
        <button
          @click="decline"
          class="px-4 py-2 text-sm font-medium text-gray-400 hover:text-white transition-colors"
        >
          Recusar Opcionais
        </button>
        <button
          @click="accept"
          class="px-6 py-2 text-sm font-medium bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors shadow-sm"
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
