<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import VueTurnstile from 'vue-turnstile'
import { supabase } from '../services/supabase'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'
import AuthShell from '@/components/AuthShell.vue'
import { getPlan, getPlanPrice, isBillingCycle } from '@/constants/plans'
import { appConfig } from '@/config/env'
import { SESSION_REQUEST_TIMEOUT_MS, isTemporarySessionError } from '../services/sessionRecovery'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const selectedPlan = getPlan(route.query.plano)
const selectedCycle = isBillingCycle(route.query.ciclo) ? route.query.ciclo : 'monthly'
const selectedQuery = selectedPlan
  ? { plano: selectedPlan.id, ...(selectedCycle === 'annual' ? { ciclo: 'annual' } : {}) }
  : {}
const isLoading = ref(false)
const erroMensagem = ref('')
const email = ref('')
const senha = ref('')
const captchaToken = ref('')
const turnstileSiteKey = appConfig.turnstileSiteKey
const hasAuthenticatedSession = ref(false)
const isConnecting = ref(false)

onMounted(async () => {
  const { data } = await supabase.auth.getSession()
  hasAuthenticatedSession.value = !!data.session
})

const getErrorMessage = (error: unknown): string => {
  const candidate = error as {
    response?: { data?: { detail?: string | Array<{ msg?: string }> } }
    message?: string
  }
  const detail = candidate.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail))
    return (
      detail
        .map((item) => item.msg)
        .filter(Boolean)
        .join(' ') || 'Dados inválidos.'
    )
  return candidate.message || 'Ocorreu um erro ao tentar fazer login.'
}

const handleLogin = async () => {
  if (isLoading.value) return
  if (!hasAuthenticatedSession.value && !captchaToken.value) {
    erroMensagem.value = 'Por favor, aguarde a verificação de segurança.'
    return
  }
  erroMensagem.value = ''
  isLoading.value = true
  try {
    const { data, error } = hasAuthenticatedSession.value
      ? await supabase.auth.getSession()
      : await supabase.auth.signInWithPassword({
          email: email.value,
          password: senha.value,
          options: { captchaToken: captchaToken.value },
        })
    if (error) throw error
    if (!data.session) {
      hasAuthenticatedSession.value = false
      throw new Error('Sua sessão expirou. Entre novamente com e-mail e senha.')
    }
    if (data.session) {
      hasAuthenticatedSession.value = true
      isConnecting.value = true
      senha.value = ''
      const user = data.session.user
      let profile: {
        user_id?: string
        tenant_id?: string
        role?: string
        is_superadmin?: boolean
      }
      try {
        const response = await api.get('/api/v1/auth/me', { timeout: SESSION_REQUEST_TIMEOUT_MS })
        profile = response.data
      } catch (syncError: unknown) {
        const candidate = syncError as { response?: { status?: number } }
        if (candidate.response?.status !== 403) throw syncError
        const metadata = user.user_metadata
        if (!metadata?.company_name || !metadata?.documento) {
          await supabase.auth.signOut()
          hasAuthenticatedSession.value = false
          throw new Error(
            'Seu cadastro antigo está incompleto. Entre em contato com o suporte para vincular seu escritório.',
          )
        }
        const syncResponse = await api.post(
          '/api/v1/auth/sincronizar-cadastro',
          {
            nome_completo: metadata.full_name || user.email,
            nome_escritorio: metadata.company_name,
            documento: metadata.documento,
          },
          { timeout: SESSION_REQUEST_TIMEOUT_MS },
        )
        profile = {
          user_id: user.id,
          tenant_id: syncResponse.data.tenant_id,
          role: 'admin',
          is_superadmin: false,
        }
      }
      authStore.initializeAuthenticatedSession(profile, user)
      await router.push(
        selectedPlan && selectedPlan.id !== 'free'
          ? { path: '/faturamento', query: selectedQuery }
          : '/dashboard',
      )
    }
  } catch (error: unknown) {
    const message = getErrorMessage(error)
    if (isTemporarySessionError(error)) {
      erroMensagem.value = hasAuthenticatedSession.value
        ? 'Sua sessão está autenticada, mas o escritório ainda não respondeu. Tente conectar novamente; não é necessário informar sua senha.'
        : 'Não foi possível conectar agora. Aguarde um momento e tente novamente.'
    } else if (message === 'Invalid login credentials')
      erroMensagem.value = 'E-mail ou senha incorretos.'
    else if (message === 'Email not confirmed')
      erroMensagem.value = 'Por favor, confirme seu e-mail antes de acessar.'
    else erroMensagem.value = message
    const { data } = await supabase.auth.getSession()
    hasAuthenticatedSession.value = !!data.session
    captchaToken.value = ''
  } finally {
    isLoading.value = false
    isConnecting.value = false
  }
}
</script>

<template>
  <AuthShell
    title="Acesse seu escritório"
    description="Entre para acompanhar clientes, obrigações e documentos."
  >
    <template #mobile-action
      ><RouterLink
        :to="{ path: '/cadastro', query: selectedQuery }"
        class="text-xs font-semibold text-[var(--ct-primary)]"
        >Criar conta</RouterLink
      ></template
    >
    <div
      v-if="selectedPlan && selectedPlan.id !== 'free'"
      class="mb-5 rounded-xl border border-[var(--ct-primary)]/25 bg-[var(--ct-primary-soft)] px-4 py-3"
    >
      <p class="text-sm font-semibold text-[var(--ct-primary)]">
        Plano selecionado: {{ selectedPlan.name }} — R$
        {{ getPlanPrice(selectedPlan, selectedCycle) }}/{{
          selectedCycle === 'annual' ? 'ano' : 'mês'
        }}
      </p>
      <p class="mt-1 text-xs text-[var(--ct-text-muted)]">
        Entre para revisar o plano e continuar para o pagamento.
      </p>
    </div>
    <div
      v-if="erroMensagem"
      role="alert"
      class="mb-5 border-l-2 border-red-500 bg-red-50 px-4 py-3 text-sm text-red-700"
    >
      {{ erroMensagem }}
    </div>
    <form class="space-y-5" @submit.prevent="handleLogin">
      <div v-if="!hasAuthenticatedSession">
        <label for="login-email" class="ct-label">E-mail</label
        ><input
          id="login-email"
          v-model="email"
          class="ct-field"
          type="email"
          autocomplete="username"
          required
          autofocus
          placeholder="seu@email.com"
        />
      </div>
      <div v-if="!hasAuthenticatedSession">
        <div class="mb-1.5 flex items-center justify-between">
          <label for="login-password" class="text-[13px] font-semibold text-slate-700">Senha</label
          ><RouterLink to="/esqueceu-senha" class="text-xs font-semibold text-[var(--ct-primary)]"
            >Esqueci minha senha</RouterLink
          >
        </div>
        <input
          id="login-password"
          v-model="senha"
          class="ct-field"
          type="password"
          autocomplete="current-password"
          required
          placeholder="Sua senha"
        />
      </div>
      <p
        v-if="hasAuthenticatedSession"
        role="status"
        aria-live="polite"
        class="text-sm text-slate-600"
      >
        {{
          isConnecting
            ? 'Conectando ao escritório… A primeira conexão pode levar até 90 segundos.'
            : 'Sua sessão foi identificada. Continue para conectar ao escritório.'
        }}
      </p>
      <div v-if="!hasAuthenticatedSession" class="flex justify-center overflow-hidden py-1">
        <VueTurnstile
          v-model="captchaToken"
          :site-key="turnstileSiteKey || '0x4AAAAAADe4izf5gmW3H2aL'"
          theme="light"
        />
      </div>
      <button
        type="submit"
        :disabled="isLoading"
        class="ct-button-primary w-full disabled:cursor-not-allowed disabled:opacity-50"
      >
        {{
          isConnecting
            ? 'Conectando ao escritório…'
            : isLoading
              ? 'Entrando…'
              : hasAuthenticatedSession
                ? 'Conectar ao escritório'
                : 'Entrar'
        }}
      </button>
    </form>
    <p
      class="mt-7 border-t border-[var(--ct-border)] pt-6 text-center text-sm text-[var(--ct-text-muted)]"
    >
      Ainda não tem conta?
      <RouterLink
        :to="{ path: '/cadastro', query: selectedQuery }"
        class="font-semibold text-[var(--ct-primary)]"
        >Comece gratuitamente</RouterLink
      >
    </p>
  </AuthShell>
</template>
