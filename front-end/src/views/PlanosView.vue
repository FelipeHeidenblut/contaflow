<script setup lang="ts">
import { RouterLink } from 'vue-router'
import PublicLayout from '@/components/PublicLayout.vue'

const plans = [
  {
    name: 'Free',
    price: 'R$ 0',
    description: 'Para conhecer a plataforma.',
    features: ['Até 5 clientes', '1 usuário', 'Obrigações e calendário', 'Documentos'],
    cta: 'Começar grátis',
  },
  {
    name: 'Básico',
    price: 'R$ 79,90',
    description: 'Para contadores autônomos.',
    features: ['Até 40 clientes', 'Até 5 usuários', 'Tudo do Free', 'Alertas por e-mail'],
    cta: 'Escolher Básico',
  },
  {
    name: 'Profissional',
    price: 'R$ 149,90',
    description: 'Para escritórios em crescimento.',
    features: ['Até 100 clientes', 'Até 10 usuários', 'Tudo do Básico', 'Distribuição da equipe'],
    cta: 'Escolher Profissional',
    featured: true,
  },
  {
    name: 'Business',
    price: 'R$ 449',
    description: 'Para operações maiores.',
    features: [
      'Clientes ilimitados',
      'Usuários ilimitados',
      'API e integrações',
      'Atendimento dedicado',
    ],
    cta: 'Falar com vendas',
  },
]
const faq = [
  [
    'Posso começar sem pagar?',
    'Sim. O plano Free permite validar a rotina com até cinco clientes.',
  ],
  [
    'Existe fidelidade?',
    'Não. Os planos são mensais e podem ser alterados conforme a necessidade do escritório.',
  ],
  [
    'Como funciona o pagamento?',
    'A contratação pode ser paga com PIX, boleto ou cartão pelo checkout seguro.',
  ],
]
</script>

<template>
  <PublicLayout>
    <section class="border-b border-[var(--ct-border)] bg-white">
      <div class="ct-container py-16 text-center lg:py-24">
        <p class="ct-eyebrow">Planos</p>
        <h1 class="mx-auto mt-5 max-w-3xl text-4xl font-semibold tracking-[-0.04em] sm:text-5xl">
          Comece simples e aumente a capacidade quando precisar.
        </h1>
        <p class="ct-body-lg mx-auto mt-6">Sem fidelidade e sem uma implantação complexa.</p>
      </div>
    </section>
    <section class="ct-section">
      <div class="ct-container grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <article
          v-for="plan in plans"
          :key="plan.name"
          class="relative flex flex-col rounded-xl border bg-white p-6"
          :class="
            plan.featured
              ? 'border-[var(--ct-primary)] ring-1 ring-[var(--ct-primary)]'
              : 'border-[var(--ct-border)]'
          "
        >
          <p
            v-if="plan.featured"
            class="absolute right-4 top-4 text-[10px] font-bold uppercase tracking-wider text-[var(--ct-primary)]"
          >
            Recomendado
          </p>
          <h2 class="font-semibold">{{ plan.name }}</h2>
          <p class="mt-5 text-3xl font-semibold tracking-tight">{{ plan.price }}</p>
          <p class="mt-1 text-xs text-[var(--ct-text-muted)]">por mês</p>
          <p class="mt-4 min-h-10 text-sm text-[var(--ct-text-muted)]">{{ plan.description }}</p>
          <ul class="my-6 flex-1 space-y-3 border-t border-[var(--ct-border)] pt-6">
            <li v-for="feature in plan.features" :key="feature" class="flex gap-2 text-sm">
              <span class="text-[var(--ct-primary)]">✓</span>{{ feature }}
            </li>
          </ul>
          <RouterLink
            :to="plan.name === 'Business' ? '/contato?assunto=Plano Business' : '/cadastro'"
            :class="plan.featured ? 'ct-button-primary' : 'ct-button-secondary'"
            >{{ plan.cta }}</RouterLink
          >
        </article>
      </div>
    </section>
    <section class="border-y border-[var(--ct-border)] bg-white">
      <div class="ct-container grid gap-12 py-16 lg:grid-cols-[0.75fr_1.25fr]">
        <div>
          <p class="ct-eyebrow">Dúvidas frequentes</p>
          <h2 class="ct-section-title mt-4">Antes de escolher.</h2>
        </div>
        <dl class="border-t border-[var(--ct-border)]">
          <div v-for="item in faq" :key="item[0]" class="border-b border-[var(--ct-border)] py-6">
            <dt class="font-semibold">{{ item[0] }}</dt>
            <dd class="mt-2 text-sm leading-6 text-[var(--ct-text-muted)]">{{ item[1] }}</dd>
          </div>
        </dl>
      </div>
    </section>
  </PublicLayout>
</template>
