<script setup lang="ts">
import { RouterLink } from 'vue-router'

const problemas = [
  {
    numero: '01',
    titulo: 'Tarefas espalhadas',
    descricao:
      'Planilhas, mensagens, anotações e sistemas diferentes dificultam saber o que realmente está pendente.',
  },
  {
    numero: '02',
    titulo: 'Prazos sem visibilidade',
    descricao:
      'Quando não há um fluxo claro, entregas importantes podem depender da memória ou de cobranças manuais.',
  },
  {
    numero: '03',
    titulo: 'Equipe desalinhada',
    descricao:
      'Sem responsáveis definidos e acompanhamento centralizado, o retrabalho aumenta e a gestão perde previsibilidade.',
  },
]

const principios = [
  {
    numero: '01',
    titulo: 'Clareza antes de complexidade',
    descricao:
      'A tecnologia deve simplificar a rotina. Por isso, priorizamos uma experiência intuitiva, objetiva e útil desde o primeiro acesso.',
  },
  {
    numero: '02',
    titulo: 'Responsabilidade visível',
    descricao:
      'Toda tarefa precisa ter contexto, prazo e responsável. Isso transforma acompanhamento em processo, não em cobrança constante.',
  },
  {
    numero: '03',
    titulo: 'Evolução com método',
    descricao:
      'Construímos a plataforma ouvindo a rotina real dos escritórios, para evoluir com base em problemas concretos.',
  },
]

const marcos = [
  {
    etapa: 'A origem',
    titulo: 'Uma dor que se repete em muitos escritórios',
    descricao:
      'A ContablyTask surgiu da observação de uma rotina marcada por controles descentralizados, prazos críticos e pouca visibilidade da operação.',
    icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
  },
  {
    etapa: 'A proposta',
    titulo: 'Transformar rotina em processo acompanhável',
    descricao:
      'Nossa resposta foi criar uma plataforma que reúne tarefas, clientes, documentos e responsáveis em um mesmo ambiente.',
    icon: 'M13 10V3L4 14h7v7l9-11h-7z'
  },
  {
    etapa: 'A construção',
    titulo: 'Produto que acompanha a operação real',
    descricao:
      'Seguimos evoluindo cada fluxo com um objetivo simples: ajudar o escritório a crescer sem perder controle sobre o que precisa ser entregue.',
    icon: 'M5 13l4 4L19 7'
  },
]

const beneficios = [
  'Visualização centralizada de tarefas e obrigações',
  'Responsáveis, prioridades e prazos em um só fluxo',
  'Acompanhamento mais simples para gestores e equipe',
  'Estrutura para reduzir retrabalho e dependência de controles paralelos',
]
</script>

<template>
  <div class="min-h-screen overflow-x-hidden bg-[#F8FAFC] text-slate-900">
    <header class="sticky top-0 z-50 border-b border-slate-200/80 bg-white/85 backdrop-blur-xl">
      <div class="mx-auto flex h-[72px] max-w-7xl items-center justify-between px-5 sm:px-6 lg:px-8">
        <RouterLink to="/" class="group flex items-center gap-3" aria-label="Ir para a página inicial">
          <span class="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 transition-colors group-hover:bg-blue-100">
            <svg class="h-5 w-5 text-blue-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true">
              <path d="M9 11l3 3L22 4" />
              <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
            </svg>
          </span>
          <span class="text-lg font-bold tracking-tight text-slate-950">
            Contably<span class="text-blue-600">Task</span>
          </span>
        </RouterLink>

        <nav class="hidden items-center gap-7 md:flex" aria-label="Navegação principal">
          <RouterLink to="/" class="text-sm font-medium text-slate-500 transition-colors hover:text-slate-950">Início</RouterLink>
          <RouterLink to="/sobre" class="text-sm font-semibold text-slate-950">Sobre nós</RouterLink>
          <RouterLink to="/planos" class="text-sm font-medium text-slate-500 transition-colors hover:text-slate-950">Planos</RouterLink>
          <RouterLink to="/como-funciona" class="text-sm font-medium text-slate-500 transition-colors hover:text-slate-950">Como Funciona</RouterLink>
          <RouterLink to="/contato" class="text-sm font-medium text-slate-500 transition-colors hover:text-slate-950">Contato</RouterLink>
        </nav>

        <RouterLink to="/cadastro" class="hidden min-h-[44px] items-center justify-center rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-blue-700 md:inline-flex">
          Criar escritório
        </RouterLink>
      </div>
    </header>

    <main>
      <!-- HERO -->
      <section class="border-b border-slate-200 bg-white">
        <div class="mx-auto max-w-7xl px-5 py-16 sm:px-6 lg:px-8 lg:py-24">
          <div class="grid items-center gap-12 lg:grid-cols-[0.88fr_1.12fr] lg:gap-16">
            <div class="max-w-xl">
              <p class="text-sm font-semibold uppercase tracking-[0.16em] text-blue-600">Sobre a ContablyTask</p>
              <h1 class="mt-4 text-4xl font-semibold tracking-[-0.045em] text-slate-950 sm:text-5xl lg:text-6xl">
                Organização não deveria depender da memória da sua equipe.
              </h1>
              <p class="mt-6 max-w-2xl text-base leading-8 text-slate-600 sm:text-lg">
                A ContablyTask foi criada para transformar a rotina de escritórios contábeis em uma operação mais visível, responsável e previsível — sem depender de planilhas dispersas, mensagens soltas ou cobranças manuais.
              </p>
              <div class="mt-8 flex flex-col gap-3 sm:flex-row">
                <RouterLink to="/cadastro" class="inline-flex min-h-[48px] items-center justify-center rounded-xl bg-blue-600 px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-blue-700">
                  Criar meu escritório
                  <svg class="ml-2 h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                    <path d="M5 12h14" />
                    <path d="m13 6 6 6-6 6" />
                  </svg>
                </RouterLink>
                <a href="#como-ajudamos" class="inline-flex min-h-[48px] items-center justify-center rounded-xl border border-slate-200 bg-white px-6 py-3 text-sm font-semibold text-slate-700 transition-colors hover:border-blue-300 hover:text-blue-700">
                  Entender nossa proposta
                </a>
              </div>
              <div class="mt-9 flex items-center gap-3 text-sm text-slate-500">
                <span class="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-50 text-emerald-600">
                  <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="m5 12 4 4L19 6" /></svg>
                </span>
                Feita para a rotina real de escritórios contábeis.
              </div>
            </div>

            <!-- Mockup Realista -->
            <div class="relative">
              <div class="absolute -inset-4 rounded-[2rem] bg-blue-50/60 blur-2xl" aria-hidden="true"></div>
              <div class="relative overflow-hidden rounded-[1.25rem] border border-slate-200 bg-white shadow-[0_30px_80px_rgba(15,23,42,0.12)]">
                <!-- Browser Top Bar -->
                <div class="flex h-10 items-center gap-2 border-b border-slate-200 bg-slate-50 px-4">
                  <span class="h-2.5 w-2.5 rounded-full bg-red-400"></span>
                  <span class="h-2.5 w-2.5 rounded-full bg-amber-400"></span>
                  <span class="h-2.5 w-2.5 rounded-full bg-emerald-400"></span>
                  <div class="mx-auto flex h-6 w-1/2 items-center justify-center rounded-md bg-white text-[10px] font-medium text-slate-400 shadow-sm">
                    app.contablytask.com.br/dashboard
                  </div>
                </div>

                <div class="grid min-h-[360px] grid-cols-[100px_1fr] sm:min-h-[430px] sm:grid-cols-[140px_1fr]">
                  <!-- Sidebar -->
                  <aside class="border-r border-slate-200 bg-slate-50/50 px-2 py-4 sm:px-3">
                    <div class="mb-6 flex items-center gap-2 px-2">
                      <div class="flex h-6 w-6 items-center justify-center rounded-md bg-blue-600 text-[10px] font-bold text-white">C</div>
                      <div class="hidden h-2.5 w-12 rounded bg-slate-300 sm:block"></div>
                    </div>
                    <div class="space-y-1.5">
                      <div class="flex items-center gap-2 rounded-lg bg-blue-100 px-2 py-1.5 text-blue-700">
                        <svg class="h-3 w-3" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>
                        <span class="hidden h-2 w-12 rounded bg-blue-500 sm:block"></span>
                      </div>
                      <div class="flex items-center gap-2 px-2 py-1.5 text-slate-400">
                        <svg class="h-3 w-3" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg>
                        <span class="hidden h-2 w-10 rounded bg-slate-300 sm:block"></span>
                      </div>
                      <div class="flex items-center gap-2 px-2 py-1.5 text-slate-400">
                        <svg class="h-3 w-3" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
                        <span class="hidden h-2 w-8 rounded bg-slate-300 sm:block"></span>
                      </div>
                    </div>
                  </aside>

                  <!-- Main Content -->
                  <div class="p-4 sm:p-6">
                    <div class="flex items-start justify-between gap-4">
                      <div>
                        <div class="flex h-4 w-24 items-center rounded bg-slate-800 text-[8px] font-bold text-white px-1">Visão Geral</div>
                        <div class="mt-2 h-2.5 w-32 rounded bg-slate-200"></div>
                      </div>
                      <div class="flex h-8 w-24 items-center justify-center rounded-lg bg-blue-600 text-[9px] font-semibold text-white">+ Nova Tarefa</div>
                    </div>

                    <div class="mt-6 grid grid-cols-3 gap-2 sm:gap-3">
                      <div class="rounded-xl border border-slate-200 bg-white p-3">
                        <div class="h-2 w-10 rounded bg-slate-200"></div>
                        <div class="mt-2 h-4 w-8 rounded bg-slate-800"></div>
                        <div class="mt-2 h-1.5 w-full rounded-full bg-slate-100"><div class="h-1.5 w-3/4 rounded-full bg-emerald-500"></div></div>
                      </div>
                      <div class="rounded-xl border border-slate-200 bg-white p-3">
                        <div class="h-2 w-8 rounded bg-slate-200"></div>
                        <div class="mt-2 h-4 w-6 rounded bg-slate-800"></div>
                        <div class="mt-2 h-1.5 w-full rounded-full bg-slate-100"><div class="h-1.5 w-1/2 rounded-full bg-amber-500"></div></div>
                      </div>
                      <div class="rounded-xl border border-slate-200 bg-white p-3">
                        <div class="h-2 w-10 rounded bg-slate-200"></div>
                        <div class="mt-2 h-4 w-8 rounded bg-slate-800"></div>
                        <div class="mt-2 h-1.5 w-full rounded-full bg-slate-100"><div class="h-1.5 w-1/4 rounded-full bg-blue-500"></div></div>
                      </div>
                    </div>

                    <div class="mt-5 overflow-hidden rounded-xl border border-slate-200 bg-white">
                      <div class="border-b border-slate-100 px-3 py-2.5">
                        <div class="h-2.5 w-20 rounded bg-slate-700"></div>
                      </div>
                      <div class="divide-y divide-slate-100">
                        <div class="flex items-center gap-3 px-3 py-2.5">
                          <span class="h-2 w-2 rounded-full bg-blue-500"></span>
                          <div class="h-2 flex-1 rounded bg-slate-200"></div>
                          <span class="flex h-4 w-12 items-center justify-center rounded-full bg-blue-100 text-[8px] font-bold text-blue-700">Aberta</span>
                        </div>
                        <div class="flex items-center gap-3 px-3 py-2.5">
                          <span class="h-2 w-2 rounded-full bg-amber-400"></span>
                          <div class="h-2 flex-1 rounded bg-slate-200"></div>
                          <span class="flex h-4 w-12 items-center justify-center rounded-full bg-amber-100 text-[8px] font-bold text-amber-700">Pendente</span>
                        </div>
                        <div class="flex items-center gap-3 px-3 py-2.5">
                          <span class="h-2 w-2 rounded-full bg-emerald-500"></span>
                          <div class="h-2 flex-1 rounded bg-slate-200"></div>
                          <span class="flex h-4 w-12 items-center justify-center rounded-full bg-emerald-100 text-[8px] font-bold text-emerald-700">Feita</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Toast Notification -->
              <div class="absolute -bottom-5 -left-4 hidden max-w-56 animate-bounce rounded-2xl border border-slate-200 bg-white p-4 shadow-[0_16px_40px_rgba(15,23,42,0.12)] sm:block" style="animation-duration: 3s;">
                <div class="flex items-center gap-3">
                  <span class="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
                    <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="m5 12 4 4L19 6" /></svg>
                  </span>
                  <div>
                    <p class="text-xs font-semibold text-slate-900">Tarefa concluída</p>
                    <p class="mt-0.5 text-xs text-slate-500">Responsável atualizado</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- O PROBLEMA -->
      <section class="mx-auto max-w-7xl px-5 py-20 sm:px-6 lg:px-8 lg:py-24">
        <div class="grid gap-12 lg:grid-cols-[0.8fr_1.2fr] lg:gap-20">
          <div>
            <p class="text-sm font-semibold uppercase tracking-[0.16em] text-blue-600">O problema que nos trouxe até aqui</p>
            <h2 class="mt-4 text-3xl font-semibold tracking-[-0.04em] text-slate-950 sm:text-4xl">
              Uma rotina importante não pode ficar escondida entre planilhas e conversas.
            </h2>
            <p class="mt-6 text-base leading-8 text-slate-600">
              Escritórios contábeis trabalham com uma enorme quantidade de tarefas, documentos e prazos. Quando essas informações ficam descentralizadas, o time passa mais tempo procurando contexto do que executando bem.
            </p>
          </div>

          <div class="grid gap-6 md:grid-cols-3">
            <article v-for="problema in problemas" :key="problema.numero" class="flex h-full flex-col rounded-2xl border border-slate-200 bg-white p-7 shadow-sm transition-all hover:-translate-y-1 hover:shadow-lg">
              <p class="font-mono text-xs font-bold tracking-[0.12em] text-blue-600">{{ problema.numero }}</p>
              <h3 class="mt-4 text-lg font-semibold tracking-tight text-slate-950">{{ problema.titulo }}</h3>
              <p class="mt-3 text-sm leading-7 text-slate-600">{{ problema.descricao }}</p>
            </article>
          </div>
        </div>
      </section>

      <!-- COMO AJUDAMOS -->
      <section id="como-ajudamos" class="scroll-mt-24 border-y border-slate-200 bg-white">
        <div class="mx-auto max-w-7xl px-5 py-20 sm:px-6 lg:px-8 lg:py-24">
          <div class="max-w-3xl">
            <p class="text-sm font-semibold uppercase tracking-[0.16em] text-blue-600">Como ajudamos</p>
            <h2 class="mt-4 text-3xl font-semibold tracking-[-0.04em] text-slate-950 sm:text-4xl">
              Da operação reativa para uma rotina que a equipe consegue acompanhar.
            </h2>
            <p class="mt-5 text-base leading-8 text-slate-600">
              A ContablyTask reúne o que precisa acontecer no escritório em um fluxo claro: o que fazer, quem faz, quando vence e o que está bloqueando a entrega.
            </p>
          </div>

          <div class="mt-12 grid items-stretch gap-6 lg:grid-cols-2">
            <!-- Antes -->
            <article class="flex flex-col rounded-3xl border border-slate-200 bg-slate-50 p-7 sm:p-8">
              <p class="text-sm font-semibold uppercase tracking-[0.14em] text-slate-500">Antes</p>
              <div class="mt-6 space-y-4">
                <div class="rounded-xl border border-slate-200 bg-white p-4">
                  <p class="text-sm font-medium text-slate-900">“Quem ficou responsável por isso?”</p>
                  <div class="mt-3 h-2 w-4/5 animate-pulse rounded bg-slate-200"></div>
                  <div class="mt-2 h-2 w-3/5 animate-pulse rounded bg-slate-200"></div>
                </div>
                <div class="rounded-xl border border-slate-200 bg-white p-4">
                  <p class="text-sm font-medium text-slate-900">“Esse documento já chegou?”</p>
                  <div class="mt-3 h-2 w-3/4 animate-pulse rounded bg-slate-200"></div>
                  <div class="mt-2 h-2 w-2/5 animate-pulse rounded bg-slate-200"></div>
                </div>
                <div class="rounded-xl border border-slate-200 bg-white p-4">
                  <p class="text-sm font-medium text-slate-900">“Qual é a prioridade de hoje?”</p>
                  <div class="mt-3 h-2 w-4/5 animate-pulse rounded bg-slate-200"></div>
                  <div class="mt-2 h-2 w-1/2 animate-pulse rounded bg-slate-200"></div>
                </div>
              </div>
            </article>

            <!-- Depois -->
            <article class="flex flex-col rounded-3xl bg-[#172554] p-7 text-white shadow-xl sm:p-8">
              <p class="text-sm font-semibold uppercase tracking-[0.14em] text-blue-200">Com a ContablyTask</p>
              <h3 class="mt-5 max-w-lg text-2xl font-semibold tracking-tight sm:text-3xl">
                Contexto, prioridade e responsabilidade em um único lugar.
              </h3>
              <ul class="mt-8 flex-1 space-y-5">
                <li v-for="beneficio in beneficios" :key="beneficio" class="flex items-start gap-3 text-sm leading-7 text-white/75">
                  <span class="mt-1.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-blue-400/20 text-blue-200">
                    <svg class="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8" aria-hidden="true"><path d="m5 12 4 4L19 6" /></svg>
                  </span>
                  {{ beneficio }}
                </li>
              </ul>
              <div class="mt-8">
                <RouterLink to="/cadastro" class="inline-flex min-h-[44px] w-fit items-center justify-center rounded-xl bg-white px-5 py-3 text-sm font-semibold text-[#172554] transition-colors hover:bg-blue-50">
                  Organizar minha operação
                </RouterLink>
              </div>
            </article>
          </div>
        </div>
      </section>

      <!-- COMO CONSTRUÍMOS -->
      <section class="mx-auto max-w-7xl px-5 py-20 sm:px-6 lg:px-8 lg:py-24">
        <div class="mx-auto max-w-3xl text-center">
          <p class="text-sm font-semibold uppercase tracking-[0.16em] text-blue-600">Como construímos</p>
          <h2 class="mt-4 text-3xl font-semibold tracking-[-0.04em] text-slate-950 sm:text-4xl">
            Produto útil para quem precisa entregar bem todos os dias.
          </h2>
          <p class="mt-5 text-base leading-8 text-slate-600">
            Não buscamos criar mais uma ferramenta para preencher. Nosso compromisso é criar uma base operacional que se encaixe na rotina do escritório e ajude pessoas a trabalharem com mais segurança.
          </p>
        </div>

        <!-- Quote Principal -->
        <div class="mx-auto mt-12 max-w-4xl rounded-3xl border border-slate-200 bg-slate-50 p-8 text-center sm:p-12">
          <svg class="mx-auto h-10 w-10 text-blue-200" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M9.983 3v7.391c0 5.704-3.731 9.57-8.983 10.609l-.995-2.151c2.432-.917 3.995-3.638 3.995-5.849h-4v-10h9.983zm14.017 0v7.391c0 5.704-3.748 9.571-9 10.609l-.996-2.151c2.433-.917 3.996-3.638 3.996-5.849h-3.983v-10h9.983z"/>
          </svg>
          <blockquote class="mt-4 text-2xl font-semibold leading-snug tracking-[-0.03em] text-slate-800 sm:text-3xl">
            “Toda rotina importante precisa ser simples de entender, fácil de acompanhar e segura de executar.”
          </blockquote>
          <p class="mt-6 text-sm font-medium text-slate-500">É a partir dessa ideia que avaliamos cada tela, cada fluxo e cada melhoria feita na ContablyTask.</p>
        </div>

        <!-- Grid de Princípios -->
        <div class="mt-8 grid gap-6 md:grid-cols-3">
          <article v-for="principio in principios" :key="principio.numero" class="flex h-full flex-col rounded-3xl border border-slate-200 bg-white p-7 shadow-sm transition-all hover:-translate-y-1 hover:shadow-lg">
            <span class="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 font-mono text-sm font-bold text-blue-600">
              {{ principio.numero }}
            </span>
            <h3 class="mt-5 text-lg font-semibold tracking-tight text-slate-950">{{ principio.titulo }}</h3>
            <p class="mt-3 text-sm leading-7 text-slate-600">{{ principio.descricao }}</p>
          </article>
        </div>
      </section>

      <!-- TRAJETÓRIA (TIMELINE) -->
      <section class="border-y border-slate-200 bg-white">
        <div class="mx-auto max-w-5xl px-5 py-20 sm:px-6 lg:px-8 lg:py-24">
          <div class="max-w-3xl">
            <p class="text-sm font-semibold uppercase tracking-[0.16em] text-blue-600">Nossa trajetória</p>
            <h2 class="mt-4 text-3xl font-semibold tracking-[-0.04em] text-slate-950 sm:text-4xl">
              A plataforma nasceu da necessidade de dar forma a uma rotina complexa.
            </h2>
          </div>

          <div class="relative mt-12 pl-12 sm:pl-16">
            <!-- Linha vertical -->
            <div class="absolute left-4 top-2 h-full w-px bg-slate-200 sm:left-5" aria-hidden="true"></div>
            
            <article v-for="(marco, index) in marcos" :key="marco.etapa" class="relative pb-12 last:pb-0">
              <!-- Bolinha com ícone -->
              <span class="absolute left-0 top-1 flex h-8 w-8 -translate-x-1/2 items-center justify-center rounded-full border-4 border-white bg-blue-600 shadow-sm ring-1 ring-slate-200 sm:h-10 sm:w-10 sm:left-1" aria-hidden="true">
                <svg class="h-4 w-4 text-white" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" v-if="index === 2" />
                  <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" v-else-if="index === 1" />
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" v-else />
                </svg>
              </span>
              
              <div class="ml-4">
                <p class="text-xs font-semibold uppercase tracking-[0.14em] text-blue-600">{{ marco.etapa }}</p>
                <h3 class="mt-2 text-xl font-semibold tracking-tight text-slate-950 sm:text-2xl">{{ marco.titulo }}</h3>
                <p class="mt-3 max-w-2xl text-base leading-8 text-slate-600">{{ marco.descricao }}</p>
              </div>
            </article>
          </div>
        </div>
      </section>

      <!-- CTA FINAL -->
      <section class="mx-auto max-w-7xl px-5 py-20 sm:px-6 lg:px-8 lg:py-24">
        <div class="overflow-hidden rounded-[2rem] bg-[#172554] px-7 py-12 sm:px-10 lg:px-14 lg:py-16">
          <div class="grid items-center gap-10 lg:grid-cols-[1fr_0.82fr]">
            <div>
              <p class="text-sm font-semibold uppercase tracking-[0.16em] text-blue-200">Próximo passo</p>
              <h2 class="mt-4 max-w-2xl text-3xl font-semibold tracking-[-0.04em] text-white sm:text-4xl">
                Seu escritório já trabalha muito. Agora ele pode trabalhar com mais clareza.
              </h2>
              <p class="mt-5 max-w-xl text-base leading-8 text-white/70">
                Crie seu escritório na ContablyTask e comece a centralizar tarefas, responsabilidades e prazos em uma rotina mais organizada.
              </p>
              <RouterLink to="/cadastro" class="mt-8 inline-flex min-h-[48px] items-center justify-center rounded-xl bg-white px-6 py-3 text-sm font-semibold text-[#172554] transition-colors hover:bg-blue-50">
                Criar meu escritório
                <svg class="ml-2 h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                  <path d="M5 12h14" />
                  <path d="m13 6 6 6-6 6" />
                </svg>
              </RouterLink>
            </div>

            <div class="hidden rounded-2xl border border-white/10 bg-white/[0.08] p-4 shadow-2xl lg:block">
              <div class="rounded-xl bg-white p-4">
                <div class="flex items-center justify-between">
                  <div>
                    <div class="h-3 w-28 rounded bg-slate-800"></div>
                    <div class="mt-2 h-2 w-20 rounded bg-slate-200"></div>
                  </div>
                  <div class="h-7 w-16 rounded-lg bg-blue-600"></div>
                </div>
                <div class="mt-5 space-y-2">
                  <div class="flex items-center gap-3 rounded-lg bg-blue-50 px-3 py-3">
                    <span class="h-3 w-3 rounded-full bg-blue-500"></span>
                    <span class="h-2.5 flex-1 rounded bg-slate-200"></span>
                    <span class="h-5 w-12 rounded-full bg-blue-100"></span>
                  </div>
                  <div class="flex items-center gap-3 px-3 py-3">
                    <span class="h-3 w-3 rounded-full bg-emerald-500"></span>
                    <span class="h-2.5 flex-1 rounded bg-slate-200"></span>
                    <span class="h-5 w-12 rounded-full bg-emerald-100"></span>
                  </div>
                  <div class="flex items-center gap-3 px-3 py-3">
                    <span class="h-3 w-3 rounded-full bg-amber-400"></span>
                    <span class="h-2.5 flex-1 rounded bg-slate-200"></span>
                    <span class="h-5 w-12 rounded-full bg-amber-100"></span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>

    <footer class="border-t border-slate-200 bg-white">
      <div class="mx-auto flex max-w-7xl flex-col gap-5 px-5 py-8 text-sm text-slate-500 sm:px-6 md:flex-row md:items-center md:justify-between lg:px-8">
        <RouterLink to="/" class="font-semibold text-slate-800">
          Contably<span class="text-blue-600">Task</span>
        </RouterLink>
        <p>© {{ new Date().getFullYear() }} ContablyTask. Todos os direitos reservados.</p>
        <div class="flex flex-wrap gap-5">
          <RouterLink to="/sobre" class="transition-colors hover:text-slate-950">Sobre nós</RouterLink>
          <RouterLink to="/planos" class="transition-colors hover:text-slate-950">Planos</RouterLink>
          <RouterLink to="/contato" class="transition-colors hover:text-slate-950">Contato</RouterLink>
        </div>
      </div>
    </footer>
  </div>
</template>