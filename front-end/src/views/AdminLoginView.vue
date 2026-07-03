<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { supabase } from '../services/supabase'
import { toast } from 'vue3-toastify'
import api from '../services/api'
import VueTurnstile from 'vue-turnstile'

// Importação do gerenciador de estado (Pinia)
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isLoading = ref(false)
const erroMensagem = ref('')

const email = ref('')
const senha = ref('')
const captchaToken = ref('')

const handleAdminLogin = async () => {
  if (!captchaToken.value) {
    erroMensagem.value = 'Verificação de segurança obrigatória.'
    return
  }

  erroMensagem.value = ''
  isLoading.value = true

  try {
    // 1. Autenticação primária no Supabase
    const { data, error } = await supabase.auth.signInWithPassword({
      email: email.value,
      password: senha.value,
      options: {
        captchaToken: captchaToken.value,
      },
    })

    if (error) throw error

    if (data?.session) {
      // 2. Validação rigorosa de Autorização
      try {
        await api.get('/api/v1/admin/dashboard-stats')

        // 3. ATUALIZAÇÃO DO ESTADO GLOBAL (PINIA)
        authStore.setSuperAdmin(true)

        toast.success('Bem-vindo ao Backoffice, Admin.')

        // Usa o router.push normal
        router.push('/admin')
      } catch (authError: any) {
        await supabase.auth.signOut()
        const detail = authError.response?.data?.detail || 'Acesso negado.'
        throw new Error(detail)
      }
    }
  } catch (error: any) {
    console.error('Erro no login admin:', error)
    if (error.message === 'Invalid login credentials') {
      erroMensagem.value = 'Credenciais administrativas inválidas.'
    } else {
      erroMensagem.value = error.message || 'Falha na autenticação de segurança.'
    }
    captchaToken.value = '' // Reseta o desafio do Captcha
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div
    class="min-h-screen flex items-center justify-center bg-[#19341a] py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden"
  >
    <!-- Efeitos visuais de fundo (Luzes e Grid) -->
    <div class="absolute inset-0 z-0">
      <div
        class="absolute top-1/4 left-1/4 w-96 h-96 bg-[#ff8a65] rounded-full filter blur-[128px] opacity-10"
      ></div>
      <div
        class="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#2a4830] rounded-full filter blur-[128px] opacity-30"
      ></div>
      <div
        class="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:32px_32px]"
      ></div>
    </div>

    <!-- Card de Login -->
    <div
      class="max-w-md w-full space-y-8 bg-white/5 backdrop-blur-xl p-10 rounded-2xl shadow-2xl border border-white/10 relative z-10"
    >
      <!-- Cabeçalho -->
      <div>
        <div class="flex justify-center mb-6">
          <div
            class="w-14 h-14 rounded-2xl bg-[#ff8a65] flex items-center justify-center shadow-lg shadow-[#ff8a65]/30"
          >
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
              ></path>
            </svg>
          </div>
        </div>
        <h2 class="text-center text-3xl font-extrabold text-white tracking-tight">
          ContaFlow<span class="text-[#ff8a65]">Admin</span>
        </h2>
        <p class="mt-2 text-center text-sm text-white/40 font-medium">
          Acesso restrito à engenharia e operações.
        </p>
      </div>

      <!-- Mensagem de Erro -->
      <div
        v-if="erroMensagem"
        class="bg-red-500/10 border border-red-500/30 text-red-400 p-4 rounded-xl text-sm font-medium flex items-center gap-3"
      >
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          ></path>
        </svg>
        {{ erroMensagem }}
      </div>

      <!-- Formulário -->
      <form class="mt-8 space-y-6" @submit.prevent="handleAdminLogin">
        <div class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-white/40 uppercase mb-1.5"
              >E-mail Administrativo</label
            >
            <input
              v-model="email"
              type="email"
              required
              class="appearance-none rounded-xl relative block w-full px-4 py-3 border border-white/10 bg-[#0f2010] placeholder-white/30 text-white focus:outline-none focus:ring-2 focus:ring-[#ff8a65] focus:border-transparent transition-all sm:text-sm"
              placeholder="admin@contaflow.com"
            />
          </div>
          <div>
            <label class="block text-xs font-bold text-white/40 uppercase mb-1.5"
              >Senha de Segurança</label
            >
            <input
              v-model="senha"
              type="password"
              required
              class="appearance-none rounded-xl relative block w-full px-4 py-3 border border-white/10 bg-[#0f2010] placeholder-white/30 text-white focus:outline-none focus:ring-2 focus:ring-[#ff8a65] focus:border-transparent transition-all sm:text-sm"
              placeholder="••••••••••••"
            />
          </div>
        </div>

        <!-- Widget do Cloudflare Turnstile -->
        <div class="flex justify-center py-2 rounded-xl overflow-hidden">
          <VueTurnstile v-model="captchaToken" site-key="0x4AAAAAADe4izf5gmW3H2aL" theme="light" />
        </div>

        <div>
          <button
            type="submit"
            :disabled="isLoading || !captchaToken"
            class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-bold rounded-xl text-white bg-[#ff8a65] hover:bg-[#f07047] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[#19341a] focus:ring-[#ff8a65] transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_20px_rgba(255,138,101,0.3)] hover:shadow-[0_0_25px_rgba(255,138,101,0.5)]"
          >
            {{ isLoading ? 'Verificando privilégios...' : 'Autorizar Acesso' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
