<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { supabase } from '../services/supabase'
import { toast } from 'vue3-toastify'
import VueTurnstile from 'vue-turnstile'

const email = ref('')
const isLoading = ref(false)
const emailEnviado = ref(false)

const captchaToken = ref('')

const turnstileSiteKey = import.meta.env.VITE_TURNSTILE_SITE_KEY || ''

const handleResetPassword = async () => {
  if (!captchaToken.value) {
    toast.error('Por favor, conclua a verificação de segurança.')
    return
  }

  isLoading.value = true

  try {
    const { error } = await supabase.auth.resetPasswordForEmail(email.value, {
      redirectTo: `${window.location.origin}/redefinir-senha`,
      captchaToken: captchaToken.value,
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
          class="absolute top-1/4 left-1/4 h-96 w-96 rounded-full bg-[var(--ct-primary)]/20 blur-[120px]"
        ></div>

        <div
          class="absolute bottom-1/3 right-1/4 h-72 w-72 rounded-full bg-[#1E3A8A]/20 blur-3xl"
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
            Recupere o acesso à sua conta com segurança e volte a ter controle da sua rotina contábil.
          </p>

          <div class="mt-10 grid max-w-md gap-3 text-left">
            <div class="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur-sm">
              <div class="text-sm font-semibold text-white">Recuperação segura</div>
              <p class="mt-1 text-sm leading-relaxed text-white/65">
                Enviamos um link protegido para redefinição da senha no e-mail cadastrado.
              </p>
            </div>

            <div class="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur-sm">
              <div class="text-sm font-semibold text-white">Acesso rápido</div>
              <p class="mt-1 text-sm leading-relaxed text-white/65">
                Em poucos passos você volta ao painel e continua de onde parou.
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
            <div class="mb-8">
              <h2 class="mb-2 text-2xl font-extrabold tracking-tight text-[var(--ct-ink)]">
                Esqueceu a senha?
              </h2>
              <p class="text-[0.95rem] text-[var(--ct-text-muted)]">
                Informe seu e-mail cadastrado e enviaremos um link seguro para redefinir sua senha.
              </p>
            </div>

            <!-- Sucesso -->
            <div
              v-if="emailEnviado"
              class="rounded-2xl border border-green-200 bg-green-50 p-5 text-sm text-green-800 shadow-sm"
            >
              <div class="flex items-start gap-3">
                <svg
                  class="h-6 w-6 flex-shrink-0 text-green-700"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>

                <div>
                  <strong class="font-bold">E-mail enviado!</strong><br />
                  Verifique sua caixa de entrada e a pasta de spam. Depois, clique no link para redefinir sua senha.
                </div>
              </div>

              <div class="mt-5 border-t border-green-200 pt-4">
                <RouterLink
                  to="/login"
                  class="font-bold text-[var(--ct-primary)] transition-colors hover:text-[var(--ct-primary-hover)]"
                >
                  ← Voltar para o login
                </RouterLink>
              </div>
            </div>

            <!-- Form -->
            <form v-else @submit.prevent="handleResetPassword" class="space-y-6">
              <div>
                <label class="mb-1.5 block text-sm font-medium text-[var(--ct-ink)]/80">
                  E-mail cadastrado
                </label>
                <input
                  v-model="email"
                  type="email"
                  required
                  placeholder="seu@email.com"
                  class="w-full rounded-2xl border border-[var(--ct-border)] bg-white px-4 py-3 text-sm text-[var(--ct-ink)] shadow-sm transition-all placeholder:text-slate-400 focus:border-[var(--ct-primary)] focus:outline-none focus:ring-4 focus:ring-[var(--ct-primary)]/10"
                />
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
                  class="flex w-full justify-center rounded-2xl border border-transparent bg-[var(--ct-primary)] px-4 py-3 text-sm font-semibold text-white shadow-md transition-all hover:bg-[var(--ct-primary-hover)] focus:outline-none focus:ring-2 focus:ring-[var(--ct-primary)] focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {{ isLoading ? 'Enviando...' : 'Enviar link de recuperação' }}
                </button>
              </div>
            </form>

            <div v-if="!emailEnviado" class="mt-8 text-center text-sm text-[var(--ct-text-muted)]">
              Lembrou a senha?
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