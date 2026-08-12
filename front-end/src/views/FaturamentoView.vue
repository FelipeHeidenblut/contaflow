<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../services/api'
import Layout from '../components/Layout.vue'
import { toast } from 'vue3-toastify'
import { getApiErrorMessage } from '../utils/apiError'
import { getPlan, plans, type PlanOption } from '../constants/plans'

const isLoadingPlano = ref<string | null>(null)
const isLoadingCurrent = ref(true)
const planoAtual = ref('free')
const statusPagamento = ref('ativo')
const router = useRouter()
const route = useRoute()
const selectedPlan = computed(() => getPlan(route.query.plano))
const currentPlan = computed(() => getPlan(planoAtual.value))
const isCurrentPlan = (plan: PlanOption) => plan.id === planoAtual.value

const getCta = (plan: PlanOption) => {
  if (isCurrentPlan(plan)) return 'Plano atual'
  if (plan.sales) return 'Falar com vendas'
  if (plan.id === 'free') return 'Plano gratuito'
  return `Assinar ${plan.name}`
}

const loadCurrentPlan = async () => {
  try {
    const { data } = await api.get('/api/v1/dashboard/')
    planoAtual.value = data.plano || 'free'
    statusPagamento.value = data.status_pagamento || 'ativo'
  } catch {
    toast.error('Não foi possível identificar seu plano atual.')
  } finally {
    isLoadingCurrent.value = false
  }
}

const assinarPlano = async (plano: PlanOption) => {
  if (isCurrentPlan(plano) || plano.id === 'free') {
    toast.info(
      isCurrentPlan(plano)
        ? 'Este já é o seu plano atual.'
        : 'Entre em contato com o suporte para fazer downgrade.',
    )
    return
  }
  if (plano.sales) {
    router.push({ path: '/contato', query: { assunto: 'Plano Empresarial' } })
    return
  }

  isLoadingPlano.value = plano.id

  try {
    const response = await api.post(`/api/v1/asaas/criar-assinatura/${plano.id}`)

    if (response.data.invoice_url) {
      toast.success('Estamos te redirecionando para o pagamento seguro...')
      window.location.href = response.data.invoice_url
    } else {
      toast.error('Assinatura criada, mas o link de pagamento ainda está sendo gerado.')
    }
  } catch (error: unknown) {
    toast.error(getApiErrorMessage(error, 'Erro ao gerar a cobrança do plano.'))
  } finally {
    isLoadingPlano.value = null
  }
}

onMounted(loadCurrentPlan)
</script>

<template>
  <Layout title="Planos e Faturamento">
    <div class="ct-workspace space-y-4">
      <!-- hero -->
      <header class="ct-page-header border-b border-[var(--ct-border)] pb-6 text-left">
        <h1
          class="ct-page-title text-2xl font-semibold tracking-tight text-[var(--ct-ink)] md:text-3xl"
        >
          Escolha o plano ideal para o seu escritório
        </h1>
        <p
          class="ct-page-description mt-2 text-sm leading-relaxed text-[var(--ct-text-muted)] md:text-base"
        >
          Sem fidelidade. Pague com PIX, boleto ou cartão e solicite alterações pelo suporte.
        </p>
      </header>

      <section
        v-if="!isLoadingCurrent"
        class="ct-information-panel flex flex-col items-center justify-between gap-3 rounded-xl border border-[var(--ct-border)] bg-[var(--ct-primary-soft)] px-5 py-4 text-center sm:flex-row sm:text-left"
        role="status"
      >
        <div>
          <p class="text-sm font-semibold text-[var(--ct-primary)]">
            Seu plano: {{ currentPlan?.name || planoAtual }}
          </p>
          <p class="mt-0.5 text-xs text-[var(--ct-text-muted)]">
            Status:
            {{
              statusPagamento === 'ativo'
                ? 'Ativo'
                : statusPagamento === 'aguardando_pagamento'
                  ? 'Pagamento pendente'
                  : 'Requer atenção'
            }}
          </p>
        </div>
        <span class="rounded-full bg-white px-3 py-1 text-xs font-semibold text-[var(--ct-primary)]"
          >Assinatura mensal</span
        >
      </section>

      <section
        v-if="selectedPlan && selectedPlan.id !== planoAtual"
        class="ct-information-panel flex flex-col justify-between gap-4 rounded-xl border border-[var(--ct-primary)] bg-[var(--ct-primary-soft)] px-5 py-4 sm:flex-row sm:items-center"
        aria-live="polite"
      >
        <div>
          <p class="text-sm font-semibold text-[var(--ct-primary)]">
            Você escolheu o plano {{ selectedPlan.name }} — R$ {{ selectedPlan.price }}/mês.
          </p>
          <p class="mt-1 text-xs text-[var(--ct-text-muted)]">
            Confira os limites abaixo e prossiga quando estiver pronto.
          </p>
        </div>
        <button
          class="ct-button-primary shrink-0"
          type="button"
          @click="assinarPlano(selectedPlan)"
        >
          Continuar para pagamento
        </button>
      </section>

      <!-- trust strip -->
      <section
        class="ct-information-panel grid border-y border-[var(--ct-border)] bg-white sm:grid-cols-3 sm:divide-x sm:divide-[var(--ct-border)]"
      >
        <div class="px-4 py-3 text-center">
          <p class="text-xs font-medium text-[var(--ct-text-muted)]">Sem fidelidade</p>
          <p class="mt-1 text-sm font-semibold text-[var(--ct-ink)]">Cancele quando quiser</p>
        </div>

        <div class="border-t border-[var(--ct-border)] px-4 py-3 text-center sm:border-t-0">
          <p class="text-xs font-medium text-[var(--ct-text-muted)]">Pagamento seguro</p>
          <p class="mt-1 text-sm font-semibold text-[var(--ct-ink)]">Checkout protegido</p>
        </div>

        <div class="border-t border-[var(--ct-border)] px-4 py-3 text-center sm:border-t-0">
          <p class="text-xs font-medium text-[var(--ct-text-muted)]">Escalável</p>
          <p class="mt-1 text-sm font-semibold text-[var(--ct-ink)]">Cresça no seu ritmo</p>
        </div>
      </section>

      <!-- cards -->
      <section class="ct-plan-grid grid items-start gap-4 md:grid-cols-2 xl:grid-cols-4">
        <article
          v-for="plano in plans"
          :key="plano.id"
          class="relative flex h-full flex-col rounded-xl border bg-white p-6 transition-colors duration-200"
          :class="
            isCurrentPlan(plano)
              ? 'border-emerald-400 ring-2 ring-emerald-100'
              : selectedPlan?.id === plano.id
                ? 'border-[var(--ct-primary)] ring-2 ring-[var(--ct-primary-soft)]'
                : plano.featured
                  ? 'border-[var(--ct-primary)] ring-1 ring-[var(--ct-primary)]/20'
                  : 'border-[var(--ct-border)]'
          "
        >
          <div
            v-if="plano.featured"
            class="absolute right-4 top-4 text-[10px] font-bold uppercase tracking-[0.1em] text-[var(--ct-primary)]"
          >
            Mais popular
          </div>

          <div class="mb-5">
            <p class="text-xs font-semibold uppercase tracking-[0.12em] text-slate-400">
              {{ plano.name }}
            </p>

            <div class="mt-4 flex items-end gap-1">
              <span class="mb-1 text-lg font-semibold text-slate-400">R$</span>
              <span class="text-4xl font-semibold tracking-tight text-[var(--ct-ink)]">
                {{ plano.price }}
              </span>
            </div>

            <p class="mt-1 text-sm font-medium text-slate-400">/mês</p>
            <p class="mt-4 min-h-[42px] text-sm leading-relaxed text-[var(--ct-text-muted)]">
              {{ plano.description }}
            </p>
          </div>

          <ul class="mb-6 space-y-3 border-t border-[var(--ct-border)] pt-6">
            <li
              v-if="plano.id === 'profissional'"
              class="rounded-lg bg-[var(--ct-primary-soft)] px-3 py-2 text-xs font-semibold text-[var(--ct-primary)]"
            >
              25% menor custo por cliente que o Essencial
            </li>
            <li
              v-for="f in [`${plano.clients} clientes`, plano.users, ...plano.features]"
              :key="f"
              class="flex items-start gap-3 text-sm text-[var(--ct-ink)]"
            >
              <span
                class="mt-0.5 inline-flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-[var(--ct-primary-soft)] text-[var(--ct-primary)]"
              >
                <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="3"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </span>
              <span>{{ f }}</span>
            </li>
          </ul>

          <div class="mt-auto">
            <button
              @click="assinarPlano(plano)"
              :disabled="isLoadingPlano === plano.id || isCurrentPlan(plano) || isLoadingCurrent"
              class="w-full rounded-xl py-3 text-sm font-semibold transition-all duration-300 disabled:cursor-not-allowed disabled:opacity-50"
              :class="
                plano.featured
                  ? 'bg-[var(--ct-primary)] text-white hover:bg-[var(--ct-primary-hover)]'
                  : isCurrentPlan(plano) || plano.id === 'free'
                    ? 'border border-[var(--ct-border)] bg-slate-50 text-slate-400'
                    : 'border border-[var(--ct-border)] bg-white text-[var(--ct-ink)] hover:border-[var(--ct-primary)] hover:text-[var(--ct-primary)]'
              "
            >
              {{ isLoadingPlano === plano.id ? 'Gerando cobrança...' : getCta(plano) }}
            </button>
          </div>
        </article>
      </section>

      <!-- info box -->
      <section class="ct-information-panel border-t border-[var(--ct-border)] bg-white pt-6">
        <div class="grid gap-4 md:grid-cols-3">
          <div>
            <p class="text-sm font-semibold text-[var(--ct-ink)]">Upgrade simples</p>
            <p class="mt-1 text-sm text-[var(--ct-text-muted)]">
              Escolha o plano e siga para o pagamento com redirecionamento seguro.
            </p>
          </div>

          <div>
            <p class="text-sm font-semibold text-[var(--ct-ink)]">Sem travas desnecessárias</p>
            <p class="mt-1 text-sm text-[var(--ct-text-muted)]">
              Comece no Gratuito e evolua conforme o volume de clientes e equipe crescer.
            </p>
          </div>

          <div>
            <p class="text-sm font-semibold text-[var(--ct-ink)]">Para cada fase do escritório</p>
            <p class="mt-1 text-sm text-[var(--ct-text-muted)]">
              Dos contadores autônomos até operações maiores com necessidade de escala.
            </p>
          </div>
        </div>
      </section>
    </div>
  </Layout>
</template>
