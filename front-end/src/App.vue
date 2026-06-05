<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { supabase } from './services/supabase' // Ajuste o caminho se necessário

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
    class="h-screen w-screen flex flex-col items-center justify-center bg-slate-900"
  >
    <div class="text-center">
      <h1 class="text-5xl font-black tracking-tight text-white mb-8">
        Conta<span class="text-indigo-400">Flow</span>.
      </h1>
      <!-- Spinner de Carregamento do Tailwind -->
      <div
        class="w-10 h-10 border-4 border-indigo-400 border-t-transparent rounded-full animate-spin mx-auto"
      ></div>
      <p class="text-slate-400 text-sm mt-4">Carregando sistema...</p>
    </div>
  </div>

  <!-- Aplicação Real (Quando estiver pronta) -->
  <div v-else>
    <RouterView />
  </div>
</template>
