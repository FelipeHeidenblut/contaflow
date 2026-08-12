<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'
import Layout from '../components/Layout.vue'
import { toast } from 'vue3-toastify'
import { getApiErrorMessage } from '../utils/apiError'

const isLoadingPlano = ref<string | null>(null)
const isLoadingCurrent = ref(true)
const planoAtual = ref('free')
const statusPagamento = ref('ativo')
const router = useRouter()

const planos = [
  {
    nome: 'Free',
    price: '0',
    desc: 'Para testar a plataforma.',
    isFree: true,
    features: [
      'Até 5 clientes',
      '1 usuário (Admin)',
      'Calendário de obrigações',
      'Gestão de documentos',
      'Suporte por e-mail',
    ],
  },
  {
    nome: 'Básico',
    price: '79,90',
    desc: 'Para contadores autônomos.',
    features: [
      'Até 40 clientes',
      'Até 5 usuários',
      'Tudo do Free',
      'Alertas por e-mail',
      'Suporte por chat',
    ],
  },
  {
    nome: 'Profissional',
    price: '149,90',
    featured: true,
    desc: 'Para escritórios em crescimento.',
    features: [
      'Até 100 clientes',
      'Até 10 usuários',
      'Tudo do Básico',
      'Distribuição de equipe',
      'Relatórios avançados',
      'Suporte prioritário',
    ],
  },
  {
    nome: 'Business',
    price: '449',
    desc: 'Para grandes operações.',
    sales: true,
    features: [
      'Clientes ilimitados',
      'Usuários ilimitados',
      'Tudo do Profissional',
      'API e integrações',
      'Gerente de conta dedicado',
      'Onboarding assistido',
    ],
  },
]

const normalizePlan = (name: string) =>
  name
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
const isCurrentPlan = (name: string) => normalizePlan(name) === planoAtual.value
const currentPlanLabel = computed(
  () => planoAtual.value.charAt(0).toUpperCase() + planoAtual.value.slice(1),
)

type Plan = (typeof planos)[number]

const getCta = (plan: Plan) => {
  if (isCurrentPlan(plan.nome)) return 'Plano atual'
  if (plan.sales) return 'Falar com vendas'
  if (plan.isFree) return 'Plano gratuito'
  return `Assinar ${plan.nome}`
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

const assinarPlano = async (plano: Plan) => {
  const nomePlano = plano.nome
  if (isCurrentPlan(nomePlano) || plano.isFree) {
    toast.info(
      isCurrentPlan(nomePlano)
        ? 'Este já é o seu plano atual.'
        : 'Entre em contato com o suporte para fazer downgrade.',
    )
    return
  }
  if (plano.sales) {
    router.push({ path: '/contato', query: { assunto: 'Plano Business' } })
    return
  }

  isLoadingPlano.value = nomePlano

  try {
    const planoFormatado = nomePlano
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase()

    const response = await api.post(`/api/v1/asaas/criar-assinatura/${planoFormatado}`)

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
    <div class="space-y-7">
      <!-- hero -->
      <header class="border-b border-[var(--ct-border)] pb-6 text-left">
        <h1 class="text-2xl font-semibold tracking-tight text-[var(--ct-ink)] md:text-3xl">
          Escolha o plano ideal para o seu escritório
        </h1>
        <p class="mt-3 text-sm leading-relaxed text-[var(--ct-text-muted)] md:text-base">
          Sem fidelidade. Pague com PIX, boleto ou cartão e solicite alterações pelo suporte.
        </p>
      </header>

      <section
        v-if="!isLoadingCurrent"
        class="flex flex-col items-center justify-between gap-3 rounded-xl border border-[var(--ct-border)] bg-[var(--ct-primary-soft)] px-5 py-4 text-center sm:flex-row sm:text-left"
        role="status"
      >
        <div>
          <p class="text-sm font-semibold text-[var(--ct-primary)]">
            Seu plano: {{ currentPlanLabel }}
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

      <!-- trust strip -->
      <section
        class="grid border-y border-[var(--ct-border)] sm:grid-cols-3 sm:divide-x sm:divide-[var(--ct-border)]"
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
      <section class="grid items-start gap-6 md:grid-cols-2 xl:grid-cols-4">
        <article
          v-for="plano in planos"
          :key="plano.nome"
          class="relative flex h-full flex-col rounded-xl border bg-white p-6 transition-colors duration-200"
          :class="
            isCurrentPlan(plano.nome)
              ? 'border-emerald-400 ring-2 ring-emerald-100'
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
              {{ plano.nome }}
            </p>

            <div class="mt-4 flex items-end gap-1">
              <span class="mb-1 text-lg font-semibold text-slate-400">R$</span>
              <span class="text-4xl font-semibold tracking-tight text-[var(--ct-ink)]">
                {{ plano.price }}
              </span>
            </div>

            <p class="mt-1 text-sm font-medium text-slate-400">/mês</p>
            <p class="mt-4 min-h-[42px] text-sm leading-relaxed text-[var(--ct-text-muted)]">
              {{ plano.desc }}
            </p>
          </div>

          <ul class="mb-6 space-y-3 border-t border-[var(--ct-border)] pt-6">
            <li
              v-for="f in plano.features"
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
              :disabled="
                isLoadingPlano === plano.nome || isCurrentPlan(plano.nome) || isLoadingCurrent
              "
              class="w-full rounded-xl py-3 text-sm font-semibold transition-all duration-300 disabled:cursor-not-allowed disabled:opacity-50"
              :class="
                plano.featured
                  ? 'bg-[var(--ct-primary)] text-white hover:bg-[var(--ct-primary-hover)]'
                  : isCurrentPlan(plano.nome) || plano.isFree
                    ? 'border border-[var(--ct-border)] bg-slate-50 text-slate-400'
                    : 'border border-[var(--ct-border)] bg-white text-[var(--ct-ink)] hover:border-[var(--ct-primary)] hover:text-[var(--ct-primary)]'
              "
            >
              {{ isLoadingPlano === plano.nome ? 'Gerando cobrança...' : getCta(plano) }}
            </button>
          </div>
        </article>
      </section>

      <!-- info box -->
      <section class="border-t border-[var(--ct-border)] pt-6">
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
              Comece no Free e evolua conforme o volume de clientes e equipe crescer.
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
