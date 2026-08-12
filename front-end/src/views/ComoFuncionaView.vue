<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import PublicLayout from '@/components/PublicLayout.vue'
import { useScrollReveal } from '@/composables/useScrollReveal'

const page = ref<HTMLElement | null>(null)
useScrollReveal(page)

const steps = [
  {
    number: '01',
    title: 'Clientes',
    description:
      'Cadastre manualmente ou importe sua carteira para reunir dados fiscais e operacionais.',
    output: 'Carteira pronta',
    icon: 'clients',
  },
  {
    number: '02',
    title: 'Obrigações',
    description: 'Defina vencimento, importância, responsável e recorrência para cada demanda.',
    output: 'Rotina planejada',
    icon: 'tasks',
  },
  {
    number: '03',
    title: 'Execução',
    description:
      'A equipe atualiza o andamento e sinaliza quando depende de informação do cliente.',
    output: 'Trabalho visível',
    icon: 'execution',
  },
  {
    number: '04',
    title: 'Controle',
    description: 'Dashboard, calendário e relatórios mostram prioridades, atrasos e resultados.',
    output: 'Decisão clara',
    icon: 'control',
  },
]

const features = [
  {
    label: 'Calendário',
    title: 'Prazos dentro e fora da plataforma',
    description: 'Sincronize vencimentos com Google Agenda e Outlook por um link seguro.',
    meta: 'feed · compartilhável',
  },
  {
    label: 'Documentos',
    title: 'O arquivo continua ligado ao contexto',
    description: 'Encontre documentos fiscais, contábeis e operacionais pelo cliente certo.',
    meta: 'arquivo · até 5 MB',
  },
  {
    label: 'Equipe',
    title: 'Responsabilidade sem depender de cobrança',
    description: 'Saiba quem cuida de cada entrega e como o trabalho está distribuído.',
    meta: 'carga · responsável',
  },
]
</script>

<template>
  <PublicLayout>
    <div ref="page" class="ct-modern-landing overflow-hidden">
      <section class="relative border-b border-slate-200 bg-white">
        <div class="ct-engineering-grid pointer-events-none absolute inset-0 opacity-60"></div>
        <div
          class="ct-container relative grid min-h-[650px] items-center gap-14 py-16 lg:grid-cols-[0.82fr_1.18fr] lg:py-20"
        >
          <div data-reveal>
            <p class="ct-technical-label">Produto · fluxo operacional</p>
            <h1 class="ct-modern-display mt-6">
              Do cliente cadastrado à
              <span class="ct-gradient-text">obrigação entregue.</span>
            </h1>
            <p class="mt-6 max-w-xl text-[17px] leading-7 text-slate-600">
              Um fluxo direto que acompanha a operação real do escritório, sem exigir implantação
              longa ou um processo artificial para funcionar.
            </p>
            <div class="mt-8 flex flex-col gap-3 sm:flex-row">
              <RouterLink to="/cadastro" class="ct-button-primary ct-landing-primary">
                Começar grátis <span>→</span>
              </RouterLink>
              <a href="#fluxo" class="ct-button-secondary ct-landing-secondary">Ver o fluxo</a>
            </div>
          </div>

          <div data-reveal style="--reveal-delay: 120ms" class="relative">
            <div
              class="absolute -inset-5 rounded-[28px] border border-blue-100 bg-blue-50/50 [transform:rotate(-1deg)]"
            ></div>
            <div
              class="relative overflow-hidden rounded-2xl border border-slate-300 bg-[#fbfcfe] shadow-[0_28px_80px_rgba(15,23,42,0.14)]"
            >
              <div
                class="flex items-center justify-between border-b border-slate-200 bg-white px-5 py-4"
              >
                <div>
                  <p class="text-xs font-semibold text-[#101a38]">Fluxo de uma obrigação</p>
                  <p class="mt-1 font-mono text-[9px] uppercase tracking-wider text-slate-400">
                    Grupo Horizonte · competência atual
                  </p>
                </div>
                <span
                  class="rounded-full border border-blue-100 bg-blue-50 px-2.5 py-1 text-[9px] font-semibold text-blue-700"
                  >Em andamento</span
                >
              </div>

              <div class="p-5 sm:p-6">
                <div
                  class="mb-5 grid grid-cols-2 gap-2 rounded-xl border border-slate-200 bg-white p-3 sm:grid-cols-4"
                >
                  <div>
                    <p class="font-mono text-[8px] uppercase text-slate-400">Cliente</p>
                    <p class="mt-1 truncate text-[10px] font-semibold">Grupo Horizonte</p>
                  </div>
                  <div>
                    <p class="font-mono text-[8px] uppercase text-slate-400">Responsável</p>
                    <p class="mt-1 text-[10px] font-semibold">Ana Costa</p>
                  </div>
                  <div>
                    <p class="font-mono text-[8px] uppercase text-slate-400">Prazo</p>
                    <p class="mt-1 text-[10px] font-semibold">21 de agosto</p>
                  </div>
                  <div>
                    <p class="font-mono text-[8px] uppercase text-slate-400">Prioridade</p>
                    <p class="mt-1 text-[10px] font-semibold text-amber-600">Alta</p>
                  </div>
                </div>

                <ol
                  class="relative space-y-0 before:absolute before:bottom-6 before:left-3 before:top-6 before:w-px before:bg-slate-200"
                >
                  <li
                    v-for="(step, index) in [
                      'Cliente cadastrado',
                      'DCTFWeb criada',
                      'Execução pela equipe',
                      'Entrega e histórico',
                    ]"
                    :key="step"
                    class="relative grid grid-cols-[1.5rem_1fr_auto] items-center gap-3 border-b border-slate-100 py-4 last:border-0"
                  >
                    <span
                      class="z-10 flex h-6 w-6 items-center justify-center rounded-full border text-[9px] font-bold"
                      :class="
                        index < 2
                          ? 'border-emerald-100 bg-emerald-50 text-emerald-700'
                          : index === 2
                            ? 'border-blue-600 bg-blue-600 text-white ring-4 ring-blue-50'
                            : 'border-slate-200 bg-white text-slate-400'
                      "
                      >{{ index < 2 ? '✓' : index + 1 }}</span
                    >
                    <div>
                      <p class="text-[11px] font-semibold text-[#26344f]">{{ step }}</p>
                      <p class="mt-1 text-[9px] text-slate-400">
                        {{
                          index === 0
                            ? 'Dados e regime tributário centralizados'
                            : index === 1
                              ? 'Prazo, importância e recorrência definidos'
                              : index === 2
                                ? 'Responsável atualiza o andamento'
                                : 'Conclusão permanece no histórico'
                        }}
                      </p>
                    </div>
                    <span
                      class="font-mono text-[8px] uppercase"
                      :class="
                        index < 2
                          ? 'text-emerald-600'
                          : index === 2
                            ? 'text-blue-600'
                            : 'text-slate-400'
                      "
                      >{{ index < 2 ? 'concluído' : index === 2 ? 'agora' : 'próxima' }}</span
                    >
                  </li>
                </ol>
              </div>
              <div class="grid grid-cols-2 border-t border-slate-200 bg-white">
                <div class="border-r border-slate-200 px-5 py-3">
                  <span class="font-mono text-[8px] uppercase text-slate-400">Documentos</span
                  ><strong class="ml-2 text-[10px]">4 anexos</strong>
                </div>
                <div class="px-5 py-3">
                  <span class="font-mono text-[8px] uppercase text-slate-400">Atualização</span
                  ><strong class="ml-2 text-[10px]">há 12 min</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="border-b border-slate-200 bg-white">
        <div class="ct-container grid py-2 sm:grid-cols-3 sm:divide-x sm:divide-slate-200">
          <div class="px-4 py-5 text-center">
            <p class="font-mono text-[10px] uppercase tracking-wider text-blue-600">entrada</p>
            <p class="mt-2 text-sm font-semibold">Cadastro ou importação</p>
          </div>
          <div class="border-t border-slate-200 px-4 py-5 text-center sm:border-t-0">
            <p class="font-mono text-[10px] uppercase tracking-wider text-blue-600">execução</p>
            <p class="mt-2 text-sm font-semibold">Responsável e status visíveis</p>
          </div>
          <div class="border-t border-slate-200 px-4 py-5 text-center sm:border-t-0">
            <p class="font-mono text-[10px] uppercase tracking-wider text-blue-600">resultado</p>
            <p class="mt-2 text-sm font-semibold">Histórico e relatório</p>
          </div>
        </div>
      </section>

      <section id="fluxo" class="scroll-mt-24 bg-[#f8fafc] py-20 lg:py-28">
        <div class="ct-container grid gap-12 lg:grid-cols-[0.65fr_1.35fr]">
          <div data-reveal class="lg:sticky lg:top-28 lg:self-start">
            <p class="ct-technical-label">Fluxo principal</p>
            <h2 class="ct-modern-section-title mt-5">Quatro etapas, um só contexto.</h2>
            <p class="mt-5 max-w-md text-sm leading-7 text-slate-600">
              Cada etapa termina com um resultado que já prepara a seguinte. Nada precisa ser
              reconstruído em outra ferramenta.
            </p>
          </div>
          <div class="grid gap-4 md:grid-cols-2">
            <article
              v-for="(step, index) in steps"
              :key="step.number"
              data-reveal
              class="ct-capability-card flex min-h-[290px] flex-col"
              :style="{ '--reveal-delay': `${(index % 2) * 80}ms` }"
            >
              <div class="flex items-center justify-between">
                <span class="font-mono text-[11px] tracking-[0.12em] text-blue-600"
                  >PASSO {{ step.number }}</span
                ><span
                  class="rounded-full border border-slate-200 px-3 py-1 font-mono text-[8px] uppercase tracking-wider text-slate-400"
                  >{{ step.output }}</span
                >
              </div>
              <h3 class="mt-7 text-2xl font-semibold tracking-[-0.03em] text-[#101a38]">
                {{ step.title }}
              </h3>
              <p class="mt-3 text-sm leading-6 text-slate-600">{{ step.description }}</p>
              <div class="mt-auto pt-8">
                <div class="flex items-center gap-2">
                  <span class="h-2 w-2 rounded-full bg-blue-500"></span>
                  <div class="h-px flex-1 bg-gradient-to-r from-blue-400 to-slate-100"></div>
                  <span class="font-mono text-[9px] uppercase text-slate-400">{{ step.icon }}</span>
                </div>
              </div>
            </article>
          </div>
        </div>
      </section>

      <section class="bg-white py-20 lg:py-28">
        <div class="ct-container">
          <div data-reveal class="max-w-3xl">
            <p class="ct-technical-label">No dia a dia</p>
            <h2 class="ct-modern-section-title mt-5">
              Recursos discretos até o momento em que você precisa deles.
            </h2>
          </div>
          <div
            class="mt-12 grid gap-px overflow-hidden rounded-2xl border border-slate-200 bg-slate-200 md:grid-cols-3"
          >
            <article
              v-for="(feature, index) in features"
              :key="feature.title"
              data-reveal
              class="flex min-h-[300px] flex-col bg-white p-7"
              :style="{ '--reveal-delay': `${index * 80}ms` }"
            >
              <p class="font-mono text-[10px] uppercase tracking-[0.12em] text-blue-600">
                {{ feature.label }}
              </p>
              <h3 class="mt-6 text-xl font-semibold tracking-[-0.025em] text-[#101a38]">
                {{ feature.title }}
              </h3>
              <p class="mt-3 text-sm leading-6 text-slate-600">{{ feature.description }}</p>
              <div
                class="mt-auto border-t border-slate-100 pt-5 font-mono text-[9px] uppercase tracking-wider text-slate-400"
              >
                {{ feature.meta }}
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
                Próximo passo
              </p>
              <h2
                class="mt-6 max-w-3xl text-[clamp(2.25rem,4vw,3.75rem)] font-semibold leading-[1.03] tracking-[-0.05em]"
              >
                Veja o fluxo funcionando com a rotina do seu escritório.
              </h2>
              <p class="mt-4 text-sm text-white/60">
                Comece com até cinco clientes no plano gratuito.
              </p>
            </div>
            <div class="flex shrink-0 flex-col gap-3 sm:flex-row">
              <RouterLink to="/planos" class="ct-button-secondary ct-landing-secondary"
                >Ver planos</RouterLink
              ><RouterLink to="/cadastro" class="ct-button-primary ct-landing-primary"
                >Criar conta <span>→</span></RouterLink
              >
            </div>
          </div>
        </div>
      </section>
    </div>
  </PublicLayout>
</template>
