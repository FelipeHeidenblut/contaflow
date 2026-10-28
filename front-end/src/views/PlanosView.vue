<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import PublicLayout from '@/components/PublicLayout.vue'
import PublicPageHero from '@/components/PublicPageHero.vue'
import PublicCallToAction from '@/components/PublicCallToAction.vue'
import { getPlanMonthlyPrice, getPlanPrice, plans, type BillingCycle } from '@/constants/plans'

const billingCycle = ref<BillingCycle>('monthly')

const comparison = [
  { label: 'Clientes ativos', values: plans.map((plan) => plan.clients) },
  { label: 'Usuários', values: plans.map((plan) => plan.users) },
  { label: 'Obrigações recorrentes', values: plans.map(() => 'Incluído') },
  { label: 'Calendário compartilhável', values: plans.map(() => 'Incluído') },
  { label: 'Documentos por cliente', values: plans.map(() => 'Incluído') },
  { label: 'Tamanho máximo por arquivo', values: plans.map(() => '5 MB') },
  {
    label: 'Relatórios operacionais',
    values: plans.map((plan) =>
      plan.id === 'free' ? 'Prévia' : plan.id === 'basico' ? 'Resumo' : 'Avançado',
    ),
  },
  {
    label: 'Período de análise',
    values: plans.map((plan) =>
      plan.id === 'free' ? '—' : plan.id === 'basico' ? 'Até 3 meses' : 'Até 12 meses',
    ),
  },
  {
    label: 'Desempenho por cliente e colaborador',
    values: plans.map((plan) =>
      ['profissional', 'escritorio', 'business'].includes(plan.id) ? 'Incluído' : '—',
    ),
  },
  {
    label: 'Filtros por cliente e responsável',
    values: plans.map((plan) =>
      ['profissional', 'escritorio', 'business'].includes(plan.id) ? 'Incluído' : '—',
    ),
  },
  {
    label: 'Exportação CSV',
    values: plans.map((plan) =>
      ['profissional', 'escritorio', 'business'].includes(plan.id) ? 'Incluído' : '—',
    ),
  },
]

const faq = [
  [
    'Como funcionam os 14 dias gratuitos?',
    'Novos escritórios experimentam o Profissional por 14 dias, sem cartão e sem cobrança automática. Sem contratação ao final, a conta retorna ao Gratuito.',
  ],
  [
    'O que acontece quando atinjo um limite?',
    'Seus dados continuam disponíveis. Para adicionar novos clientes ou usuários, libere espaço ou escolha um plano com maior capacidade.',
  ],
  [
    'O que os planos pagos acrescentam?',
    'O Essencial libera um resumo operacional de até 3 meses. Profissional, Escritório e Empresarial acrescentam análises de até 12 meses, desempenho por cliente e equipe, filtros avançados e exportação CSV.',
  ],
  [
    'Existe fidelidade?',
    'Não há renovação obrigatória. Você escolhe o ciclo mensal ou anual e pode cancelar a próxima renovação.',
  ],
  [
    'Como funciona o pagamento?',
    'A contratação é concluída em checkout externo protegido, com PIX, boleto ou cartão.',
  ],
]
</script>
<template>
  <PublicLayout>
    <div class="ct-clarity-page">
      <PublicPageHero
        eyebrow="Planos e preços"
        title="Um plano para cada fase do seu escritório."
        description="Comece com 14 dias do Profissional grátis. Depois, escolha a capacidade que acompanha sua carteira, sua equipe e sua rotina."
      >
        <template #actions
          ><RouterLink to="/cadastro" class="ct-button-primary"
            >Experimentar por 14 dias <span aria-hidden="true">→</span></RouterLink
          ></template
        >
        <template #note
          >Sem cartão · Sem cobrança automática · Plano Gratuito disponível após o teste</template
        >
      </PublicPageHero>
      <section class="ct-public-section">
        <div class="ct-container">
          <div class="mb-10 flex flex-col items-center gap-4 text-center">
            <div
              role="group"
              aria-label="Período de cobrança"
              class="inline-flex rounded-lg border border-blue-100 bg-[#f5f8ff] p-1"
            >
              <button
                v-for="cycle in [
                  { value: 'monthly', label: 'Mensal' },
                  { value: 'annual', label: 'Anual' },
                ] as const"
                :key="cycle.value"
                type="button"
                :aria-pressed="billingCycle === cycle.value"
                class="rounded-md px-6 py-2.5 text-sm font-medium"
                :class="
                  billingCycle === cycle.value
                    ? 'bg-[#087cff] text-white'
                    : 'text-slate-500 hover:bg-white'
                "
                @click="billingCycle = cycle.value"
              >
                {{ cycle.label }}
              </button>
            </div>
            <p class="text-xs leading-6 text-slate-500">
              {{
                billingCycle === 'annual'
                  ? 'No ciclo anual, o valor total é cobrado uma vez por ano.'
                  : 'Escolha o pagamento mensal ou compare o valor do ciclo anual.'
              }}
            </p>
          </div>
          <div
            class="grid gap-5 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5"
            aria-label="Planos disponíveis"
          >
            <article
              v-for="plan in plans"
              :key="plan.id"
              class="ct-public-plan"
              :class="{ 'ct-public-plan-featured': plan.featured }"
              :aria-label="`Plano ${plan.name}`"
            >
              <span v-if="plan.featured" class="ct-public-plan-badge">Recomendado</span>
              <h3>{{ plan.name }}</h3>
              <p class="ct-public-plan-price">
                <span class="mr-1 text-base font-normal tracking-normal text-slate-500">R$</span
                >{{ getPlanMonthlyPrice(plan, billingCycle) }}
              </p>
              <p class="mt-2 text-xs text-slate-500">por mês</p>
              <p class="mt-2 min-h-8 text-[11px] leading-5 text-slate-500">
                {{
                  plan.id === 'free'
                    ? 'Plano sem mensalidade'
                    : billingCycle === 'annual'
                      ? `R$ ${getPlanPrice(plan, billingCycle)} cobrados por ano`
                      : 'Cobrança mensal'
                }}
              </p>
              <p class="ct-public-plan-description">{{ plan.description }}</p>
              <ul class="ct-public-plan-features border-t border-[#edf1f7] pt-5">
                <li>
                  <span aria-hidden="true">✓</span><span>{{ plan.clients }} clientes</span>
                </li>
                <li>
                  <span aria-hidden="true">✓</span
                  ><span>{{ plan.users }}{{ plan.id === 'free' ? '' : ' usuários' }}</span>
                </li>
                <li v-for="feature in plan.features" :key="feature">
                  <span aria-hidden="true">✓</span><span>{{ feature }}</span>
                </li>
              </ul>
              <RouterLink
                :to="
                  plan.sales
                    ? { path: '/contato', query: { assunto: 'Plano Empresarial' } }
                    : {
                        path: '/cadastro',
                        query: plan.id === 'free' ? {} : { plano: plan.id, ciclo: billingCycle },
                      }
                "
                :class="plan.featured ? 'ct-button-primary' : 'ct-button-secondary'"
                >{{
                  plan.sales
                    ? 'Falar com vendas'
                    : plan.id === 'free'
                      ? 'Começar grátis'
                      : `Escolher ${plan.name}`
                }}</RouterLink
              >
            </article>
          </div>
        </div>
      </section>
      <section class="ct-public-section ct-public-section-soft">
        <div class="ct-container">
          <div class="ct-public-section-heading">
            <p class="ct-public-eyebrow">Compare com calma</p>
            <h2 class="ct-public-heading">O que muda em cada plano?</h2>
            <p class="ct-public-copy mt-4">
              Veja os limites de clientes, equipe e os recursos de análise disponíveis.
            </p>
          </div>
          <div class="overflow-x-auto rounded-xl border border-[#e5ecf7] bg-white">
            <table class="w-full min-w-[860px] text-left text-sm">
              <caption class="sr-only">
                Comparação dos recursos dos planos ContablyTask
              </caption>
              <thead class="bg-[#f5f8ff]">
                <tr>
                  <th scope="col" class="px-5 py-4 font-medium text-slate-500">Recurso</th>
                  <th
                    v-for="plan in plans"
                    :key="plan.id"
                    scope="col"
                    class="px-5 py-4 font-semibold"
                  >
                    {{ plan.name }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in comparison" :key="row.label" class="border-t border-[#edf1f7]">
                  <th scope="row" class="px-5 py-4 text-[13px] font-medium text-slate-600">
                    {{ row.label }}
                  </th>
                  <td
                    v-for="(value, index) in row.values"
                    :key="`${row.label}-${plans[index]?.id}`"
                    class="px-5 py-4 text-[13px]"
                    :class="value === 'Incluído' ? 'text-blue-600' : 'text-slate-500'"
                  >
                    {{ value }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <p class="mt-4 text-xs leading-6 text-slate-500">
            Os limites se aplicam aos clientes ativos e aos usuários cadastrados no escritório.
          </p>
        </div>
      </section>
      <section class="ct-public-section">
        <div class="ct-container grid gap-10 lg:grid-cols-[0.8fr_1.2fr] lg:gap-20">
          <div>
            <p class="ct-public-eyebrow">Dúvidas frequentes</p>
            <h2 class="ct-public-heading">Escolha com tranquilidade.</h2>
            <p class="ct-public-copy mt-5">
              Se precisar de ajuda para encontrar o plano certo, converse com nossa equipe.
            </p>
            <RouterLink to="/contato" class="ct-public-link mt-6"
              >Falar com a equipe <span aria-hidden="true">→</span></RouterLink
            >
          </div>
          <div class="ct-public-faq">
            <details v-for="item in faq" :key="item[0]">
              <summary>{{ item[0] }}</summary>
              <p>{{ item[1] }}</p>
            </details>
          </div>
        </div>
      </section>
      <PublicCallToAction />
    </div>
  </PublicLayout>
</template>
