<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { supabase } from './services/supabase' // Ajuste o caminho se necessário
import CookiesView from './components/CookiesView.vue'

// Estado de carregamento global
const isAppReady = ref(false)

onMounted(async () => {
  // 1. Forçamos o Supabase a checar a sessão atual antes de qualquer coisa.
  // Isso garante que o Vue só vai renderizar as telas quando já souber se o usuário está logado.
  await supabase.auth.getSession()

  // 2. Libera o app para ser exibido
  isAppReady.value = true
})
</script>

<template>
  <!-- Tela de Splash (Enquanto o Supabase carrega) -->
  <div
    v-if="!isAppReady"
    class="h-screen w-screen flex flex-col items-center justify-center bg-[#19341a] relative overflow-hidden"
  >
    <!-- Efeito de luz de fundo (igual as outras telas) -->
    <div class="absolute top-1/3 left-1/2 -translate-x-1/2 w-96 h-96 bg-[#ff8a65]/20 rounded-full filter blur-[120px] z-0"></div>
    
    <div class="text-center relative z-10">
      <h1 class="text-5xl font-extrabold tracking-tight text-white mb-8">
        Conta<span class="text-[#ff8a65]">Flow</span>.
      </h1>
      <!-- Spinner de Carregamento com as cores da marca -->
      <div
        class="w-10 h-10 border-4 border-[#ff8a65]/30 border-t-[#ff8a65] rounded-full animate-spin mx-auto"
      ></div>
      <p class="text-white/50 text-sm mt-4 font-medium">Carregando sistema...</p>
    </div>
  </div>

  <!-- Aplicação Real (Quando estiver pronta) -->
  <div v-else>
    <RouterView />
    <CookiesView />
  </div>
</template>