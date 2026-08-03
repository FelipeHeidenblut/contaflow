<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { supabase } from '../services/supabase'
import api from '../services/api'
import VueTurnstile from 'vue-turnstile'

const router = useRouter()
const isLoading = ref(false)
const erroMensagem = ref('')

const email = ref('')
const senha = ref('')

const captchaToken = ref('')

const turnstileSiteKey = import.meta.env.VITE_TURNSTILE_SITE_KEY || ''

const handleLogin = async () => {
  if (!captchaToken.value) {
    erroMensagem.value = 'Por favor, aguarde a verificação de segurança.'
    return
  }

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
      try {
        await api.post('/api/v1/auth/sincronizar-cadastro', {
          supabase_user_id: data.user.id,
          email: data.user.email,
          nome_completo: data.user.user_metadata?.full_name || data.user.email,
          nome_escritorio: data.user.user_metadata?.company_name || 'Meu Escritório',
          documento: '00000000000',
        })
      } catch (syncError: any) {
        console.warn(
          'Aviso na sincronização pós-login:',
          syncError.response?.data?.detail || syncError.message,
        )
      }

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

    captchaToken.value = ''
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
          class="absolute top-1/4 left-1/4 h-64 w-64 rounded-full bg-[var(--ct-primary)]/25 blur-3xl"
        ></div>

        <div
          class="absolute bottom-1/4 right-1/4 h-64 w-64 rounded-full bg-[#1E3A8A]/20 blur-3xl"
        ></div>

        <div
          class="absolute inset-0"
          style="background: radial-gradient(120% 90% at 50% 30%, transparent 35%, rgba(15, 23, 42, .72) 100%)"
        ></div>

        <div class="relative z-10 text-center">
          <div class="mb-6 flex items-center justify-center gap-3">
            
            <h1 class="text-4xl font-extrabold tracking-tight">
              Contably<span class="text-[#93C5FD]">Task</span>
            </h1>
          </div>

          <p class="mx-auto max-w-md text-lg leading-relaxed text-white/70">
            Organize tarefas, prazos e clientes da rotina contábil com mais clareza, controle e agilidade.
          </p>

          <div class="mt-10 grid gap-3 text-left max-w-md">
            <div class="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur-sm">
              <div class="text-sm font-semibold text-white">Mais visibilidade</div>
              <p class="mt-1 text-sm leading-relaxed text-white/65">
                Visualize o que está pendente, em andamento e o que precisa de atenção.
              </p>
            </div>

            <div class="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur-sm">
              <div class="text-sm font-semibold text-white">Mais organização</div>
              <p class="mt-1 text-sm leading-relaxed text-white/65">
                Centralize tarefas, documentos e responsáveis em um só lugar.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Form -->
      <div class="flex w-full items-center justify-center bg-[var(--ct-bg)] px-6 py-10 md:w-1/2">
        <div class="w-full max-w-md">
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
            <div class="mb-8">
              <h2 class="mb-2 text-2xl font-bold text-[var(--ct-ink)]">Bem-vindo de volta</h2>
              <p class="text-sm text-[var(--ct-text-muted)]">
                Acesse sua conta para continuar no painel da ContablyTask.
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

            <form @submit.prevent="handleLogin" class="space-y-5">
              <div>
                <label class="mb-1.5 block text-sm font-medium text-[var(--ct-ink)]/80">
                  E-mail
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
                  placeholder="••••••••"
                  class="w-full rounded-2xl border border-[var(--ct-border)] bg-white px-4 py-3 text-sm text-[var(--ct-ink)] shadow-sm transition-colors placeholder:text-slate-400 focus:border-[var(--ct-primary)] focus:outline-none focus:ring-4 focus:ring-[var(--ct-primary)]/10"
                />
              </div>

              <div class="flex items-center justify-between">
                <div class="flex items-center">
                  <input
                    id="remember-me"
                    type="checkbox"
                    class="h-4 w-4 cursor-pointer rounded border-slate-300 text-[var(--ct-primary)] focus:ring-[var(--ct-primary)]"
                  />
                  <label
                    for="remember-me"
                    class="ml-2 block cursor-pointer text-xs text-[var(--ct-text-muted)]"
                  >
                    Lembrar de mim
                  </label>
                </div>

                <div class="text-xs">
                  <RouterLink
                    to="/esqueceu-senha"
                    class="font-semibold text-[var(--ct-primary)] transition-colors hover:text-[var(--ct-primary-hover)]"
                  >
                    Esqueceu a senha?
                  </RouterLink>
                </div>
              </div>

              <div class="flex justify-center py-2">
                <VueTurnstile
                  v-model="captchaToken"
                  :site-key="turnstileSiteKey || '0x4AAAAAADe4izf5gmW3H2aL'"
                  theme="light"
                />
              </div>

              <div>
                <button
                  type="submit"
                  :disabled="isLoading || !captchaToken"
                  class="flex w-full justify-center rounded-2xl border border-transparent bg-[var(--ct-primary)] px-4 py-3 text-sm font-bold text-white shadow-md transition-all hover:bg-[var(--ct-primary-hover)] focus:outline-none focus:ring-2 focus:ring-[var(--ct-primary)] focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {{ isLoading ? 'Autenticando...' : 'Entrar no sistema' }}
                </button>
              </div>
            </form>

            <div class="mt-8 text-center text-sm text-[var(--ct-text-muted)]">
              Ainda não tem uma conta?
              <RouterLink
                to="/cadastro"
                class="font-bold text-[var(--ct-ink)] transition-colors hover:text-[var(--ct-primary)]"
              >
                Criar escritório
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