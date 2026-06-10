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
    <!-- Lado Esquerdo: Branding (Verde Escuro) -->
    <div
      class="hidden md:flex md:w-1/2 bg-[#19341a] text-white flex-col justify-center items-center p-12 relative overflow-hidden"
    >
      <!-- Efeito de luzes sutis -->
      <div class="absolute inset-0 opacity-10">
        <div
          class="absolute top-1/4 left-1/4 w-64 h-64 bg-[#ff8a65] rounded-full filter blur-3xl"
        ></div>
        <div
          class="absolute bottom-1/4 right-1/4 w-64 h-64 bg-[#2a4830] rounded-full filter blur-3xl"
        ></div>
      </div>

      <div class="relative z-10 text-center">
        <h1 class="text-5xl font-extrabold tracking-tight mb-4">
          Contably<span class="text-[#ff8a65]">Task</span>
        </h1>
        <p class="text-white/60 text-lg max-w-md mx-auto leading-relaxed">
          O painel de controle definitivo para organizar as obrigações e clientes do seu escritório
          contábil.
        </p>
      </div>
    </div>

    <!-- Lado Direito: Formulário (Fundo Claro) -->
    <div class="w-full md:w-1/2 flex flex-col justify-center items-center p-8 bg-[#f8f8f8]">
      <div class="w-full max-w-md">
        <!-- Logo no Mobile -->
        <div class="md:hidden text-center mb-8">
          <h1 class="text-4xl font-extrabold tracking-tight text-[#19341a]">
            Contably<span class="text-[#ff8a65]">Task</span>
          </h1>
        </div>

        <h2 class="text-2xl font-bold text-[#19341a] mb-2">Bem-vindo de volta</h2>
        <p class="text-[#2a2a2a]/60 mb-8">Acesse sua conta para continuar.</p>

        <div
          v-if="erroMensagem"
          class="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl font-medium flex items-center gap-2"
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
            <label class="block text-sm font-medium text-[#2a2a2a]/70 mb-1.5">E-mail</label>
            <input
              v-model="email"
              type="email"
              required
              placeholder="seu@email.com"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-[#ff8a65] focus:border-transparent text-sm transition-colors bg-white"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-[#2a2a2a]/70 mb-1.5">Senha</label>
            <input
              v-model="senha"
              type="password"
              required
              placeholder="••••••••"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-[#ff8a65] focus:border-transparent text-sm transition-colors bg-white"
            />
          </div>

          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <input
                id="remember-me"
                type="checkbox"
                class="h-4 w-4 text-[#ff8a65] focus:ring-[#ff8a65] border-gray-300 rounded cursor-pointer"
              />
              <label for="remember-me" class="ml-2 block text-xs text-[#2a2a2a]/60 cursor-pointer"
                >Lembrar de mim</label
              >
            </div>
            <div class="text-xs">
              <RouterLink
                to="/esqueceu-senha"
                class="font-semibold text-[#ff8a65] hover:text-[#f07047] transition-colors"
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
              class="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-md text-sm font-bold text-white bg-[#ff8a65] hover:bg-[#f07047] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#ff8a65] disabled:opacity-50 transition-all"
            >
              {{ isLoading ? 'Autenticando...' : 'Entrar no Sistema' }}
            </button>
          </div>
        </form>

        <div class="mt-8 text-center text-sm text-[#2a2a2a]/50">
          Ainda não tem uma conta?
          <RouterLink
            to="/cadastro"
            class="font-bold text-[#19341a] hover:text-[#ff8a65] transition-colors"
          >
            Criar escritório
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>
