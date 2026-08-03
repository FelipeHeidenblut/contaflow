<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, RouterLink, useRoute } from 'vue-router'
import { supabase } from '../services/supabase'
import api from '../services/api'
import { toast } from 'vue3-toastify'
import VueTurnstile from 'vue-turnstile'

const router = useRouter()
const route = useRoute()

const isLoading = ref(false)
const erroMensagem = ref('')

const nomeCompleto = ref('')
const email = ref(route.query.email ? String(route.query.email) : '')
const senha = ref('')
const nomeEscritorio = ref('')
const documentoRaw = ref('')

const acceptedTerms = ref(false)
const captchaToken = ref('')

const turnstileSiteKey = import.meta.env.VITE_TURNSTILE_SITE_KEY || ''

const documentoFormatado = computed({
  get() {
    let v = documentoRaw.value.replace(/\D/g, '')
    if (v.length <= 11) {
      v = v.replace(/(\d{3})(\d)/, '$1.$2')
      v = v.replace(/(\d{3})(\d)/, '$1.$2')
      v = v.replace(/(\d{3})(\d{1,2})$/, '$1-$2')
    } else {
      v = v.replace(/^(\d{2})(\d)/, '$1.$2')
      v = v.replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3')
      v = v.replace(/\.(\d{3})(\d)/, '.$1/$2')
      v = v.replace(/(\d{4})(\d)/, '$1-$2')
    }
    return v
  },
  set(novoValor) {
    documentoRaw.value = novoValor.replace(/\D/g, '').slice(0, 14)
  },
})

const handleRegister = async () => {
  if (!acceptedTerms.value) {
    erroMensagem.value =
      'Você precisa aceitar os Termos de Uso e a Política de Privacidade para criar uma conta.'
    return
  }

  if (!captchaToken.value) {
    erroMensagem.value = 'Por favor, aguarde a verificação de segurança.'
    return
  }

  if (documentoRaw.value.length !== 11 && documentoRaw.value.length !== 14) {
    erroMensagem.value = 'O documento deve ser um CPF (11 dígitos) ou CNPJ (14 dígitos) válido.'
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
          documento: documentoRaw.value,
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
  <div class="min-h-screen bg-[var(--ct-bg)] text-[var(--ct-ink)]">
    <div class="flex min-h-screen">
      <!-- Branding -->
      <div
        class="relative hidden overflow-hidden md:flex md:w-1/2 flex-col justify-center items-center p-12 text-white bg-[var(--ct-navy)]"
      >
        <div
          class="absolute inset-0 bg-[linear-gradient(to_right,#ffffff08_1px,transparent_1px),linear-gradient(to_bottom,#ffffff08_1px,transparent_1px)] bg-[size:32px_32px] opacity-30"
        ></div>

        <div
          class="absolute top-1/3 right-1/4 h-72 w-72 rounded-full bg-[var(--ct-primary)]/25 blur-3xl"
        ></div>

        <div
          class="absolute bottom-1/3 left-1/4 h-72 w-72 rounded-full bg-[#1E3A8A]/20 blur-3xl"
        ></div>

        <div
          class="absolute inset-0"
          style="background: radial-gradient(120% 90% at 50% 30%, transparent 35%, rgba(15, 23, 42, .72) 100%)"
        ></div>

        <div class="relative z-10 text-center">
          <div class="mb-6 flex items-center justify-center gap-3">
            <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/10 backdrop-blur-sm">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="#93C5FD"
                stroke-width="2.4"
                class="h-6 w-6"
              >
                <path d="M9 11l3 3L22 4" />
                <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" />
              </svg>
            </div>
            <h1 class="text-4xl font-extrabold tracking-tight">
              Contably<span class="text-[#93C5FD]">Task</span>
            </h1>
          </div>

          <p class="mx-auto max-w-md text-lg leading-relaxed text-white/70">
            Comece agora a organizar tarefas, prazos e documentos da sua rotina contábil com mais controle.
          </p>

          <div class="mt-10 grid gap-3 text-left max-w-md">
            <div class="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur-sm">
              <div class="text-sm font-semibold text-white">Operação mais organizada</div>
              <p class="mt-1 text-sm leading-relaxed text-white/65">
                Centralize clientes, demandas e responsáveis em um só lugar.
              </p>
            </div>

            <div class="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur-sm">
              <div class="text-sm font-semibold text-white">Mais previsibilidade</div>
              <p class="mt-1 text-sm leading-relaxed text-white/65">
                Tenha uma visão mais clara do que precisa ser feito e do que está pendente.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Formulário -->
      <div class="flex w-full items-center justify-center bg-[var(--ct-bg)] px-6 py-10 md:w-1/2">
        <div class="w-full max-w-md">
          <!-- Logo mobile -->
          <div class="mb-8 text-center md:hidden">
            <div class="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-[var(--ct-primary-soft)]">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="var(--ct-primary)"
                stroke-width="2.4"
                class="h-6 w-6"
              >
                <path d="M9 11l3 3L22 4" />
                <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" />
              </svg>
            </div>

            <h1 class="text-4xl font-extrabold tracking-tight text-[var(--ct-ink)]">
              Contably<span class="text-[var(--ct-primary)]">Task</span>
            </h1>
          </div>

          <div class="rounded-3xl border border-[var(--ct-border)] bg-white p-8 shadow-[0_20px_60px_rgba(15,23,42,0.08)]">
            <div class="mb-6">
              <h2 class="mb-2 text-2xl font-bold text-[var(--ct-ink)]">Crie sua conta</h2>
              <p class="text-sm text-[var(--ct-text-muted)]">
                Preencha os dados abaixo para começar a usar a ContablyTask.
              </p>
            </div>

            <div
              v-if="erroMensagem"
              class="mb-6 flex items-start gap-2 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm font-medium text-red-700"
            >
              <svg class="mt-0.5 h-5 w-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
              <span>{{ erroMensagem }}</span>
            </div>

            <form @submit.prevent="handleRegister" class="space-y-4">
              <div>
                <label class="mb-1.5 block text-sm font-medium text-[var(--ct-ink)]/80">
                  Seu nome completo
                </label>
                <input
                  v-model="nomeCompleto"
                  type="text"
                  required
                  placeholder="João da Silva"
                  class="w-full rounded-2xl border border-[var(--ct-border)] bg-white px-4 py-3 text-sm text-[var(--ct-ink)] shadow-sm transition-colors placeholder:text-slate-400 focus:border-[var(--ct-primary)] focus:outline-none focus:ring-4 focus:ring-[var(--ct-primary)]/10"
                />
              </div>

              <div>
                <label class="mb-1.5 block text-sm font-medium text-[var(--ct-ink)]/80">
                  Nome do escritório
                </label>
                <input
                  v-model="nomeEscritorio"
                  type="text"
                  required
                  placeholder="JS Contabilidade"
                  class="w-full rounded-2xl border border-[var(--ct-border)] bg-white px-4 py-3 text-sm text-[var(--ct-ink)] shadow-sm transition-colors placeholder:text-slate-400 focus:border-[var(--ct-primary)] focus:outline-none focus:ring-4 focus:ring-[var(--ct-primary)]/10"
                />
              </div>

              <div>
                <label class="mb-1.5 block text-sm font-medium text-[var(--ct-ink)]/80">
                  CPF ou CNPJ
                </label>
                <input
                  v-model="documentoFormatado"
                  type="text"
                  required
                  placeholder="000.000.000-00 ou 00.000.000/0001-00"
                  class="w-full rounded-2xl border border-[var(--ct-border)] bg-white px-4 py-3 text-sm text-[var(--ct-ink)] shadow-sm transition-colors placeholder:text-slate-400 focus:border-[var(--ct-primary)] focus:outline-none focus:ring-4 focus:ring-[var(--ct-primary)]/10"
                />
                <p class="mt-1 text-xs text-slate-400">
                  Usado para emissão fiscal da sua assinatura.
                </p>
              </div>

              <div>
                <label class="mb-1.5 block text-sm font-medium text-[var(--ct-ink)]/80">
                  E-mail corporativo
                </label>
                <input
                  v-model="email"
                  type="email"
                  required
                  placeholder="seu@email.com"
                  class="w-full rounded-2xl border border-[var(--ct-border)] bg-white px-4 py-3 text-sm text-[var(--ct-ink)] shadow-sm transition-colors placeholder:text-slate-400 focus:border-[var(--ct-primary)] focus:outline-none focus:ring-4 focus:ring-[var(--ct-primary)]/10"
                />
              </div>

              <div>
                <label class="mb-1.5 block text-sm font-medium text-[var(--ct-ink)]/80">
                  Senha
                </label>
                <input
                  v-model="senha"
                  type="password"
                  required
                  placeholder="Mínimo 6 caracteres"
                  class="w-full rounded-2xl border border-[var(--ct-border)] bg-white px-4 py-3 text-sm text-[var(--ct-ink)] shadow-sm transition-colors placeholder:text-slate-400 focus:border-[var(--ct-primary)] focus:outline-none focus:ring-4 focus:ring-[var(--ct-primary)]/10"
                />
              </div>

              <div class="flex justify-center py-2">
                <VueTurnstile
                  v-model="captchaToken"
                  :site-key="turnstileSiteKey || '0x4AAAAAADe4izf5gmW3H2aL'"
                  theme="light"
                />
              </div>

              <div class="mt-4 mb-6 flex items-start">
                <div class="flex h-5 items-center">
                  <input
                    id="termos"
                    v-model="acceptedTerms"
                    type="checkbox"
                    class="h-4 w-4 cursor-pointer rounded border-slate-300 bg-white text-[var(--ct-primary)] focus:ring-2 focus:ring-[var(--ct-primary)]"
                  />
                </div>

                <div class="ml-3 text-sm">
                  <label for="termos" class="cursor-pointer font-medium text-[var(--ct-text-muted)]">
                    Eu li e concordo com os
                    <a
                      href="/termos"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="text-[var(--ct-primary)] underline transition-colors hover:text-[var(--ct-primary-hover)]"
                    >
                      Termos de Uso
                    </a>
                    e a
                    <a
                      href="/privacidade"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="text-[var(--ct-primary)] underline transition-colors hover:text-[var(--ct-primary-hover)]"
                    >
                      Política de Privacidade
                    </a>.
                  </label>
                </div>
              </div>

              <div class="pt-2">
                <button
                  type="submit"
                  :disabled="!acceptedTerms || isLoading || !captchaToken"
                  class="flex w-full justify-center rounded-2xl border border-transparent bg-[var(--ct-primary)] px-4 py-3 text-sm font-bold text-white shadow-md transition-all hover:bg-[var(--ct-primary-hover)] focus:outline-none focus:ring-2 focus:ring-[var(--ct-primary)] focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <span v-if="isLoading">Criando conta...</span>
                  <span v-else>Criar minha conta</span>
                </button>
              </div>
            </form>

            <div class="mt-8 text-center text-sm text-[var(--ct-text-muted)]">
              Já tem uma conta?
              <RouterLink
                to="/login"
                class="font-bold text-[var(--ct-ink)] transition-colors hover:text-[var(--ct-primary)]"
              >
                Fazer login
              </RouterLink>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
:global(:root) {
  --ct-bg: #F8FAFC;
  --ct-surface: #FFFFFF;
  --ct-muted: #F1F5F9;
  --ct-border: #E2E8F0;

  --ct-ink: #0F172A;
  --ct-text-muted: #64748B;

  --ct-primary: #2563EB;
  --ct-primary-hover: #1D4ED8;
  --ct-primary-soft: #DBEAFE;
  --ct-navy: #172554;
}
</style>