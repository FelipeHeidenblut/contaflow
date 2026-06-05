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
      class="hidden md:flex md:w-1/2 bg-slate-900 text-white flex-col justify-center items-center p-12 relative overflow-hidden"
    >
      <div class="absolute inset-0 opacity-10">
        <div
          class="absolute top-1/4 left-1/4 w-64 h-64 bg-indigo-500 rounded-full filter blur-3xl"
        ></div>
      </div>
      <div class="relative z-10 text-center">
        <h1 class="text-5xl font-black tracking-tight mb-4">
          Conta<span class="text-indigo-400">Flow</span>.
        </h1>
        <p class="text-slate-300 text-lg max-w-md mx-auto">
          Recupere o acesso à sua conta de forma segura.
        </p>
      </div>
    </div>

    <!-- Lado Direito (Formulário) -->
    <div class="w-full md:w-1/2 flex flex-col justify-center items-center p-8 bg-gray-50">
      <div class="w-full max-w-md">
        <div class="md:hidden text-center mb-8">
          <h1 class="text-4xl font-black tracking-tight text-gray-900">
            Conta<span class="text-indigo-600">Flow</span>.
          </h1>
        </div>

        <h2 class="text-2xl font-bold text-gray-900 mb-2">Esqueceu a senha?</h2>
        <p class="text-gray-500 mb-8">
          Informe seu e-mail e enviaremos um link para redefinir sua senha.
        </p>

        <!-- Mensagem de Sucesso -->
        <div
          v-if="emailEnviado"
          class="bg-green-50 border border-green-200 text-green-700 p-4 rounded-lg text-sm"
        >
          📧 E-mail enviado! Verifique sua caixa de entrada (e o spam) e clique no link para
          redefinir sua senha.
          <div class="mt-4">
            <RouterLink to="/login" class="font-semibold text-indigo-600 hover:text-indigo-500">
              Voltar para o Login
            </RouterLink>
          </div>
        </div>

        <!-- Formulário -->
        <form v-else @submit.prevent="handleResetPassword" class="space-y-5">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">E-mail cadastrado</label>
            <input
              v-model="email"
              type="email"
              required
              placeholder="seu@email.com"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
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
              class="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {{ isLoading ? 'Enviando...' : 'Enviar Link de Recuperação' }}
            </button>
          </div>
        </form>

        <div v-if="!emailEnviado" class="mt-6 text-center text-sm text-gray-500">
          Lembrou a senha?
          <RouterLink to="/login" class="font-semibold text-indigo-600 hover:text-indigo-500">
            Fazer Login
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>
