<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, RouterLink, useRoute } from 'vue-router'
import VueTurnstile from 'vue-turnstile'
import { toast } from 'vue3-toastify'
import { supabase } from '../services/supabase'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'
import AuthShell from '@/components/AuthShell.vue'
import { getPlan, getPlanPrice, isBillingCycle } from '@/constants/plans'
import { appConfig } from '@/config/env'

const router = useRouter()
const authStore = useAuthStore()
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
const turnstileSiteKey = appConfig.turnstileSiteKey
const showPassword = ref(false)
const selectedPlan = getPlan(route.query.plano)
const selectedCycle = isBillingCycle(route.query.ciclo) ? route.query.ciclo : 'monthly'
const selectedQuery = selectedPlan
  ? { plano: selectedPlan.id, ...(selectedCycle === 'annual' ? { ciclo: 'annual' } : {}) }
  : {}

const documentoFormatado = computed({
  get() {
    let value = documentoRaw.value.replace(/\D/g, '')
    if (value.length <= 11) {
      value = value
        .replace(/(\d{3})(\d)/, '$1.$2')
        .replace(/(\d{3})(\d)/, '$1.$2')
        .replace(/(\d{3})(\d{1,2})$/, '$1-$2')
    } else {
      value = value
        .replace(/^(\d{2})(\d)/, '$1.$2')
        .replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3')
        .replace(/\.(\d{3})(\d)/, '.$1/$2')
        .replace(/(\d{4})(\d)/, '$1-$2')
    }
    return value
  },
  set(value: string) {
    documentoRaw.value = value.replace(/\D/g, '').slice(0, 14)
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
  if (![11, 14].includes(documentoRaw.value.length)) {
    erroMensagem.value = 'O documento deve ser um CPF ou CNPJ válido.'
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
          company_name: nomeEscritorio.value,
          documento: documentoRaw.value,
        },
        captchaToken: captchaToken.value,
      },
    })
    if (error) throw error
    if (data.user) {
      try {
        if (data.session) {
          const syncResponse = await api.post('/api/v1/auth/sincronizar-cadastro', {
            nome_completo: nomeCompleto.value,
            nome_escritorio: nomeEscritorio.value,
            documento: documentoRaw.value,
          })
          authStore.initializeAuthenticatedSession(
            {
              user_id: data.user.id,
              tenant_id: syncResponse.data.tenant_id,
              role: 'admin',
              is_superadmin: false,
            },
            data.user,
          )
          router.push(
            selectedPlan && selectedPlan.id !== 'free'
              ? { path: '/faturamento', query: selectedQuery }
              : '/dashboard',
          )
        } else {
          toast.success('Conta criada! Verifique seu e-mail para confirmar antes de entrar.')
          router.push({
            path: '/login',
            query: selectedPlan && selectedPlan.id !== 'free' ? selectedQuery : {},
          })
        }
      } catch {
        erroMensagem.value = 'Conta criada, mas falhou ao sincronizar. Tente fazer login.'
      }
    }
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : ''
    erroMensagem.value =
      message === 'User already registered'
        ? 'Este e-mail já está cadastrado.'
        : message || 'Ocorreu um erro ao criar a conta.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <AuthShell
    wide
    title="Crie seu escritório"
    description="Configure a conta administradora. Você poderá adicionar clientes e membros depois."
  >
    <template #mobile-action
      ><RouterLink
        :to="{ path: '/login', query: selectedQuery }"
        class="text-xs font-semibold text-[var(--ct-primary)]"
        >Entrar</RouterLink
      ></template
    >
    <div
      v-if="selectedPlan && selectedPlan.id !== 'free'"
      class="mb-5 rounded-xl border border-[var(--ct-primary)]/25 bg-[var(--ct-primary-soft)] px-4 py-3"
    >
      <p class="text-sm font-semibold text-[var(--ct-primary)]">
        Você escolheu o plano {{ selectedPlan.name }} — R$
        {{ getPlanPrice(selectedPlan, selectedCycle) }}/{{
          selectedCycle === 'annual' ? 'ano' : 'mês'
        }}
      </p>
      <p class="mt-1 text-xs text-[var(--ct-text-muted)]">
        Crie o escritório primeiro. O pagamento será apresentado depois do acesso.
      </p>
    </div>
    <div
      v-if="erroMensagem"
      role="alert"
      class="mb-5 border-l-2 border-red-500 bg-red-50 px-4 py-3 text-sm text-red-700"
    >
      {{ erroMensagem }}
    </div>
    <form class="space-y-5" @submit.prevent="handleRegister">
      <div class="grid gap-5 sm:grid-cols-2">
        <div>
          <label for="register-name" class="ct-label">Seu nome</label
          ><input
            id="register-name"
            v-model="nomeCompleto"
            class="ct-field"
            required
            autocomplete="name"
            placeholder="Nome completo"
          />
        </div>
        <div>
          <label for="register-email" class="ct-label">E-mail profissional</label
          ><input
            id="register-email"
            v-model="email"
            class="ct-field"
            required
            type="email"
            autocomplete="email"
            placeholder="voce@escritorio.com.br"
          />
        </div>
        <div>
          <label for="register-company" class="ct-label">Nome do escritório</label
          ><input
            id="register-company"
            v-model="nomeEscritorio"
            class="ct-field"
            required
            autocomplete="organization"
            placeholder="Nome do escritório"
          />
        </div>
        <div>
          <label for="register-document" class="ct-label">CPF ou CNPJ</label
          ><input
            id="register-document"
            v-model="documentoFormatado"
            class="ct-field"
            required
            inputmode="numeric"
            placeholder="Documento do responsável"
          />
          <p class="ct-help">
            Usado para identificar o responsável pelo escritório e preparar futuras contratações.
            Nenhuma cobrança é feita no plano gratuito.
          </p>
        </div>
      </div>
      <div>
        <label for="register-password" class="ct-label">Senha</label>
        <div class="relative">
          <input
            id="register-password"
            v-model="senha"
            class="ct-field pr-20"
            required
            :type="showPassword ? 'text' : 'password'"
            autocomplete="new-password"
            minlength="8"
            maxlength="72"
            placeholder="Mínimo de 8 caracteres"
          />
          <button
            type="button"
            class="absolute inset-y-0 right-0 px-4 text-xs font-semibold text-[var(--ct-primary)]"
            :aria-label="showPassword ? 'Ocultar senha' : 'Mostrar senha'"
            :aria-pressed="showPassword"
            @click="showPassword = !showPassword"
          >
            {{ showPassword ? 'Ocultar' : 'Mostrar' }}
          </button>
        </div>
        <p class="ct-help">Use pelo menos 8 caracteres e uma senha exclusiva para esta conta.</p>
      </div>
      <label class="flex items-start gap-3 text-sm leading-5 text-[var(--ct-text-muted)]"
        ><input
          v-model="acceptedTerms"
          type="checkbox"
          class="mt-0.5 h-4 w-4 rounded border-slate-300 text-[var(--ct-primary)]"
        /><span
          >Li e aceito os
          <RouterLink to="/termos" class="font-semibold text-[var(--ct-primary)]"
            >Termos de Uso</RouterLink
          >
          e a
          <RouterLink to="/privacidade" class="font-semibold text-[var(--ct-primary)]"
            >Política de Privacidade</RouterLink
          >.</span
        ></label
      >
      <div class="flex justify-center overflow-hidden py-1">
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
          isLoading
            ? 'Criando conta…'
            : selectedPlan && selectedPlan.id !== 'free'
              ? 'Criar escritório e continuar'
              : 'Criar conta gratuita'
        }}
      </button>
      <p class="text-center text-xs text-[var(--ct-text-muted)]">
        Gratuito para até 5 clientes · Sem cartão · Sem fidelidade
      </p>
    </form>
    <p
      class="mt-7 border-t border-[var(--ct-border)] pt-6 text-center text-sm text-[var(--ct-text-muted)]"
    >
      Já possui uma conta?
      <RouterLink
        :to="{ path: '/login', query: selectedQuery }"
        class="font-semibold text-[var(--ct-primary)]"
        >Entrar</RouterLink
      >
    </p>
  </AuthShell>
</template>
