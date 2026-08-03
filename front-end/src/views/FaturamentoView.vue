<script setup lang="ts">
import { ref } from 'vue'
import api from '../services/api'
import Layout from '../components/Layout.vue'
import { toast } from 'vue3-toastify'

const isLoadingPlano = ref<string | null>(null)

const planos = [
  {
    nome: 'Free',
    price: '0',
    desc: 'Para testar a plataforma.',
    cta: 'Plano atual',
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
    cta: 'Assinar Básico',
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
    cta: 'Assinar Profissional',
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
    cta: 'Falar com vendas',
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

const assinarPlano = async (nomePlano: string, isFree: boolean = false) => {
  if (isFree) {
    toast.info('Você já pode utilizar os recursos do plano Free. Faça upgrade para liberar mais.')
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
  } catch (error: any) {
    const detail = error.response?.data?.detail || 'Erro ao gerar a cobrança do plano.'
    toast.error(detail)
  } finally {
    isLoadingPlano.value = null
  }
}
</script>

<template>
  <Layout title="Planos e Faturamento">
    <div class="space-y-8">
      <!-- hero -->
      <header class="mx-auto max-w-3xl text-center">
        <h1 class="text-3xl font-semibold tracking-tight text-[var(--ct-ink)] md:text-4xl">
          Escolha o plano ideal para o seu escritório
        </h1>
        <p class="mt-3 text-sm leading-relaxed text-[var(--ct-text-muted)] md:text-base">
          Cancele quando quiser. Sem fidelidade. Pague com PIX, boleto ou cartão.
        </p>
      </header>

      <!-- trust strip -->
      <section class="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div class="rounded-xl border border-[var(--ct-border)] bg-white p-4 text-center shadow-sm">
          <p class="text-xs font-medium text-[var(--ct-text-muted)]">Sem fidelidade</p>
          <p class="mt-1 text-sm font-semibold text-[var(--ct-ink)]">Cancele quando quiser</p>
        </div>

        <div class="rounded-xl border border-[var(--ct-border)] bg-white p-4 text-center shadow-sm">
          <p class="text-xs font-medium text-[var(--ct-text-muted)]">Pagamento seguro</p>
          <p class="mt-1 text-sm font-semibold text-[var(--ct-ink)]">Checkout protegido</p>
        </div>

        <div class="rounded-xl border border-[var(--ct-border)] bg-white p-4 text-center shadow-sm">
          <p class="text-xs font-medium text-[var(--ct-text-muted)]">Escalável</p>
          <p class="mt-1 text-sm font-semibold text-[var(--ct-ink)]">Cresça no seu ritmo</p>
        </div>
      </section>

      <!-- cards -->
      <section class="grid items-start gap-6 md:grid-cols-2 xl:grid-cols-4">
        <article
          v-for="plano in planos"
          :key="plano.nome"
          class="relative flex h-full flex-col rounded-2xl border bg-white p-6 shadow-sm transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg"
          :class="
            plano.featured
              ? 'border-[var(--ct-primary)] shadow-[0_20px_60px_rgba(37,99,235,0.14)]'
              : 'border-[var(--ct-border)]'
          "
        >
          <div
            v-if="plano.featured"
            class="absolute left-1/2 top-0 -translate-x-1/2 -translate-y-1/2 rounded-full bg-[var(--ct-primary)] px-4 py-1.5 text-[11px] font-bold uppercase tracking-[0.08em] text-white shadow-md"
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
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/>
                </svg>
              </span>
              <span>{{ f }}</span>
            </li>
          </ul>

          <div class="mt-auto">
            <button
              @click="assinarPlano(plano.nome, plano.isFree)"
              :disabled="isLoadingPlano === plano.nome || plano.isFree"
              class="w-full rounded-xl py-3 text-sm font-semibold transition-all duration-300 disabled:cursor-not-allowed disabled:opacity-50"
              :class="
                plano.featured
                  ? 'bg-[var(--ct-primary)] text-white hover:bg-[var(--ct-primary-hover)] shadow-sm'
                  : plano.isFree
                    ? 'border border-[var(--ct-border)] bg-slate-50 text-slate-400'
                    : 'border border-[var(--ct-border)] bg-white text-[var(--ct-ink)] hover:border-[var(--ct-primary)] hover:text-[var(--ct-primary)]'
              "
            >
              {{ isLoadingPlano === plano.nome ? 'Gerando cobrança...' : plano.cta }}
            </button>
          </div>
        </article>
      </section>

      <!-- info box -->
      <section class="rounded-2xl border border-[var(--ct-border)] bg-white p-5 shadow-sm">
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