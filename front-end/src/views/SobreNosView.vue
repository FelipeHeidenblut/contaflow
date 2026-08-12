<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import PublicLayout from '@/components/PublicLayout.vue'
import { useScrollReveal } from '@/composables/useScrollReveal'

const page = ref<HTMLElement | null>(null)
useScrollReveal(page)

const principles = [
  {
    title: 'Clareza antes de complexidade',
    description:
      'Cada tela deve ajudar o usuário a decidir o próximo passo sem exigir treinamento extenso.',
    meta: 'produto · decisão',
  },
  {
    title: 'Processo antes de improviso',
    description:
      'A tecnologia precisa sustentar uma rotina consistente, não criar mais uma tarefa para a equipe.',
    meta: 'operação · consistência',
  },
  {
    title: 'Evolução com o escritório',
    description:
      'O produto começa simples e acompanha o crescimento da carteira, da equipe e da operação.',
    meta: 'escala · continuidade',
  },
]
</script>

<template>
  <PublicLayout>
    <div ref="page" class="ct-modern-landing overflow-hidden">
      <section class="relative border-b border-slate-200 bg-white">
        <div class="ct-engineering-grid pointer-events-none absolute inset-0 opacity-60"></div>
        <div
          class="ct-container relative grid min-h-[650px] items-center gap-14 py-16 lg:grid-cols-[1fr_0.9fr] lg:py-20"
        >
          <div data-reveal>
            <p class="ct-technical-label">Sobre a ContablyTask</p>
            <h1 class="ct-modern-display mt-6">
              Software contábil deve
              <span class="ct-gradient-text">reduzir ruído.</span>
            </h1>
            <p class="mt-6 max-w-xl text-[17px] leading-7 text-slate-600">
              Criamos uma base operacional comum para escritórios que ainda precisam conciliar
              planilhas, mensagens, pastas e memória para entregar no prazo.
            </p>
          </div>

          <div data-reveal style="--reveal-delay: 120ms" class="relative mx-auto w-full max-w-lg">
            <div
              class="absolute -inset-5 rounded-[28px] border border-blue-100 bg-blue-50/50 [transform:rotate(-1deg)]"
            ></div>
            <div
              class="relative overflow-hidden rounded-2xl border border-slate-300 bg-white p-6 shadow-[0_28px_80px_rgba(15,23,42,0.13)] sm:p-8"
            >
              <div class="flex items-center justify-between">
                <p class="font-mono text-[9px] uppercase tracking-[0.12em] text-slate-400">
                  uma fonte operacional
                </p>
                <span class="h-2.5 w-2.5 rounded-full bg-emerald-500 ring-4 ring-emerald-50"></span>
              </div>
              <svg
                viewBox="0 0 500 330"
                class="mt-5 w-full"
                aria-label="Clientes, tarefas, equipe e documentos ligados ao ContablyTask"
              >
                <g fill="white" stroke="#cbd5e1" stroke-width="1.5">
                  <rect x="22" y="30" width="122" height="52" rx="12" />
                  <rect x="22" y="244" width="122" height="52" rx="12" />
                  <rect x="356" y="30" width="122" height="52" rx="12" />
                  <rect x="356" y="244" width="122" height="52" rx="12" />
                </g>
                <g fill="#475569" font-family="ui-monospace" font-size="11">
                  <text x="83" y="61" text-anchor="middle">CLIENTES</text>
                  <text x="83" y="275" text-anchor="middle">DOCUMENTOS</text>
                  <text x="417" y="61" text-anchor="middle">PRAZOS</text>
                  <text x="417" y="275" text-anchor="middle">EQUIPE</text>
                </g>
                <g fill="none" stroke="#2563eb" stroke-width="2">
                  <path d="M144 56 C210 56 175 135 220 145" />
                  <path d="M144 270 C210 270 175 192 220 182" />
                  <path d="M356 56 C290 56 325 135 280 145" />
                  <path d="M356 270 C290 270 325 192 280 182" />
                </g>
                <circle cx="250" cy="164" r="74" fill="#172554" />
                <circle
                  cx="250"
                  cy="164"
                  r="58"
                  fill="none"
                  stroke="#3b82f6"
                  stroke-opacity=".45"
                />
                <path
                  d="M224 164l17 17 36-39"
                  fill="none"
                  stroke="#93c5fd"
                  stroke-width="5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
                <text
                  x="250"
                  y="217"
                  text-anchor="middle"
                  fill="#bfdbfe"
                  font-family="ui-monospace"
                  font-size="9"
                >
                  CONTABLYTASK
                </text>
                <g fill="#2563eb">
                  <circle cx="160" cy="66" r="4" />
                  <circle cx="160" cy="260" r="4" />
                  <circle cx="340" cy="66" r="4" />
                  <circle cx="340" cy="260" r="4" />
                </g>
              </svg>
              <p
                class="border-t border-slate-100 pt-4 text-center text-xs font-medium text-slate-500"
              >
                A complexidade permanece conectada, não espalhada.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section class="border-b border-slate-200 bg-white">
        <div class="ct-container grid py-2 md:grid-cols-3 md:divide-x md:divide-slate-200">
          <div class="px-5 py-6">
            <p class="font-mono text-[9px] uppercase tracking-wider text-blue-600">problema</p>
            <p class="mt-2 text-sm font-semibold text-[#101a38]">Informação espalhada</p>
          </div>
          <div class="border-t border-slate-200 px-5 py-6 md:border-t-0">
            <p class="font-mono text-[9px] uppercase tracking-wider text-blue-600">produto</p>
            <p class="mt-2 text-sm font-semibold text-[#101a38]">Contexto compartilhado</p>
          </div>
          <div class="border-t border-slate-200 px-5 py-6 md:border-t-0">
            <p class="font-mono text-[9px] uppercase tracking-wider text-blue-600">resultado</p>
            <p class="mt-2 text-sm font-semibold text-[#101a38]">Próximo passo visível</p>
          </div>
        </div>
      </section>

      <section class="bg-[#f8fafc] py-20 lg:py-28">
        <div class="ct-container grid gap-12 lg:grid-cols-[0.65fr_1.35fr]">
          <div data-reveal class="lg:sticky lg:top-28 lg:self-start">
            <p class="ct-technical-label">Por que existimos</p>
            <h2 class="ct-modern-section-title mt-5">A operação cresce antes do processo.</h2>
          </div>
          <div class="space-y-4">
            <article data-reveal class="rounded-2xl border border-slate-200 bg-white p-7 sm:p-9">
              <span class="font-mono text-[10px] uppercase tracking-wider text-blue-600"
                >01 · o ruído</span
              >
              <h3 class="mt-5 text-2xl font-semibold tracking-[-0.03em] text-[#101a38]">
                A informação certa existe, mas está em lugares diferentes.
              </h3>
              <p class="mt-4 text-[15px] leading-7 text-slate-600">
                Quando a carteira aumenta, tarefas passam a depender de planilhas paralelas,
                conversas no WhatsApp e conhecimento concentrado em poucas pessoas. O risco não é
                apenas esquecer uma atividade: é descobrir tarde demais.
              </p>
            </article>
            <article
              data-reveal
              class="rounded-2xl border border-blue-900 bg-[var(--ct-navy)] p-7 text-white sm:p-9"
            >
              <span class="font-mono text-[10px] uppercase tracking-wider text-blue-300"
                >02 · a base</span
              >
              <h3 class="mt-5 text-2xl font-semibold tracking-[-0.03em]">
                Cada cliente, obrigação e arquivo precisa continuar conectado.
              </h3>
              <p class="mt-4 text-[15px] leading-7 text-white/60">
                A ContablyTask cria essa base operacional: cada cliente tem contexto, cada obrigação
                tem responsável e prazo, e cada documento pode ser encontrado dentro do mesmo fluxo.
              </p>
              <div class="mt-8 grid grid-cols-3 gap-2">
                <div class="rounded-xl border border-white/10 bg-white/[0.04] p-3">
                  <p class="font-mono text-lg text-blue-200">01</p>
                  <p class="mt-1 text-[10px] text-white/40">carteira</p>
                </div>
                <div class="rounded-xl border border-white/10 bg-white/[0.04] p-3">
                  <p class="font-mono text-lg text-blue-200">02</p>
                  <p class="mt-1 text-[10px] text-white/40">execução</p>
                </div>
                <div class="rounded-xl border border-white/10 bg-white/[0.04] p-3">
                  <p class="font-mono text-lg text-blue-200">03</p>
                  <p class="mt-1 text-[10px] text-white/40">controle</p>
                </div>
              </div>
            </article>
          </div>
        </div>
      </section>

      <section class="bg-white py-20 lg:py-28">
        <div class="ct-container">
          <div data-reveal class="max-w-3xl">
            <p class="ct-technical-label">Como pensamos</p>
            <h2 class="ct-modern-section-title mt-5">Princípios que aparecem no produto.</h2>
          </div>
          <div
            class="mt-12 grid gap-px overflow-hidden rounded-2xl border border-slate-200 bg-slate-200 md:grid-cols-3"
          >
            <article
              v-for="(item, index) in principles"
              :key="item.title"
              data-reveal
              class="flex min-h-[320px] flex-col bg-white p-7"
              :style="{ '--reveal-delay': `${index * 80}ms` }"
            >
              <span class="font-mono text-[11px] tracking-[0.12em] text-blue-600"
                >0{{ index + 1 }}</span
              >
              <h3 class="mt-8 text-xl font-semibold tracking-[-0.025em] text-[#101a38]">
                {{ item.title }}
              </h3>
              <p class="mt-3 text-sm leading-6 text-slate-600">{{ item.description }}</p>
              <div
                class="mt-auto border-t border-slate-100 pt-5 font-mono text-[9px] uppercase tracking-wider text-slate-400"
              >
                {{ item.meta }}
              </div>
            </article>
          </div>
        </div>
      </section>

      <section class="px-3 pb-3 sm:px-4 sm:pb-4">
        <div class="relative overflow-hidden rounded-[28px] bg-[var(--ct-navy)] py-20 text-white">
          <div
            class="ct-engineering-grid-dark pointer-events-none absolute inset-0 opacity-50"
          ></div>
          <div
            data-reveal
            class="ct-container relative flex flex-col justify-between gap-8 md:flex-row md:items-end"
          >
            <div>
              <p class="ct-technical-label border-white/15 bg-white/5 text-blue-200">
                Conheça na prática
              </p>
              <h2
                class="mt-6 max-w-3xl text-[clamp(2.25rem,4vw,3.75rem)] font-semibold leading-[1.03] tracking-[-0.05em]"
              >
                A próxima rotina mensal pode começar em um único lugar.
              </h2>
              <p class="mt-4 text-sm text-white/60">
                Até cinco clientes, sem cartão e sem fidelidade.
              </p>
            </div>
            <RouterLink to="/cadastro" class="ct-button-primary ct-landing-primary shrink-0"
              >Criar conta <span>→</span></RouterLink
            >
          </div>
        </div>
      </section>
    </div>
  </PublicLayout>
</template>
