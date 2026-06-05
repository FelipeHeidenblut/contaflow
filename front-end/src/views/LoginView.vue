<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { supabase } from '../services/supabase'
import { toast } from 'vue3-toastify'
import VueTurnstile from 'vue-turnstile'
import api from '../services/api' // Garanta que o api está importado!

const router = useRouter()
const isLoading = ref(false)
const erroMensagem = ref('')

const email = ref('')
const senha = ref('')

// Variável do CAPTCHA
const captchaToken = ref('')

const handleLogin = async () => {
  erroMensagem.value = ''
  isLoading.value = true

  try {
    const { data, error } = await supabase.auth.signInWithPassword({
      email: email.value,
      password: senha.value,
      options: {
        captchaToken: captchaToken.value,
      },
    })

    if (error) throw error

    if (data?.session) {
      // ==========================================
      // AUTO-CURA: Garante que o perfil existe no banco local
      // Se o banco caiu durante o cadastro, isso recria o perfil agora
      // ==========================================
      try {
        await api.post('/api/v1/auth/sincronizar-cadastro', {
          supabase_user_id: data.user.id,
          email: data.user.email,
          nome_completo: data.user.user_metadata?.full_name || data.user.email,
          nome_escritorio: data.user.user_metadata?.company_name || 'Meu Escritório',
        })
      } catch (syncError: any) {
        // Se der erro 400 (já existe), ignoramos. Se for 500, o banco está offline.
        console.warn(
          'Aviso na sincronização pós-login:',
          syncError.response?.data?.detail || syncError.message,
        )
      }

      // Só redireciona depois de tentar sincronizar
      router.push('/dashboard')
    }
  } catch (error: any) {
    console.error('Erro no login:', error)
    if (error.message === 'Invalid login credentials') {
      erroMensagem.value = 'E-mail ou senha incorretos.'
    } else if (error.message === 'Email not confirmed') {
      erroMensagem.value = 'Por favor, confirme seu e-mail antes de acessar.'
    } else {
      erroMensagem.value = error.message || 'Ocorreu um erro ao tentar fazer login.'
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex">
    <!-- Lado Esquerdo: Branding (Escuro) -->
    <div
      class="hidden md:flex md:w-1/2 bg-slate-900 text-white flex-col justify-center items-center p-12 relative overflow-hidden"
    >
      <div class="absolute inset-0 opacity-10">
        <div
          class="absolute top-1/4 left-1/4 w-64 h-64 bg-indigo-500 rounded-full filter blur-3xl"
        ></div>
        <div
          class="absolute bottom-1/4 right-1/4 w-64 h-64 bg-indigo-700 rounded-full filter blur-3xl"
        ></div>
      </div>

      <div class="relative z-10 text-center">
        <h1 class="text-5xl font-black tracking-tight mb-4">
          Conta<span class="text-indigo-400">Flow</span>.
        </h1>
        <p class="text-slate-300 text-lg max-w-md mx-auto">
          O painel de controle definitivo para organizar as obrigações e clientes do seu escritório
          contábil.
        </p>
      </div>
    </div>

    <!-- Lado Direito: Formulário (Claro) -->
    <div class="w-full md:w-1/2 flex flex-col justify-center items-center p-8 bg-gray-50">
      <div class="w-full max-w-md">
        <!-- Logo no Mobile -->
        <div class="md:hidden text-center mb-8">
          <h1 class="text-4xl font-black tracking-tight text-gray-900">
            Conta<span class="text-indigo-600">Flow</span>.
          </h1>
        </div>

        <h2 class="text-2xl font-bold text-gray-900 mb-2">Bem-vindo de volta</h2>
        <p class="text-gray-500 mb-8">Acesse sua conta para continuar.</p>

        <div
          v-if="erroMensagem"
          class="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg font-medium flex items-center gap-2"
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

        <form @submit.prevent="handleLogin" class="space-y-5">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">E-mail</label>
            <input
              v-model="email"
              type="email"
              required
              placeholder="seu@email.com"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm transition-colors"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Senha</label>
            <input
              v-model="senha"
              type="password"
              required
              placeholder="••••••••"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm transition-colors"
            />
          </div>

          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <input
                id="remember-me"
                type="checkbox"
                class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
              <label for="remember-me" class="ml-2 block text-xs text-gray-600"
                >Lembrar de mim</label
              >
            </div>
            <div class="text-xs">
              <RouterLink
                to="/esqueceu-senha"
                class="font-medium text-indigo-600 hover:text-indigo-500"
                >Esqueceu a senha?</RouterLink
              >
            </div>
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
              class="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 transition-colors"
            >
              {{ isLoading ? 'Autenticando...' : 'Entrar no Sistema' }}
            </button>
          </div>
        </form>

        <div class="mt-8 text-center text-sm text-gray-500">
          Ainda não tem uma conta?
          <RouterLink to="/cadastro" class="font-semibold text-indigo-600 hover:text-indigo-500">
            Criar escritório
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>
