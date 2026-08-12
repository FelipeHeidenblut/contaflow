<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue3-toastify'
import VueTurnstile from 'vue-turnstile'
import { supabase } from '../services/supabase'
import { useAuthStore } from '../stores/auth'
import BrandMark from '@/components/BrandMark.vue'
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
    const { data, error } = await supabase.auth.signInWithPassword({
      email: email.value,
      password: senha.value,
      options: { captchaToken: captchaToken.value },
    })
    if (error) throw error
    if (data?.session) {
      try {
        const activeSession = await authStore.checkSession(true)
        if (!activeSession || !authStore.isSuperAdmin) throw new Error('Acesso negado.')
        toast.success('Bem-vindo ao backoffice.')
        router.push('/admin')
      } catch (authError: unknown) {
        await supabase.auth.signOut()
        const candidate = authError as { response?: { data?: { detail?: string } } }
        throw new Error(candidate.response?.data?.detail || 'Acesso negado.')
      }
    }
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : ''
    erroMensagem.value =
      message === 'Invalid login credentials'
        ? 'Credenciais administrativas inválidas.'
        : message || 'Falha na autenticação.'
    captchaToken.value = ''
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-[var(--ct-navy)] px-5 py-12">
    <div class="w-full max-w-sm">
      <div class="mb-8 text-center text-white">
        <BrandMark inverse />
        <p class="mt-6 text-xs font-semibold uppercase tracking-[0.14em] text-[var(--ct-accent)]">
          Acesso restrito
        </p>
        <h1 class="mt-3 text-2xl font-semibold tracking-tight">Backoffice SaaS</h1>
      </div>
      <form
        class="rounded-xl border border-white/15 bg-white p-6"
        @submit.prevent="handleAdminLogin"
      >
        <div
          v-if="erroMensagem"
          class="mb-5 border-l-2 border-red-500 bg-red-50 px-3 py-2 text-sm text-red-700"
        >
          {{ erroMensagem }}
        </div>
        <div class="space-y-5">
          <div>
            <label for="admin-email" class="ct-label">E-mail administrativo</label
            ><input
              id="admin-email"
              v-model="email"
              class="ct-field"
              type="email"
              autocomplete="username"
              required
            />
          </div>
          <div>
            <label for="admin-password" class="ct-label">Senha</label
            ><input
              id="admin-password"
              v-model="senha"
              class="ct-field"
              type="password"
              autocomplete="current-password"
              required
            />
          </div>
          <div class="flex justify-center overflow-hidden">
            <VueTurnstile
              v-model="captchaToken"
              site-key="0x4AAAAAADe4izf5gmW3H2aL"
              theme="light"
            />
          </div>
          <button
            type="submit"
            :disabled="isLoading || !captchaToken"
            class="ct-button-primary w-full disabled:opacity-50"
          >
            {{ isLoading ? 'Verificando…' : 'Autorizar acesso' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
