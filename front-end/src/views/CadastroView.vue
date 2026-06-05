<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { supabase } from '../services/supabase'
import api from '../services/api'
import { toast } from 'vue3-toastify'
import VueTurnstile from 'vue-turnstile' // Importação do Captcha

const router = useRouter()
const isLoading = ref(false)
const erroMensagem = ref('')

const nomeCompleto = ref('')
const email = ref('')
const senha = ref('')
const nomeEscritorio = ref('')

// Variável do CAPTCHA
const captchaToken = ref('')

const handleRegister = async () => {
  erroMensagem.value = ''
  isLoading.value = true

  try {
    const { data, error } = await supabase.auth.signUp({
      email: email.value,
      password: senha.value,
      options: {
        data: {
          full_name: nomeCompleto.value,
        },
        captchaToken: captchaToken.value, // Token do Captcha aqui
      },
    })

    if (error) throw error

    if (data.user) {
      try {
        await api.post('/api/v1/auth/sincronizar-cadastro', {
          supabase_user_id: data.user.id,
          email: email.value,
          nome_completo: nomeCompleto.value,
          nome_escritorio: nomeEscritorio.value,
        })

        if (data.session) {
          router.push('/dashboard')
        } else {
          toast.success('Conta criada! Verifique seu e-mail para confirmar antes de logar.')
          router.push('/login')
        }
      } catch (syncError) {
        console.error('Erro na sincronização:', syncError)
        erroMensagem.value =
          'Conta criada no Supabase, mas falhou ao sincronizar. Tente fazer login.'
      }
    }
  } catch (error: any) {
    console.error('Erro no cadastro:', error)
    if (error.message === 'User already registered') {
      erroMensagem.value = 'Este e-mail já está cadastrado.'
    } else {
      erroMensagem.value = error.message || 'Ocorreu um erro ao criar a conta.'
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
          class="absolute top-1/3 right-1/4 w-72 h-72 bg-indigo-500 rounded-full filter blur-3xl"
        ></div>
        <div
          class="absolute bottom-1/3 left-1/4 w-72 h-72 bg-indigo-700 rounded-full filter blur-3xl"
        ></div>
      </div>

      <div class="relative z-10 text-center">
        <h1 class="text-5xl font-black tracking-tight mb-4">
          Conta<span class="text-indigo-400">Flow</span>.
        </h1>
        <p class="text-slate-300 text-lg max-w-md mx-auto">
          Comece agora a organizar seus prazos e tenha o controle total do seu escritório.
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

        <h2 class="text-2xl font-bold text-gray-900 mb-2">Crie sua conta</h2>
        <p class="text-gray-500 mb-6">Preencha os dados abaixo para começar.</p>

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

        <form @submit.prevent="handleRegister" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Seu Nome Completo</label>
            <input
              v-model="nomeCompleto"
              type="text"
              required
              placeholder="João da Silva"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm transition-colors"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nome do Escritório</label>
            <input
              v-model="nomeEscritorio"
              type="text"
              required
              placeholder="JS Contabilidade"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm transition-colors"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">E-mail Corporativo</label>
            <input
              v-model="email"
              type="email"
              required
              placeholder="seu@email.com"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm transition-colors"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Senha</label>
            <input
              v-model="senha"
              type="password"
              required
              placeholder="Mínimo 6 caracteres"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm transition-colors"
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

          <div class="pt-2">
            <button
              type="submit"
              :disabled="isLoading"
              class="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 transition-colors"
            >
              {{ isLoading ? 'Criando Conta...' : 'Criar Minha Conta' }}
            </button>
          </div>
        </form>

        <div class="mt-6 text-center text-sm text-gray-500">
          Já tem uma conta?
          <RouterLink to="/login" class="font-semibold text-indigo-600 hover:text-indigo-500">
            Fazer Login
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>
