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

// Termos de uso
const acceptedTerms = ref(false)

// Variável do CAPTCHA
const captchaToken = ref('')

const handleRegister = async () => {
  if (!acceptedTerms.value) {
    erroMensagem.value =
      'Você precisa aceitar os Termos de Uso e a Política de Privacidade para criar uma conta.'
    return
  }
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
        captchaToken: captchaToken.value,
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
    <!-- Lado Esquerdo: Branding (Verde Escuro) -->
    <div
      class="hidden md:flex md:w-1/2 bg-[#19341a] text-white flex-col justify-center items-center p-12 relative overflow-hidden"
    >
      <!-- Efeito de luzes sutis -->
      <div class="absolute inset-0 opacity-10">
        <div
          class="absolute top-1/3 right-1/4 w-72 h-72 bg-[#ff8a65] rounded-full filter blur-3xl"
        ></div>
        <div
          class="absolute bottom-1/3 left-1/4 w-72 h-72 bg-[#2a4830] rounded-full filter blur-3xl"
        ></div>
      </div>

      <div class="relative z-10 text-center">
        <h1 class="text-5xl font-extrabold tracking-tight mb-4">
          Contably<span class="text-[#ff8a65]">Task</span>
        </h1>
        <p class="text-white/60 text-lg max-w-md mx-auto leading-relaxed">
          Comece agora a organizar seus prazos e tenha o controle total do seu escritório contábil.
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

        <h2 class="text-2xl font-bold text-[#19341a] mb-2">Crie sua conta</h2>
        <p class="text-[#2a2a2a]/60 mb-6">Preencha os dados abaixo para começar.</p>

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

        <form @submit.prevent="handleRegister" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-[#2a2a2a]/70 mb-1.5"
              >Seu Nome Completo</label
            >
            <input
              v-model="nomeCompleto"
              type="text"
              required
              placeholder="João da Silva"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-[#ff8a65] focus:border-transparent text-sm transition-colors bg-white"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-[#2a2a2a]/70 mb-1.5"
              >Nome do Escritório</label
            >
            <input
              v-model="nomeEscritorio"
              type="text"
              required
              placeholder="JS Contabilidade"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-[#ff8a65] focus:border-transparent text-sm transition-colors bg-white"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-[#2a2a2a]/70 mb-1.5"
              >E-mail Corporativo</label
            >
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
              placeholder="Mínimo 6 caracteres"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-[#ff8a65] focus:border-transparent text-sm transition-colors bg-white"
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

          <!-- Check dos termos de uso e política de privacidade -->
          <div class="flex items-start mb-6 mt-4">
            <div class="flex items-center h-5">
              <input
                id="termos"
                type="checkbox"
                v-model="acceptedTerms"
                class="w-4 h-4 text-[#ff8a65] bg-white border-gray-300 rounded focus:ring-[#ff8a65] focus:ring-2 cursor-pointer"
              />
            </div>
            <div class="ml-3 text-sm">
              <label for="termos" class="font-medium text-[#2a2a2a]/60 cursor-pointer">
                Eu li e concordo com os
                <a
                  href="/termos"
                  target="_blank"
                  class="text-[#ff8a65] hover:text-[#f07047] underline transition-colors"
                  >Termos de Uso</a
                >
                e a
                <a
                  href="/privacidade"
                  target="_blank"
                  class="text-[#ff8a65] hover:text-[#f07047] underline transition-colors"
                  >Política de Privacidade</a
                >.
              </label>
            </div>
          </div>

          <div class="pt-2">
            <button
              type="submit"
              :disabled="!acceptedTerms"
              class="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-md text-sm font-bold text-white bg-[#ff8a65] hover:bg-[#f07047] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#ff8a65] disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              Criar minha conta
            </button>
          </div>
        </form>

        <div class="mt-8 text-center text-sm text-[#2a2a2a]/50">
          Já tem uma conta?
          <RouterLink
            to="/login"
            class="font-bold text-[#19341a] hover:text-[#ff8a65] transition-colors"
          >
            Fazer Login
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>
