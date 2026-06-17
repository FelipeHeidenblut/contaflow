<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { supabase } from '../services/supabase'
import { toast } from 'vue3-toastify'
import VueTurnstile from 'vue-turnstile' // Importação do Captcha

const email = ref('')
const isLoading = ref(false)
const emailEnviado = ref(false)

// Variável do CAPTCHA
const captchaToken = ref('')

const handleResetPassword = async () => {
  isLoading.value = true
  try {
    const { error } = await supabase.auth.resetPasswordForEmail(email.value, {
      redirectTo: `${window.location.origin}/redefinir-senha`,
      captchaToken: captchaToken.value, // <--- TOKEN DO CAPTCHA AQUI
    })

    if (error) throw error

    emailEnviado.value = true
    toast.success('Link de recuperação enviado!')
  } catch (error: any) {
    toast.error(error.message || 'Erro ao enviar o e-mail.')
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex">
    <!-- Lado Esquerdo (Escuro) -->
    <div
      class="hidden md:flex md:w-1/2 bg-[#19341a] text-white flex-col justify-center items-center p-12 relative overflow-hidden"
    >
      <!-- Efeito de luz moderna -->
      <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-[#ff8a65]/20 rounded-full filter blur-[120px]"></div>
      
      <div class="relative z-10 text-center">
        <h1 class="text-5xl font-extrabold tracking-tight mb-4">
          Contably<span class="text-[#ff8a65]">Task</span>.
        </h1>
        <p class="text-white/60 text-lg max-w-md mx-auto leading-relaxed">
          Recupere o acesso à sua conta de forma segura e retome o controle do seu escritório.
        </p>
      </div>
    </div>

    <!-- Lado Direito (Formulário) -->
    <div class="w-full md:w-1/2 flex flex-col justify-center items-center p-8 bg-[#f8f8f8]">
      <div class="w-full max-w-md">
        <!-- Logo para Mobile -->
        <div class="md:hidden text-center mb-8">
          <h1 class="text-4xl font-extrabold tracking-tight text-[#19341a]">
            Contably<span class="text-[#ff8a65]">Task</span>.
          </h1>
        </div>

        <h2 class="text-2xl font-extrabold text-[#19341a] mb-2 tracking-tight">Esqueceu a senha?</h2>
        <p class="text-gray-500 mb-8 text-[0.95rem]">
          Informe seu e-mail cadastrado e enviaremos um link seguro para redefinir sua senha.
        </p>

        <!-- Mensagem de Sucesso -->
        <div
          v-if="emailEnviado"
          class="bg-[#eaf3ea] border border-[#19341a]/10 text-[#19341a] p-5 rounded-xl text-sm shadow-sm"
        >
          <div class="flex items-start gap-3">
            <svg class="w-6 h-6 flex-shrink-0 text-[#19341a]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <div>
              <strong class="font-bold">E-mail enviado!</strong><br>
              Verifique sua caixa de entrada (e a pasta de spam) e clique no link para redefinir sua senha.
            </div>
          </div>
          <div class="mt-5 pt-4 border-t border-[#19341a]/10">
            <RouterLink to="/login" class="font-bold text-[#ff8a65] hover:text-[#f07047] transition-colors">
              ← Voltar para o Login
            </RouterLink>
          </div>
        </div>

        <!-- Formulário -->
        <form v-else @submit.prevent="handleResetPassword" class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-[#2a2a2a]/70 mb-1.5">E-mail cadastrado</label>
            <input
              v-model="email"
              type="email"
              required
              placeholder="seu@email.com"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-[#ff8a65] focus:border-transparent text-sm transition-all"
            />
          </div>

          <!-- Widget do CAPTCHA Cloudflare Turnstile -->
          <div class="flex justify-center py-2">
            <VueTurnstile
              v-model="captchaToken"
              site-key="0x4AAAAAADe4izf5gmW3H2aL"
              theme="light"
            />
          </div>

          <div>
            <button
              type="submit"
              :disabled="isLoading"
              class="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-md shadow-[#ff8a65]/30 text-sm font-semibold text-white bg-[#ff8a65] hover:bg-[#f07047] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#ff8a65] disabled:opacity-50 transition-all"
            >
              {{ isLoading ? 'Enviando...' : 'Enviar Link de Recuperação' }}
            </button>
          </div>
        </form>

        <div v-if="!emailEnviado" class="mt-8 text-center text-sm text-gray-500">
          Lembrou a senha?
          <RouterLink to="/login" class="font-bold text-[#19341a] hover:text-[#ff8a65] transition-colors">
            Fazer Login
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>