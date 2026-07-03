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
const authStore = useAuthStore() // Instanciando a store

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
      // 2. Validação rigorosa de Autorização (Shift-Left Security)
      try {
        await api.get('/api/v1/admin/dashboard-stats')

        // 3. ATUALIZAÇÃO DO ESTADO GLOBAL (PINIA)
        // Avisa o Guardião de Rotas que você é o dono do SaaS
        authStore.setSuperAdmin(true)

        toast.success('Bem-vindo ao Backoffice, Admin.')

        // Agora o router.push vai funcionar perfeitamente
        router.push('/admin')
      } catch (authError: any) {
        // Se retornar 403 Forbidden, é um usuário comum tentando dar "bypass"
        await supabase.auth.signOut()

        // Pega a mensagem exata de erro do backend
        const detail =
          authError.response?.data?.detail ||
          'Acesso negado. Esta credencial não possui privilégios de Super Admin.'
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
    captchaToken.value = '' // Reseta o desafio do Captcha para o usuário tentar de novo
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div
    class="min-h-screen flex items-center justify-center bg-[#0a192f] py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden"
  >
    <!-- Efeitos visuais de fundo -->
    <div class="absolute inset-0 z-0">
      <div
        class="absolute top-1/4 left-1/4 w-96 h-96 bg-[#ff8a65] rounded-full filter blur-[128px] opacity-10"
      ></div>
      <div
        class="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#19341a] rounded-full filter blur-[128px] opacity-20"
      ></div>
    </div>

    <div
      class="max-w-md w-full space-y-8 bg-[#112240] p-10 rounded-2xl shadow-2xl border border-white/10 relative z-10"
    >
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-white tracking-tight">
          ContaFlow<span class="text-[#ff8a65]">Admin</span>
        </h2>
        <p class="mt-2 text-center text-sm text-gray-400 font-medium">
          Acesso restrito à engenharia e operações.
        </p>
      </div>

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

      <form class="mt-8 space-y-6" @submit.prevent="handleAdminLogin">
        <div class="space-y-4">
          <div>
            <label class="sr-only">E-mail Administrativo</label>
            <input
              v-model="email"
              type="email"
              required
              class="appearance-none rounded-xl relative block w-full px-4 py-3 border border-white/10 bg-[#0a192f] placeholder-gray-500 text-white focus:outline-none focus:ring-2 focus:ring-[#ff8a65] focus:border-transparent transition-all sm:text-sm"
              placeholder="E-mail Administrativo"
            />
          </div>
          <div>
            <label class="sr-only">Senha de Segurança</label>
            <input
              v-model="senha"
              type="password"
              required
              class="appearance-none rounded-xl relative block w-full px-4 py-3 border border-white/10 bg-[#0a192f] placeholder-gray-500 text-white focus:outline-none focus:ring-2 focus:ring-[#ff8a65] focus:border-transparent transition-all sm:text-sm"
              placeholder="Senha de Segurança"
            />
          </div>
        </div>

        <!-- Widget do Cloudflare Turnstile -->
        <div class="flex justify-center py-2">
          <VueTurnstile v-model="captchaToken" site-key="0x4AAAAAADe4izf5gmW3H2aL" theme="light" />
        </div>

        <div>
          <button
            type="submit"
            :disabled="isLoading || !captchaToken"
            class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-bold rounded-xl text-white bg-[#ff8a65] hover:bg-[#f07047] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[#0a192f] focus:ring-[#ff8a65] transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_20px_rgba(255,138,101,0.3)] hover:shadow-[0_0_25px_rgba(255,138,101,0.5)]"
          >
            {{ isLoading ? 'Verificando privilégios...' : 'Autorizar Acesso' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
