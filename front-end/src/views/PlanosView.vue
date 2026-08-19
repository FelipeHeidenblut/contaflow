<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import PublicLayout from '@/components/PublicLayout.vue'
import { useScrollReveal } from '@/composables/useScrollReveal'
import { getPlanMonthlyPrice, getPlanPrice, plans, type BillingCycle } from '@/constants/plans'

const page = ref<HTMLElement | null>(null)
const billingCycle = ref<BillingCycle>('monthly')
useScrollReveal(page)

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
  ['Preciso de cartão para começar?', 'Não. O plano Gratuito não exige cartão nem pagamento.'],
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
    <div ref="page" class="ct-modern-landing overflow-hidden">
      <section class="relative border-b border-slate-200 bg-white">
        <div class="ct-engineering-grid pointer-events-none absolute inset-0 opacity-60"></div>
        <div
          class="ct-container relative grid items-center gap-12 py-16 lg:grid-cols-[0.9fr_1.1fr] lg:py-24"
        >
          <div data-reveal>
            <p class="ct-technical-label">Planos · capacidade sob medida</p>
            <h1 class="ct-modern-display mt-6">
              Comece pequeno.
              <span class="ct-gradient-text">Cresça sem refazer o processo.</span>
            </h1>
            <p class="mt-6 max-w-xl text-[17px] leading-7 text-slate-600">
              O fluxo principal acompanha todos os planos. A capacidade aumenta com a carteira, a
              equipe e a necessidade de análise do escritório.
            </p>
            <div
              class="mt-7 flex flex-wrap gap-x-5 gap-y-2 font-mono text-[10px] uppercase tracking-wider text-slate-500"
            >
              <span>✓ sem cartão no gratuito</span><span>✓ mensal ou anual</span
              ><span>✓ checkout protegido</span>
            </div>
          </div>

          <div data-reveal style="--reveal-delay: 120ms" class="relative mx-auto w-full max-w-xl">
            <div
              class="absolute -inset-5 rounded-[28px] border border-blue-100 bg-blue-50/50 [transform:rotate(1deg)]"
            ></div>
            <div
              class="relative overflow-hidden rounded-2xl border border-slate-300 bg-white p-6 shadow-[0_28px_80px_rgba(15,23,42,0.13)] sm:p-8"
            >
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-semibold text-[#101a38]">
                    Capacidade que acompanha a operação
                  </p>
                  <p class="mt-1 font-mono text-[9px] uppercase tracking-wider text-slate-400">
                    clientes · equipe · análise
                  </p>
                </div>
                <span class="h-2.5 w-2.5 rounded-full bg-emerald-500 ring-4 ring-emerald-50"></span>
              </div>
              <div class="mt-8 space-y-5">
                <div
                  v-for="(plan, index) in plans"
                  :key="plan.id"
                  class="grid grid-cols-[86px_1fr_auto] items-center gap-3"
                >
                  <span class="text-xs font-semibold text-slate-600">{{ plan.name }}</span>
                  <div class="h-3 overflow-hidden rounded-full bg-slate-100">
                    <div
                      class="h-full rounded-full"
                      :class="
                        plan.featured
                          ? 'bg-blue-600'
                          : index === plans.length - 1
                            ? 'bg-[var(--ct-navy)]'
                            : 'bg-blue-300'
                      "
                      :style="{ width: `${Math.min(100, 20 + index * 20)}%` }"
                    ></div>
                  </div>
                  <span class="font-mono text-[9px] text-slate-400">{{
                    index === plans.length - 1 ? '∞' : plan.clients.replace('Até ', '')
                  }}</span>
                </div>
              </div>
              <div class="mt-8 grid grid-cols-3 gap-2 border-t border-slate-100 pt-5 text-center">
                <div>
                  <p class="font-mono text-lg font-semibold text-blue-600">{{ plans.length }}</p>
                  <p class="mt-1 text-[9px] text-slate-400">opções</p>
                </div>
                <div>
                  <p class="font-mono text-lg font-semibold text-blue-600">R$ 0</p>
                  <p class="mt-1 text-[9px] text-slate-400">para começar</p>
                </div>
                <div>
                  <p class="font-mono text-lg font-semibold text-blue-600">2</p>
                  <p class="mt-1 text-[9px] text-slate-400">ciclos de cobrança</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="bg-[#f8fafc] py-16 lg:py-24">
        <div class="ct-container">
          <div data-reveal class="flex flex-col justify-between gap-6 lg:flex-row lg:items-end">
            <div>
              <p class="ct-technical-label">Escolha sua capacidade</p>
              <h2 class="ct-modern-section-title mt-5">Um plano para cada fase do escritório.</h2>
            </div>
            <p class="max-w-xl text-sm leading-7 text-slate-600">
              Compare os limites e escolha entre pagamento mensal ou anual. No ciclo anual, o valor
              total é cobrado uma vez por ano.
            </p>
          </div>

          <div data-reveal class="mt-8 flex justify-center">
            <div class="inline-flex rounded-xl border border-slate-200 bg-white p-1 shadow-sm">
              <button
                type="button"
                class="rounded-lg px-5 py-2.5 text-sm font-semibold transition-colors"
                :class="billingCycle === 'monthly' ? 'bg-blue-600 text-white' : 'text-slate-500'"
                @click="billingCycle = 'monthly'"
              >
                Mensal
              </button>
              <button
                type="button"
                class="rounded-lg px-5 py-2.5 text-sm font-semibold transition-colors"
                :class="billingCycle === 'annual' ? 'bg-blue-600 text-white' : 'text-slate-500'"
                @click="billingCycle = 'annual'"
              >
                Anual <span class="ml-1 text-[10px] opacity-80">economize 2 meses</span>
              </button>
            </div>
          </div>

          <div class="mt-12 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
            <article
              v-for="(plan, index) in plans"
              :key="plan.id"
              data-reveal
              class="group relative flex min-h-[570px] flex-col overflow-hidden rounded-2xl border p-6 transition-all duration-200 hover:-translate-y-1 hover:shadow-[0_16px_38px_rgba(15,23,42,0.08)]"
              :class="
                plan.featured
                  ? 'border-blue-500 bg-[var(--ct-navy)] text-white shadow-xl shadow-blue-950/10'
                  : 'border-slate-200 bg-white'
              "
              :style="{ '--reveal-delay': `${index * 70}ms` }"
            >
              <div class="flex items-center justify-between">
                <span
                  class="font-mono text-[10px] uppercase tracking-[0.12em]"
                  :class="plan.featured ? 'text-blue-300' : 'text-blue-600'"
                  >{{ plan.name }}</span
                ><span
                  v-if="plan.featured"
                  class="rounded-full border border-white/15 bg-white/5 px-2.5 py-1 font-mono text-[8px] uppercase tracking-wider text-blue-200"
                  >recomendado</span
                >
              </div>
              <div class="mt-7 flex items-end gap-1">
                <span
                  class="mb-1 text-sm"
                  :class="plan.featured ? 'text-white/45' : 'text-slate-400'"
                  >R$</span
                ><span class="text-[42px] font-semibold leading-none tracking-[-0.055em]">{{
                  getPlanMonthlyPrice(plan, billingCycle)
                }}</span>
              </div>
              <p
                class="mt-2 font-mono text-[9px] uppercase tracking-wider"
                :class="plan.featured ? 'text-white/40' : 'text-slate-400'"
              >
                por mês
              </p>
              <p
                v-if="billingCycle === 'annual' && plan.id !== 'free'"
                class="mt-1 text-xs"
                :class="plan.featured ? 'text-white/50' : 'text-slate-500'"
              >
                R$ {{ getPlanPrice(plan, billingCycle) }} cobrados por ano
              </p>
              <p
                class="mt-5 min-h-[66px] text-sm leading-6"
                :class="plan.featured ? 'text-white/60' : 'text-slate-600'"
              >
                {{ plan.description }}
              </p>
              <div
                class="my-6 border-t"
                :class="plan.featured ? 'border-white/10' : 'border-slate-100'"
              ></div>
              <ul class="flex-1 space-y-3.5">
                <li class="flex gap-2.5 text-sm">
                  <span :class="plan.featured ? 'text-blue-300' : 'text-blue-600'">✓</span
                  >{{ plan.clients }} clientes
                </li>
                <li class="flex gap-2.5 text-sm">
                  <span :class="plan.featured ? 'text-blue-300' : 'text-blue-600'">✓</span
                  >{{ plan.users }}
                </li>
                <li
                  v-if="plan.id === 'profissional'"
                  class="rounded-lg border border-blue-300/20 bg-blue-400/10 px-3 py-2 font-mono text-[9px] uppercase tracking-wider text-blue-200"
                >
                  25% menor custo por cliente que o Essencial
                </li>
                <li
                  v-for="feature in plan.features"
                  :key="feature"
                  class="flex gap-2.5 text-[13px]"
                  :class="plan.featured ? 'text-white/70' : 'text-slate-600'"
                >
                  <span :class="plan.featured ? 'text-blue-300' : 'text-blue-600'">✓</span
                  >{{ feature }}
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
                class="mt-7 inline-flex min-h-12 items-center justify-center rounded-xl px-4 text-sm font-semibold transition-colors"
                :class="
                  plan.featured
                    ? 'bg-white text-[var(--ct-navy)] hover:bg-blue-50'
                    : 'border border-slate-200 bg-white text-[#101a38] hover:border-blue-300 hover:text-blue-700'
                "
                >{{
                  plan.sales
                    ? 'Falar com vendas'
                    : plan.id === 'free'
                      ? 'Começar grátis'
                      : `Escolher ${plan.name}`
                }}
                <span class="ml-2">→</span></RouterLink
              >
            </article>
          </div>
        </div>
      </section>

      <section class="px-3 pb-3 sm:px-4 sm:pb-4">
        <div class="relative overflow-hidden rounded-[28px] bg-[var(--ct-navy)] py-16 text-white">
          <div
            class="ct-engineering-grid-dark pointer-events-none absolute inset-0 opacity-50"
          ></div>
          <div
            class="ct-container relative grid gap-8 md:grid-cols-3 md:divide-x md:divide-white/10"
          >
            <div data-reveal class="px-4">
              <p class="font-mono text-[10px] uppercase tracking-wider text-blue-300">
                Renovação transparente
              </p>
              <p class="mt-3 text-xl font-semibold">Você controla a renovação</p>
              <p class="mt-2 text-sm text-white/50">Escolha o ciclo que combina com a operação.</p>
            </div>
            <div data-reveal style="--reveal-delay: 70ms" class="px-4">
              <p class="font-mono text-[10px] uppercase tracking-wider text-blue-300">
                Pagamento seguro
              </p>
              <p class="mt-3 text-xl font-semibold">Checkout protegido</p>
              <p class="mt-2 text-sm text-white/50">PIX, boleto ou cartão fora da aplicação.</p>
            </div>
            <div data-reveal style="--reveal-delay: 140ms" class="px-4">
              <p class="font-mono text-[10px] uppercase tracking-wider text-blue-300">
                Seus dados permanecem
              </p>
              <p class="mt-3 text-xl font-semibold">Upgrade sem recomeçar</p>
              <p class="mt-2 text-sm text-white/50">
                A carteira e a rotina continuam no mesmo ambiente.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section class="bg-white py-20 lg:py-28">
        <div class="ct-container">
          <div data-reveal class="max-w-3xl">
            <p class="ct-technical-label">Comparação</p>
            <h2 class="ct-modern-section-title mt-5">Veja exatamente o que muda.</h2>
          </div>
          <div data-reveal class="mt-10 overflow-x-auto rounded-2xl border border-slate-200">
            <table class="min-w-[1040px] w-full border-collapse text-left text-sm">
              <thead class="bg-slate-50">
                <tr>
                  <th
                    class="px-5 py-4 font-mono text-[10px] uppercase tracking-wider text-slate-500"
                  >
                    Recurso
                  </th>
                  <th
                    v-for="plan in plans"
                    :key="plan.id"
                    class="px-5 py-4 font-semibold text-[#101a38]"
                  >
                    {{ plan.name }}
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200">
                <tr v-for="row in comparison" :key="row.label" class="hover:bg-slate-50/70">
                  <th class="px-5 py-4 font-medium text-[#26344f]">{{ row.label }}</th>
                  <td
                    v-for="(value, index) in row.values"
                    :key="`${row.label}-${plans[index]?.id}`"
                    class="px-5 py-4"
                    :class="value === 'Incluído' ? 'font-medium text-blue-700' : 'text-slate-500'"
                  >
                    {{ value }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <p class="mt-4 font-mono text-[9px] uppercase tracking-wider text-slate-400">
            Limites aplicados a clientes ativos e usuários cadastrados · ciclo selecionado:
            {{ billingCycle === 'annual' ? 'anual' : 'mensal' }}
          </p>
        </div>
      </section>

      <section class="border-t border-slate-200 bg-[#f8fafc] py-20 lg:py-28">
        <div class="ct-container grid gap-12 lg:grid-cols-[0.7fr_1.3fr]">
          <div data-reveal>
            <p class="ct-technical-label">Dúvidas frequentes</p>
            <h2 class="ct-modern-section-title mt-5">Antes de escolher.</h2>
            <p class="mt-5 max-w-sm text-sm leading-7 text-slate-600">
              Se ainda precisar conversar, nossa equipe responde sobre implantação e plano.
            </p>
            <RouterLink to="/contato" class="ct-link-arrow mt-6"
              >Falar com a equipe <span>→</span></RouterLink
            >
          </div>
          <dl class="border-t border-slate-200">
            <div
              v-for="(item, index) in faq"
              :key="item[0]"
              data-reveal
              class="grid gap-3 border-b border-slate-200 py-6 sm:grid-cols-[2rem_1fr]"
            >
              <span class="font-mono text-[10px] text-blue-600">0{{ index + 1 }}</span>
              <div>
                <dt class="font-semibold text-[#101a38]">{{ item[0] }}</dt>
                <dd class="mt-2 text-sm leading-6 text-slate-600">{{ item[1] }}</dd>
              </div>
            </div>
          </dl>
        </div>
      </section>
    </div>
  </PublicLayout>
</template>
