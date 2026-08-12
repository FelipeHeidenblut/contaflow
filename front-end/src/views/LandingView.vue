<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import PublicLayout from '@/components/PublicLayout.vue'
import { useScrollReveal } from '@/composables/useScrollReveal'

const page = ref<HTMLElement | null>(null)
useScrollReveal(page)

const proofPoints = [
  { value: '5', label: 'clientes no plano gratuito', detail: 'Comece sem cartão' },
  { value: '5 MB', label: 'por documento', detail: 'Arquivos ligados ao cliente' },
  { value: '12 meses', label: 'por relatório', detail: 'Visão consolidada nos planos pagos' },
]

const capabilities = [
  {
    number: '01',
    title: 'Carteira com contexto',
    description: 'Dados cadastrais, documentos e histórico permanecem ligados ao cliente certo.',
    meta: 'cliente · visão única',
    icon: 'client',
  },
  {
    number: '02',
    title: 'Prazos que pedem atenção',
    description: 'A equipe enxerga o que vence hoje, o que atrasou e o que depende do cliente.',
    meta: 'obrigação · ao vivo',
    icon: 'deadline',
  },
  {
    number: '03',
    title: 'Trabalho bem distribuído',
    description: 'Responsáveis, prioridades e carga da equipe aparecem antes do gargalo acontecer.',
    meta: 'equipe · capacidade',
    icon: 'team',
  },
  {
    number: '04',
    title: 'Decisão com o mês inteiro à vista',
    description:
      'Relatórios transformam tarefas, clientes e atrasos em uma leitura operacional clara.',
    meta: 'relatório · planos pagos',
    icon: 'report',
  },
]

const workflow = [
  {
    number: '01',
    title: 'Cadastre',
    description: 'Importe a carteira e reúna os dados essenciais de cada cliente.',
    meta: 'carteira · entrada',
  },
  {
    number: '02',
    title: 'Planeje',
    description: 'Defina obrigações, vencimentos, recorrências e responsáveis.',
    meta: 'rotina · organização',
  },
  {
    number: '03',
    title: 'Execute',
    description: 'Acompanhe pendências, documentos e retornos do cliente.',
    meta: 'equipe · em andamento',
  },
  {
    number: '04',
    title: 'Comprove',
    description: 'Consulte o histórico e transforme a operação em relatório.',
    meta: 'resultado · visível',
  },
]

const comparison = [
  ['Obrigação recorrente', 'Copiar linha no próximo mês', 'Próxima ocorrência criada no fluxo'],
  ['Documento recebido', 'Procurar em pasta ou conversa', 'Arquivo ligado ao cliente e à tarefa'],
  ['Prazo em risco', 'Descobrir durante a cobrança', 'Alerta visível antes da reunião'],
  ['Carga da equipe', 'Perguntar quem está disponível', 'Distribuição reunida no dashboard'],
]

const trustPoints = [
  {
    title: 'Cada escritório no seu ambiente',
    description: 'Clientes, tarefas e documentos são consultados dentro do tenant correto.',
  },
  {
    title: 'Permissões que seguem a rotina',
    description: 'Administradores e colaboradores recebem acessos compatíveis com sua função.',
  },
  {
    title: 'Arquivos com acesso temporário',
    description: 'Downloads usam links assinados e limitados no tempo, sem exposição permanente.',
  },
]
</script>

<template>
  <PublicLayout>
    <div ref="page" class="ct-modern-landing overflow-hidden">
      <section class="relative border-b border-[var(--ct-border)] bg-white">
        <div class="ct-engineering-grid pointer-events-none absolute inset-0 opacity-60"></div>
        <div
          class="pointer-events-none absolute -right-40 top-0 h-[34rem] w-[34rem] rounded-full bg-blue-100/70 blur-[100px]"
        ></div>
        <div
          class="ct-container relative grid min-h-[720px] items-center gap-12 py-16 lg:grid-cols-[0.84fr_1.16fr] lg:py-20"
        >
          <div data-reveal>
            <p class="ct-technical-label">
              <span class="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
              Gestão operacional para contabilidade
            </p>
            <h1 class="ct-modern-display mt-6">
              A rotina contábil inteira,
              <span class="ct-gradient-text">visível antes do prazo vencer.</span>
            </h1>
            <p class="mt-6 max-w-xl text-[17px] leading-7 text-[var(--ct-text-muted)]">
              Clientes, obrigações, documentos e equipe no mesmo fluxo. Você sabe o que precisa ser
              feito, quem cuida e onde a operação pede atenção.
            </p>
            <div class="mt-8 flex flex-col gap-3 sm:flex-row">
              <RouterLink to="/cadastro" class="ct-button-primary ct-landing-primary">
                Criar meu escritório grátis
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-width="2" d="M5 12h14m-6-6 6 6-6 6" />
                </svg>
              </RouterLink>
              <RouterLink to="/como-funciona" class="ct-button-secondary ct-landing-secondary">
                Ver como funciona
              </RouterLink>
            </div>
            <div class="mt-6 flex flex-wrap gap-x-5 gap-y-2 font-mono text-[11px] text-slate-500">
              <span>✓ até 5 clientes</span><span>✓ sem cartão</span
              ><span>✓ cancele quando quiser</span>
            </div>
          </div>

          <div data-reveal style="--reveal-delay: 120ms" class="relative lg:pl-4">
            <div
              class="absolute -inset-5 rounded-[28px] border border-blue-100 bg-blue-50/40 [transform:rotate(1.25deg)]"
              aria-hidden="true"
            ></div>
            <div
              class="relative overflow-hidden rounded-2xl border border-slate-300 bg-[#f7f9fc] shadow-[0_28px_80px_rgba(15,23,42,0.16)]"
            >
              <div
                class="flex h-11 items-center justify-between border-b border-slate-200 bg-white px-4"
              >
                <div class="flex items-center gap-2">
                  <span class="h-2 w-2 rounded-full bg-red-300"></span>
                  <span class="h-2 w-2 rounded-full bg-amber-300"></span>
                  <span class="h-2 w-2 rounded-full bg-emerald-400"></span>
                </div>
                <span class="font-mono text-[9px] uppercase tracking-[0.12em] text-slate-400">
                  ambiente demonstrativo · ao vivo
                </span>
              </div>
              <div class="grid min-h-[470px] sm:grid-cols-[148px_1fr]">
                <aside class="hidden border-r border-slate-200 bg-white p-3 sm:flex sm:flex-col">
                  <p class="px-2 py-2 text-[11px] font-bold text-[#101a38]">ContablyTask</p>
                  <div class="mt-5 space-y-1 text-[10px]">
                    <p class="rounded-lg bg-blue-50 px-2.5 py-2.5 font-semibold text-blue-700">
                      Visão geral
                    </p>
                    <p class="px-2.5 py-2.5 text-slate-500">Clientes</p>
                    <p class="px-2.5 py-2.5 text-slate-500">Obrigações</p>
                    <p class="px-2.5 py-2.5 text-slate-500">Calendário</p>
                    <p class="px-2.5 py-2.5 text-slate-500">Documentos</p>
                    <p class="px-2.5 py-2.5 text-slate-500">Relatórios</p>
                  </div>
                  <div class="mt-auto rounded-lg border border-slate-200 bg-slate-50 p-2.5">
                    <p class="text-[9px] font-semibold text-slate-700">Escritório Modelo</p>
                    <p class="mt-1 text-[8px] text-slate-400">Operação organizada</p>
                  </div>
                </aside>

                <div class="p-4 sm:p-5">
                  <div class="flex items-start justify-between gap-3">
                    <div>
                      <p class="text-[15px] font-semibold tracking-tight text-[#101a38]">
                        Bom dia, Felipe 👋
                      </p>
                      <p class="mt-1 text-[9px] text-slate-500">Resumo da operação de hoje.</p>
                    </div>
                    <span
                      class="rounded-lg bg-blue-600 px-2.5 py-2 text-[9px] font-semibold text-white"
                    >
                      + Nova obrigação
                    </span>
                  </div>

                  <div class="mt-4 grid grid-cols-2 gap-2 xl:grid-cols-4">
                    <div class="rounded-lg border border-slate-200 bg-white p-3">
                      <p class="text-[8px] text-slate-500">Tarefas ativas</p>
                      <p class="mt-1.5 text-lg font-semibold text-[#101a38]">28</p>
                      <p class="mt-1 text-[7px] text-blue-600">8 em andamento</p>
                    </div>
                    <div class="rounded-lg border border-slate-200 bg-white p-3">
                      <p class="text-[8px] text-slate-500">Vencendo hoje</p>
                      <p class="mt-1.5 text-lg font-semibold text-[#101a38]">4</p>
                      <p class="mt-1 text-[7px] text-amber-600">Pedem atenção</p>
                    </div>
                    <div class="rounded-lg border border-slate-200 bg-white p-3">
                      <p class="text-[8px] text-slate-500">Atrasadas</p>
                      <p class="mt-1.5 text-lg font-semibold text-[#101a38]">2</p>
                      <p class="mt-1 text-[7px] text-red-600">Fora do prazo</p>
                    </div>
                    <div class="rounded-lg border border-slate-200 bg-white p-3">
                      <p class="text-[8px] text-slate-500">No prazo</p>
                      <p class="mt-1.5 text-lg font-semibold text-[#101a38]">93%</p>
                      <p class="mt-1 text-[7px] text-emerald-600">Operação em dia</p>
                    </div>
                  </div>

                  <div class="mt-2 grid gap-2 xl:grid-cols-[1.35fr_.65fr]">
                    <div class="overflow-hidden rounded-lg border border-slate-200 bg-white p-3">
                      <div class="flex items-center justify-between">
                        <p class="text-[9px] font-semibold text-[#101a38]">Fluxo de tarefas</p>
                        <span class="font-mono text-[7px] text-slate-400">este mês</span>
                      </div>
                      <div class="mt-4 grid grid-cols-4 text-center">
                        <div>
                          <b class="block text-xs">9</b
                          ><span class="text-[7px] text-slate-400">A fazer</span>
                        </div>
                        <div>
                          <b class="block text-xs">8</b
                          ><span class="text-[7px] text-slate-400">Em curso</span>
                        </div>
                        <div>
                          <b class="block text-xs">5</b
                          ><span class="text-[7px] text-slate-400">Cliente</span>
                        </div>
                        <div>
                          <b class="block text-xs">18</b
                          ><span class="text-[7px] text-slate-400">Concluídas</span>
                        </div>
                      </div>
                      <svg
                        class="mt-2 h-16 w-full"
                        viewBox="0 0 440 72"
                        preserveAspectRatio="none"
                        aria-hidden="true"
                      >
                        <defs>
                          <linearGradient id="landing-flow" x1="0" x2="1">
                            <stop stop-color="#2563eb" />
                            <stop offset=".55" stop-color="#0891b2" />
                            <stop offset="1" stop-color="#16a34a" />
                          </linearGradient>
                          <linearGradient id="landing-fill" x1="0" y1="0" x2="0" y2="1">
                            <stop stop-color="#dbeafe" stop-opacity=".8" />
                            <stop offset="1" stop-color="#fff" stop-opacity="0" />
                          </linearGradient>
                        </defs>
                        <path
                          d="M0 45 C65 24 105 29 155 43 S250 55 310 32 S390 34 440 14 L440 72H0Z"
                          fill="url(#landing-fill)"
                        />
                        <path
                          d="M0 45 C65 24 105 29 155 43 S250 55 310 32 S390 34 440 14"
                          fill="none"
                          stroke="url(#landing-flow)"
                          stroke-width="2.5"
                        />
                      </svg>
                    </div>
                    <div class="rounded-lg border border-slate-200 bg-white p-3">
                      <p class="text-[9px] font-semibold text-[#101a38]">Alertas</p>
                      <div class="mt-3 space-y-3">
                        <div class="flex gap-2">
                          <span class="mt-0.5 h-2 w-2 rounded-full bg-red-500"></span>
                          <div>
                            <p class="text-[8px] font-semibold">2 atrasadas</p>
                            <p class="text-[7px] text-slate-400">Revise os prazos</p>
                          </div>
                        </div>
                        <div class="flex gap-2">
                          <span class="mt-0.5 h-2 w-2 rounded-full bg-amber-500"></span>
                          <div>
                            <p class="text-[8px] font-semibold">4 vencem hoje</p>
                            <p class="text-[7px] text-slate-400">Priorize entregas</p>
                          </div>
                        </div>
                        <div class="flex gap-2">
                          <span class="mt-0.5 h-2 w-2 rounded-full bg-cyan-500"></span>
                          <div>
                            <p class="text-[8px] font-semibold">5 aguardam cliente</p>
                            <p class="text-[7px] text-slate-400">Retorno externo</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="mt-2 rounded-lg border border-slate-200 bg-white p-3">
                    <div class="flex items-center justify-between">
                      <p class="text-[9px] font-semibold text-[#101a38]">Minhas prioridades</p>
                      <span class="text-[7px] font-semibold text-blue-600">Ver todas</span>
                    </div>
                    <div class="mt-2 grid gap-2 sm:grid-cols-3">
                      <div class="border-t border-slate-100 pt-2">
                        <p class="truncate text-[8px] font-semibold">Fechamento contábil</p>
                        <p class="mt-1 text-[7px] text-slate-400">Comércio Horizonte</p>
                      </div>
                      <div class="border-t border-slate-100 pt-2">
                        <p class="truncate text-[8px] font-semibold">Enviar DCTFWeb</p>
                        <p class="mt-1 text-[7px] text-slate-400">Clínica Modelo</p>
                      </div>
                      <div class="border-t border-slate-100 pt-2">
                        <p class="truncate text-[8px] font-semibold">Revisar documentos</p>
                        <p class="mt-1 text-[7px] text-slate-400">Padaria Central</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="border-b border-[var(--ct-border)] bg-white" aria-label="Recursos objetivos">
        <div class="ct-container grid lg:grid-cols-[0.8fr_repeat(3,1fr)]">
          <div
            class="flex items-center border-b border-slate-200 py-6 lg:border-b-0 lg:border-r lg:pr-8"
          >
            <p class="max-w-[15rem] text-sm font-semibold leading-5 text-[#101a38]">
              Estrutura concreta para começar pequeno e crescer sem refazer a operação.
            </p>
          </div>
          <article
            v-for="item in proofPoints"
            :key="item.value"
            class="border-b border-slate-200 py-6 lg:border-b-0 lg:border-r lg:px-8 lg:last:border-r-0"
          >
            <p class="font-mono text-[22px] font-semibold tracking-[-0.04em] text-blue-600">
              {{ item.value }}
            </p>
            <p class="mt-1 text-xs font-semibold text-[#26344f]">{{ item.label }}</p>
            <p class="mt-1 text-[11px] text-slate-500">{{ item.detail }}</p>
          </article>
        </div>
      </section>

      <section class="bg-[#f8fafc] py-20 lg:py-28">
        <div class="ct-container">
          <div data-reveal class="grid gap-6 lg:grid-cols-[0.72fr_1.28fr] lg:items-end">
            <div>
              <p class="ct-technical-label">O produto em operação</p>
              <h2 class="ct-modern-section-title mt-5">
                Tudo que o escritório precisa, no mesmo contexto.
              </h2>
            </div>
            <p
              class="max-w-2xl text-[15px] leading-7 text-[var(--ct-text-muted)] lg:justify-self-end"
            >
              Não é apenas uma lista de tarefas. Cada ação continua ligada ao cliente, ao prazo, ao
              responsável e aos arquivos necessários para concluir a entrega.
            </p>
          </div>

          <div class="mt-12 grid gap-4 lg:grid-cols-2">
            <article
              v-for="(item, index) in capabilities"
              :key="item.number"
              data-reveal
              class="ct-capability-card group"
              :style="{ '--reveal-delay': `${(index % 2) * 90}ms` }"
            >
              <div class="flex items-center justify-between">
                <span class="font-mono text-[11px] font-semibold tracking-[0.12em] text-blue-600">{{
                  item.number
                }}</span>
                <span
                  class="rounded-full border border-slate-200 px-3 py-1 font-mono text-[9px] uppercase tracking-[0.1em] text-slate-500"
                  >{{ item.meta }}</span
                >
              </div>
              <h3 class="mt-5 text-[24px] font-semibold tracking-[-0.03em] text-[#101a38]">
                {{ item.title }}
              </h3>
              <p class="mt-2 max-w-lg text-sm leading-6 text-slate-600">{{ item.description }}</p>

              <div class="mt-7 overflow-hidden rounded-xl border border-slate-200 bg-[#fbfcfe]">
                <div class="flex items-center gap-1.5 border-b border-slate-200 bg-white px-3 py-2">
                  <span class="h-1.5 w-1.5 rounded-full bg-blue-400"></span
                  ><span class="h-1.5 w-1.5 rounded-full bg-slate-200"></span>
                  <span
                    class="ml-1.5 font-mono text-[9px] uppercase tracking-[0.1em] text-slate-400"
                    >{{ item.meta }}</span
                  >
                </div>
                <div class="p-4">
                  <svg
                    v-if="item.icon === 'client'"
                    viewBox="0 0 520 150"
                    class="h-36 w-full"
                    aria-hidden="true"
                  >
                    <g fill="none" stroke="#cbd5e1" stroke-width="1.4">
                      <rect x="10" y="18" width="106" height="30" rx="7" />
                      <rect x="10" y="60" width="106" height="30" rx="7" />
                      <rect x="10" y="102" width="106" height="30" rx="7" />
                    </g>
                    <g fill="#64748b" font-family="ui-monospace" font-size="10">
                      <text x="63" y="37" text-anchor="middle">cadastro</text>
                      <text x="63" y="79" text-anchor="middle">documentos</text>
                      <text x="63" y="121" text-anchor="middle">histórico</text>
                    </g>
                    <path
                      d="M116 33H190V75H226M116 75H226M116 117H190V75"
                      fill="none"
                      stroke="#2563eb"
                      stroke-width="1.8"
                    />
                    <rect x="226" y="48" width="120" height="54" rx="12" fill="#2563eb" />
                    <text
                      x="286"
                      y="72"
                      text-anchor="middle"
                      fill="white"
                      font-family="ui-monospace"
                      font-size="11"
                    >
                      CLIENTE
                    </text>
                    <text
                      x="286"
                      y="87"
                      text-anchor="middle"
                      fill="#bfdbfe"
                      font-family="ui-monospace"
                      font-size="8"
                    >
                      contexto único
                    </text>
                    <path d="M346 75H390" stroke="#2563eb" stroke-width="1.8" />
                    <rect x="390" y="48" width="118" height="54" rx="12" fill="#172554" />
                    <path
                      d="M408 84l16-20 16 11 18-27 17 9 18-18"
                      fill="none"
                      stroke="#93c5fd"
                      stroke-width="2"
                    />
                  </svg>

                  <svg
                    v-else-if="item.icon === 'deadline'"
                    viewBox="0 0 520 150"
                    class="h-36 w-full"
                    aria-hidden="true"
                  >
                    <line x1="28" y1="116" x2="492" y2="116" stroke="#cbd5e1" />
                    <path
                      d="M50 100 C120 88 150 44 222 60 S330 108 386 64 S448 42 482 26"
                      fill="none"
                      stroke="#2563eb"
                      stroke-width="2.6"
                    />
                    <path
                      d="M50 100 C120 88 150 44 222 60 S330 108 386 64 S448 42 482 26L482 116H50Z"
                      fill="#dbeafe"
                      opacity=".65"
                    />
                    <g fill="#2563eb">
                      <circle cx="153" cy="51" r="4" />
                      <circle cx="386" cy="64" r="4" />
                      <circle cx="482" cy="26" r="4" />
                    </g>
                    <g fill="#64748b" font-family="ui-monospace" font-size="9">
                      <text x="50" y="136">pendente</text>
                      <text x="218" y="136">em curso</text>
                      <text x="424" y="136">concluída</text>
                    </g>
                    <rect x="352" y="14" width="96" height="24" rx="12" fill="#fef2f2" />
                    <text
                      x="400"
                      y="30"
                      text-anchor="middle"
                      fill="#dc2626"
                      font-family="ui-monospace"
                      font-size="9"
                    >
                      2 alertas
                    </text>
                  </svg>

                  <svg
                    v-else-if="item.icon === 'team'"
                    viewBox="0 0 520 150"
                    class="h-36 w-full"
                    aria-hidden="true"
                  >
                    <g font-family="ui-monospace" font-size="9" fill="#475569">
                      <text x="12" y="30">Ana</text>
                      <text x="12" y="66">Rafael</text>
                      <text x="12" y="102">Bruna</text>
                      <text x="12" y="138">Lucas</text>
                    </g>
                    <g fill="#eef2f7">
                      <rect x="82" y="17" width="400" height="16" rx="8" />
                      <rect x="82" y="53" width="400" height="16" rx="8" />
                      <rect x="82" y="89" width="400" height="16" rx="8" />
                      <rect x="82" y="125" width="400" height="16" rx="8" />
                    </g>
                    <rect x="82" y="17" width="330" height="16" rx="8" fill="#2563eb" />
                    <rect x="82" y="53" width="260" height="16" rx="8" fill="#0891b2" />
                    <rect x="82" y="89" width="188" height="16" rx="8" fill="#16a34a" />
                    <rect x="82" y="125" width="118" height="16" rx="8" fill="#93c5fd" />
                  </svg>

                  <svg v-else viewBox="0 0 520 150" class="h-36 w-full" aria-hidden="true">
                    <g stroke="#e2e8f0">
                      <line x1="20" y1="28" x2="500" y2="28" />
                      <line x1="20" y1="67" x2="500" y2="67" />
                      <line x1="20" y1="106" x2="500" y2="106" />
                    </g>
                    <g fill="#bfdbfe">
                      <rect x="42" y="72" width="30" height="55" rx="4" />
                      <rect x="114" y="48" width="30" height="79" rx="4" />
                      <rect x="186" y="84" width="30" height="43" rx="4" />
                      <rect x="258" y="38" width="30" height="89" rx="4" />
                      <rect x="330" y="60" width="30" height="67" rx="4" />
                      <rect x="402" y="28" width="30" height="99" rx="4" />
                    </g>
                    <g fill="#2563eb">
                      <rect x="42" y="98" width="30" height="29" rx="4" />
                      <rect x="114" y="78" width="30" height="49" rx="4" />
                      <rect x="186" y="104" width="30" height="23" rx="4" />
                      <rect x="258" y="73" width="30" height="54" rx="4" />
                      <rect x="330" y="88" width="30" height="39" rx="4" />
                      <rect x="402" y="62" width="30" height="65" rx="4" />
                    </g>
                    <path
                      d="M44 82L129 58 201 72 273 43 345 52 417 21 478 35"
                      fill="none"
                      stroke="#172554"
                      stroke-width="2.2"
                      stroke-linecap="round"
                    />
                  </svg>
                </div>
              </div>
            </article>
          </div>
        </div>
      </section>

      <section class="bg-white py-20 lg:py-28">
        <div class="ct-container">
          <div data-reveal class="grid gap-8 lg:grid-cols-[0.75fr_1.25fr] lg:items-end">
            <div>
              <p class="ct-technical-label">Antes e depois</p>
              <h2 class="ct-modern-section-title mt-5">Menos procura. Mais execução.</h2>
            </div>
            <p class="max-w-2xl text-[15px] leading-7 text-slate-600 lg:justify-self-end">
              A plataforma reduz o trabalho invisível entre descobrir uma demanda e efetivamente
              concluí-la.
            </p>
          </div>
          <div data-reveal class="mt-12 overflow-hidden rounded-2xl border border-slate-200">
            <div
              class="hidden grid-cols-[1fr_1fr_1fr] bg-slate-50 font-mono text-[10px] uppercase tracking-[0.1em] text-slate-500 md:grid"
            >
              <p class="px-5 py-4">Situação</p>
              <p class="px-5 py-4">Sem fluxo central</p>
              <p class="px-5 py-4 text-blue-600">Com ContablyTask</p>
            </div>
            <article
              v-for="row in comparison"
              :key="row[0]"
              class="grid gap-3 border-t border-slate-200 bg-white px-5 py-5 first:border-t-0 md:grid-cols-[1fr_1fr_1fr] md:gap-8"
            >
              <h3 class="text-sm font-semibold text-[#101a38]">{{ row[0] }}</h3>
              <p class="text-sm text-slate-500">
                <span class="mb-1 block font-mono text-[9px] uppercase text-slate-400 md:hidden"
                  >Sem fluxo central</span
                >{{ row[1] }}
              </p>
              <p class="text-sm font-medium text-blue-700">
                <span class="mb-1 block font-mono text-[9px] uppercase text-blue-500 md:hidden"
                  >Com ContablyTask</span
                >{{ row[2] }}
              </p>
            </article>
          </div>
        </div>
      </section>

      <section class="px-3 pb-3 sm:px-4 sm:pb-4">
        <div
          class="relative isolate overflow-hidden rounded-[28px] bg-[var(--ct-navy)] py-20 text-white lg:py-28"
        >
          <div
            class="ct-engineering-grid-dark pointer-events-none absolute inset-0 opacity-60"
          ></div>
          <div
            class="pointer-events-none absolute -right-40 -top-48 h-[38rem] w-[38rem] rounded-full bg-blue-500/20 blur-[110px]"
          ></div>
          <div class="ct-container relative">
            <div data-reveal class="max-w-3xl">
              <p class="ct-technical-label border-white/15 bg-white/5 text-blue-200">
                Do cadastro ao relatório
              </p>
              <h2
                class="mt-6 text-[clamp(2.25rem,5vw,4.25rem)] font-semibold leading-[1.02] tracking-[-0.05em]"
              >
                Quatro passos. Um escritório inteiro no mesmo fluxo.
              </h2>
              <p class="mt-5 max-w-2xl text-[16px] leading-7 text-white/65">
                A complexidade contábil continua existindo. O que muda é que a equipe deixa de
                carregá-la na memória.
              </p>
            </div>
            <div class="mt-12 grid gap-4 lg:grid-cols-4">
              <article
                v-for="(step, index) in workflow"
                :key="step.number"
                data-reveal
                class="relative overflow-hidden rounded-2xl border p-6"
                :class="
                  index === workflow.length - 1
                    ? 'border-blue-400/30 bg-blue-500/15'
                    : 'border-white/10 bg-white/[0.035]'
                "
                :style="{ '--reveal-delay': `${index * 70}ms` }"
              >
                <div class="flex items-center justify-between">
                  <span class="font-mono text-[11px] tracking-[0.12em] text-blue-300"
                    >PASSO {{ step.number }}</span
                  ><span
                    v-if="index === workflow.length - 1"
                    class="rounded-full border border-blue-300/20 px-2 py-1 font-mono text-[8px] uppercase tracking-wider text-blue-200"
                    >resultado</span
                  >
                </div>
                <h3 class="mt-6 text-xl font-semibold">{{ step.title }}</h3>
                <p class="mt-2 min-h-16 text-sm leading-6 text-white/60">{{ step.description }}</p>
                <div
                  class="mt-6 border-t border-white/10 pt-4 font-mono text-[9px] uppercase tracking-[0.1em] text-white/35"
                >
                  {{ step.meta }}
                </div>
              </article>
            </div>
          </div>
        </div>
      </section>

      <section class="bg-white py-20 lg:py-28">
        <div class="ct-container grid gap-12 lg:grid-cols-[0.7fr_1.3fr]">
          <div data-reveal>
            <p class="ct-technical-label">Segurança na rotina</p>
            <h2 class="ct-modern-section-title mt-5">Controle que aparece onde precisa.</h2>
            <p class="mt-5 max-w-md text-sm leading-7 text-slate-600">
              A proteção não fica isolada numa página jurídica. Ela participa da autenticação, das
              permissões e do acesso aos documentos.
            </p>
            <RouterLink to="/privacidade" class="ct-link-arrow mt-7"
              >Conhecer os controles <span>→</span></RouterLink
            >
          </div>
          <div
            class="grid gap-px overflow-hidden rounded-2xl border border-slate-200 bg-slate-200 md:grid-cols-3"
          >
            <article
              v-for="(item, index) in trustPoints"
              :key="item.title"
              data-reveal
              class="bg-white p-6"
              :style="{ '--reveal-delay': `${index * 80}ms` }"
            >
              <span
                class="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 font-mono text-xs font-semibold text-blue-700"
                >0{{ index + 1 }}</span
              >
              <h3 class="mt-6 text-base font-semibold text-[#101a38]">{{ item.title }}</h3>
              <p class="mt-2 text-sm leading-6 text-slate-600">{{ item.description }}</p>
            </article>
          </div>
        </div>
      </section>

      <section class="border-t border-slate-200 bg-[#f8fafc] py-20 lg:py-24">
        <div
          data-reveal
          class="ct-container flex flex-col justify-between gap-8 lg:flex-row lg:items-end"
        >
          <div>
            <p class="ct-technical-label">Comece simples</p>
            <h2 class="ct-modern-section-title mt-5 max-w-3xl">
              Organize o próximo fechamento sem depender de mais uma planilha.
            </h2>
            <p class="mt-5 max-w-2xl text-[15px] leading-7 text-slate-600">
              Cadastre até cinco clientes gratuitamente. Quando a carteira e a equipe crescerem, a
              estrutura já estará pronta.
            </p>
          </div>
          <div class="flex shrink-0 flex-col gap-3 sm:flex-row">
            <RouterLink to="/planos" class="ct-button-secondary ct-landing-secondary"
              >Comparar planos</RouterLink
            ><RouterLink to="/cadastro" class="ct-button-primary ct-landing-primary"
              >Criar meu escritório <span>→</span></RouterLink
            >
          </div>
        </div>
      </section>
    </div>
  </PublicLayout>
</template>
