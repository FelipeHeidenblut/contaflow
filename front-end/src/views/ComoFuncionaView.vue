<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

const route = useRoute()
const isActive = (path: string) => route.path === path

const etapas = [
  {
    numero: '01',
    titulo: 'Diagnóstico da rotina',
    resumo: 'Antes de propor qualquer fluxo, a gente parte da operação real do escritório.',
    bullets: [
      'Entendemos como tarefas, documentos e prazos estão organizados hoje',
      'Mapeamos gargalos, retrabalho e pontos sem visibilidade',
      'Separamos sintoma operacional da causa real do problema',
    ],
    entrega:
      'Uma leitura mais clara da rotina do escritório, com os principais pontos de atrito visíveis.',
  },
  {
    numero: '02',
    titulo: 'Estruturação da operação',
    resumo: 'Depois do diagnóstico, a ContablyTask entra como base de organização do trabalho.',
    bullets: [
      'Organizamos clientes, tarefas, responsáveis e documentos em um fluxo único',
      'Definimos uma lógica mais clara para acompanhamento da execução',
      'Reduzimos a dependência de controles paralelos e dispersos',
    ],
    entrega:
      'Uma estrutura operacional mais previsível, com menos improviso e mais clareza para a equipe.',
  },
  {
    numero: '03',
    titulo: 'Acompanhamento do dia a dia',
    resumo: 'A plataforma passa a apoiar a rotina operacional de forma prática.',
    bullets: [
      'A equipe enxerga o que precisa ser feito e por quem',
      'A gestão acompanha prazos, andamento e pendências com mais facilidade',
      'Os documentos deixam de ficar espalhados entre ferramentas e conversas',
    ],
    entrega:
      'Uma rotina mais organizada, com acompanhamento contínuo e menos retrabalho.',
  },
  {
    numero: '04',
    titulo: 'Evolução com crescimento',
    resumo: 'Conforme a operação cresce, a estrutura acompanha esse novo nível de complexidade.',
    bullets: [
      'Mais clientes e mais usuários sem perder visibilidade',
      'Mais controle sobre distribuição da equipe',
      'Mais base para decidir quando ajustar plano, processo ou acompanhamento',
    ],
    entrega:
      'Uma operação com mais capacidade de escala e mais previsibilidade no crescimento.',
  },
]

const principios = [
  {
    titulo: 'Partimos do que já existe',
    texto:
      'A proposta não é obrigar o escritório a começar do zero, mas organizar melhor a operação que já acontece no dia a dia.',
    icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10'
  },
  {
    titulo: 'Organização antes de complexidade',
    texto:
      'Antes de pensar em recursos avançados, o foco é criar uma base operacional clara para execução e acompanhamento.',
    icon: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
  },
  {
    titulo: 'Clareza para equipe e gestão',
    texto:
      'A plataforma precisa funcionar para quem executa e também para quem acompanha a operação como um todo.',
    icon: 'M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z'
  },
]

const perguntas = [
  {
    pergunta: 'A ContablyTask exige mudar toda a rotina do escritório?',
    resposta:
      'Não. A ideia é estruturar melhor a operação existente, reduzindo dispersão e dando mais clareza para o trabalho diário.',
  },
  {
    pergunta: 'Essa página substitui uma demonstração?',
    resposta:
      'Não completamente. Ela mostra a lógica de funcionamento, mas a demonstração ajuda a entender como isso aparece na prática dentro da plataforma.',
  },
  {
    pergunta: 'Serve para escritórios pequenos?',
    resposta:
      'Sim. A lógica de organização atende desde profissionais autônomos até escritórios em crescimento e operações maiores.',
  },
]

const jsonLd = computed(() =>
  JSON.stringify({
    '@context': 'https://schema.org',
    '@type': 'WebPage',
    name: 'Como funciona | ContablyTask',
    url: 'https://contablytask.com.br/como-funciona',
    description:
      'Entenda como a ContablyTask organiza a rotina operacional de escritórios contábeis em etapas claras.',
  }),
)

const openFaq = ref<number | null>(0)
const toggleFaq = (index: number) => {
  openFaq.value = openFaq.value === index ? null : index
}
</script>

<template>
  <div class="min-h-screen bg-[var(--ct-bg)] text-[var(--ct-ink)]">
    <Teleport to="head">
      <title>Como funciona | ContablyTask</title>
      <meta
        name="description"
        content="Veja como a ContablyTask organiza a rotina do escritório contábil em etapas claras, com mais visibilidade, controle e previsibilidade."
      />
      <meta property="og:title" content="Como funciona | ContablyTask" />
      <meta
        property="og:description"
        content="Conheça a lógica de funcionamento da ContablyTask e entenda como a plataforma estrutura a operação contábil."
      />
      <meta property="og:type" content="website" />
      <component :is="'script'" type="application/ld+json" v-html="jsonLd" />
    </Teleport>

    <header class="sticky top-0 z-50 border-b border-[var(--ct-border)] bg-white/85 backdrop-blur-lg">
      <div class="mx-auto flex h-16 max-w-[1200px] items-center justify-between px-6">
        <RouterLink to="/" class="flex items-center gap-2.5">
          <div class="flex h-9 w-9 items-center justify-center rounded-[10px] bg-[var(--ct-navy)]">
            <svg viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.5" class="h-5 w-5" aria-hidden="true">
              <path d="M9 11l3 3L22 4" />
              <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
            </svg>
          </div>
          <span class="text-lg font-extrabold tracking-tight text-[var(--ct-ink)]">
            Contably<span class="text-[var(--ct-primary)]">Task</span>
          </span>
        </RouterLink>

        <nav class="hidden items-center gap-1 lg:flex">
          <RouterLink to="/" class="rounded-lg px-3 py-2 text-[15px] font-medium transition-colors" :class="isActive('/') ? 'text-[var(--ct-ink)]' : 'text-[var(--ct-text-muted)] hover:text-[var(--ct-ink)]'">Início</RouterLink>
          <RouterLink to="/sobre" class="rounded-lg px-3 py-2 text-[15px] font-medium transition-colors" :class="isActive('/sobre') ? 'text-[var(--ct-ink)]' : 'text-[var(--ct-text-muted)] hover:text-[var(--ct-ink)]'">Sobre nós</RouterLink>
          <RouterLink to="/planos" class="rounded-lg px-3 py-2 text-[15px] font-medium transition-colors" :class="isActive('/planos') ? 'text-[var(--ct-ink)]' : 'text-[var(--ct-text-muted)] hover:text-[var(--ct-ink)]'">Planos</RouterLink>
          <RouterLink to="/como-funciona" class="rounded-lg px-3 py-2 text-[15px] font-medium transition-colors" :class="isActive('/como-funciona') ? 'text-[var(--ct-ink)]' : 'text-[var(--ct-text-muted)] hover:text-[var(--ct-ink)]'">Como funciona</RouterLink>
          <RouterLink to="/contato" class="rounded-lg px-3 py-2 text-[15px] font-medium transition-colors" :class="isActive('/contato') ? 'text-[var(--ct-ink)]' : 'text-[var(--ct-text-muted)] hover:text-[var(--ct-ink)]'">Contato</RouterLink>
        </nav>

        <div class="flex items-center gap-2">
          <RouterLink to="/login" class="rounded-lg px-3 py-2 text-sm font-medium text-[var(--ct-ink)] transition-colors hover:bg-[var(--ct-muted)]">Login</RouterLink>
          <RouterLink to="/cadastro" class="rounded-lg bg-[var(--ct-primary)] px-4 py-2 text-sm font-bold text-white transition-colors hover:bg-[var(--ct-primary-hover)]">Começar grátis</RouterLink>
        </div>
      </div>
    </header>

    <main>
      <!-- HERO -->
      <section class="border-b border-[var(--ct-border)] bg-white">
        <div class="mx-auto max-w-7xl px-6 py-20 lg:px-8 lg:py-24">
          <div class="grid gap-10 lg:grid-cols-[1.05fr_0.95fr] lg:items-center">
            <div>
              <p class="mb-4 text-sm font-semibold uppercase tracking-[0.14em] text-[var(--ct-primary)]">Como funciona</p>
              <h1 class="max-w-4xl text-4xl font-semibold tracking-tight text-[var(--ct-ink)] md:text-5xl">
                A ContablyTask organiza a operação do escritório a partir do que acontece de verdade no dia a dia.
              </h1>
              <p class="mt-6 max-w-2xl text-base leading-8 text-[var(--ct-text-muted)] md:text-lg">
                Em vez de começar pela ferramenta, começamos pela rotina. A lógica é entender a operação, estruturar o fluxo de trabalho e dar visibilidade contínua para tarefas, documentos, responsáveis e prazos.
              </p>
            </div>

            <div class="rounded-[28px] border border-[var(--ct-border)] bg-[var(--ct-surface)] p-7 shadow-sm transition-all hover:shadow-md">
              <p class="text-sm font-semibold text-[var(--ct-ink)]">Em resumo</p>
              <div class="mt-5 space-y-4">
                <div class="flex items-start gap-4 rounded-2xl border border-[var(--ct-border)] bg-white p-5 transition-colors hover:border-[var(--ct-primary)]">
                  <div class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-blue-50 text-[var(--ct-primary)]">
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" /></svg>
                  </div>
                  <div>
                    <p class="text-sm font-semibold text-[var(--ct-ink)]">1. Entendemos a rotina</p>
                    <p class="mt-2 text-sm leading-7 text-[var(--ct-text-muted)]">Onde há gargalo, retrabalho e falta de visibilidade.</p>
                  </div>
                </div>
                <div class="flex items-start gap-4 rounded-2xl border border-[var(--ct-border)] bg-white p-5 transition-colors hover:border-[var(--ct-primary)]">
                  <div class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-blue-50 text-[var(--ct-primary)]">
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
                  </div>
                  <div>
                    <p class="text-sm font-semibold text-[var(--ct-ink)]">2. Estruturamos o fluxo</p>
                    <p class="mt-2 text-sm leading-7 text-[var(--ct-text-muted)]">Clientes, tarefas, equipe e documentos passam a seguir uma lógica mais clara.</p>
                  </div>
                </div>
                <div class="flex items-start gap-4 rounded-2xl border border-[var(--ct-border)] bg-white p-5 transition-colors hover:border-[var(--ct-primary)]">
                  <div class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-blue-50 text-[var(--ct-primary)]">
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
                  </div>
                  <div>
                    <p class="text-sm font-semibold text-[var(--ct-ink)]">3. Acompanhamos melhor</p>
                    <p class="mt-2 text-sm leading-7 text-[var(--ct-text-muted)]">O escritório ganha previsibilidade para operar e crescer com menos improviso.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ETAPAS -->
      <section class="mx-auto max-w-7xl px-6 py-20 lg:px-8 lg:py-24">
        <div class="max-w-3xl">
          <p class="text-sm font-semibold uppercase tracking-[0.14em] text-[var(--ct-primary)]">Etapas</p>
          <h2 class="mt-3 text-3xl font-semibold tracking-tight text-[var(--ct-ink)]">Um processo simples, mas orientado à operação real.</h2>
        </div>

        <div class="mt-12 space-y-6">
          <article v-for="etapa in etapas" :key="etapa.numero" class="flex flex-col gap-6 rounded-[30px] border border-[var(--ct-border)] bg-white p-7 shadow-sm transition-all hover:shadow-lg sm:flex-row sm:gap-8">
            <div class="flex-shrink-0">
              <span class="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-[var(--ct-primary-soft)] text-lg font-semibold text-[var(--ct-primary)]">
                {{ etapa.numero }}
              </span>
            </div>

            <div class="grid flex-1 gap-6 lg:grid-cols-[1.1fr_0.9fr]">
              <div>
                <h3 class="text-2xl font-semibold tracking-tight text-[var(--ct-ink)]">{{ etapa.titulo }}</h3>
                <p class="mt-4 text-base leading-8 text-[var(--ct-text-muted)]">{{ etapa.resumo }}</p>

                <ul class="mt-6 space-y-4">
                  <li v-for="item in etapa.bullets" :key="item" class="flex items-start gap-3 text-sm leading-7 text-[var(--ct-text-muted)]">
                    <span class="mt-2 h-2.5 w-2.5 flex-shrink-0 rounded-full bg-[var(--ct-primary)]"></span>
                    <span>{{ item }}</span>
                  </li>
                </ul>
              </div>

              <aside class="flex h-full flex-col rounded-3xl border border-[var(--ct-border)] bg-[var(--ct-surface)] p-6">
                <div class="flex items-center gap-2">
                  <svg class="h-4 w-4 text-[var(--ct-primary)]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" /></svg>
                  <p class="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--ct-primary)]">Entrega</p>
                </div>
                <p class="mt-3 text-sm leading-7 text-[var(--ct-ink)]">{{ etapa.entrega }}</p>
              </aside>
            </div>
          </article>
        </div>
      </section>

      <!-- PRINCÍPIOS -->
      <section class="border-y border-[var(--ct-border)] bg-white">
        <div class="mx-auto max-w-7xl px-6 py-20 lg:px-8 lg:py-24">
          <div class="grid gap-10 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
            <div>
              <p class="text-sm font-semibold uppercase tracking-[0.14em] text-[var(--ct-primary)]">Princípios do método</p>
              <h2 class="mt-3 text-3xl font-semibold tracking-tight text-[var(--ct-ink)]">
                A ferramenta faz mais sentido quando respeita a lógica da operação.
              </h2>
            </div>

            <div class="grid gap-6 md:grid-cols-3">
              <article v-for="item in principios" :key="item.titulo" class="flex h-full flex-col rounded-3xl border border-[var(--ct-border)] bg-[var(--ct-surface)] p-7 transition-all hover:-translate-y-1 hover:shadow-lg">
                <div class="mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--ct-primary-soft)] text-[var(--ct-primary)]">
                  <svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" :d="item.icon" /></svg>
                </div>
                <h3 class="text-lg font-semibold tracking-tight text-[var(--ct-ink)]">{{ item.titulo }}</h3>
                <p class="mt-3 text-sm leading-7 text-[var(--ct-text-muted)]">{{ item.texto }}</p>
              </article>
            </div>
          </div>
        </div>
      </section>

      <!-- FAZ SENTIDO + FAQ -->
      <section class="mx-auto max-w-7xl px-6 py-20 lg:px-8 lg:py-24">
        <div class="grid gap-8 lg:grid-cols-[0.95fr_1.05fr] lg:items-stretch">
          <div class="flex flex-col rounded-[28px] border border-[var(--ct-border)] bg-[var(--ct-surface)] p-7">
            <p class="text-sm font-semibold uppercase tracking-[0.14em] text-[var(--ct-primary)]">Quando isso faz sentido</p>
            <h2 class="mt-3 text-3xl font-semibold tracking-tight text-[var(--ct-ink)]">
              Essa lógica funciona melhor para escritórios que querem sair da operação dispersa.
            </h2>
            <p class="mt-4 text-base leading-8 text-[var(--ct-text-muted)]">
              Se hoje o controle depende de planilhas paralelas, mensagens soltas, documentos espalhados e pouca visibilidade sobre o andamento das tarefas, essa página descreve exatamente o tipo de estrutura que a ContablyTask busca criar.
            </p>

            <div class="mt-auto flex flex-col gap-3 pt-8 sm:flex-row">
              <RouterLink to="/planos" class="inline-flex min-h-[48px] items-center justify-center rounded-xl bg-[var(--ct-primary)] px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-[var(--ct-primary-hover)]">
                Ver planos
              </RouterLink>
              <RouterLink to="/contato" class="inline-flex min-h-[48px] items-center justify-center rounded-xl border border-[var(--ct-border)] px-6 py-3 text-sm font-semibold text-[var(--ct-ink)] transition-colors hover:border-[var(--ct-primary)] hover:text-[var(--ct-primary)]">
                Falar com nosso time
              </RouterLink>
            </div>
          </div>

          <div class="flex flex-col rounded-[28px] border border-[var(--ct-border)] bg-white p-7 shadow-sm">
            <p class="text-sm font-semibold uppercase tracking-[0.14em] text-[var(--ct-primary)]">Dúvidas frequentes</p>

            <div class="mt-6 space-y-3">
              <div v-for="(item, index) in perguntas" :key="item.pergunta" class="overflow-hidden rounded-2xl border border-[var(--ct-border)] bg-[var(--ct-surface)] transition-all hover:border-blue-300 hover:shadow-sm">
                <button 
                  @click="toggleFaq(index)" 
                  class="flex w-full items-center justify-between gap-4 p-5 text-left"
                  :class="openFaq === index ? 'bg-slate-50' : 'bg-[var(--ct-surface)]'"
                >
                  <h3 class="text-base font-semibold text-[var(--ct-ink)]">
                    {{ item.pergunta }}
                  </h3>
                  <span class="flex-shrink-0 text-[var(--ct-primary)] transition-transform duration-300" :class="openFaq === index ? 'rotate-45' : 'rotate-0'">
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
                  </span>
                </button>
                <div 
                  v-show="openFaq === index" 
                  class="grid transition-all duration-300 ease-in-out"
                  :class="openFaq === index ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'"
                >
                  <div class="overflow-hidden">
                    <p class="px-5 pb-5 text-sm leading-7 text-[var(--ct-text-muted)]">{{ item.resposta }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- CTA FINAL -->
      <section class="mx-auto max-w-5xl px-6 py-20 lg:px-8 lg:py-24">
        <div class="rounded-[32px] border border-[var(--ct-border)] bg-[var(--ct-navy)] px-8 py-10 text-white md:px-12 md:py-14">
          <p class="text-sm font-semibold uppercase tracking-[0.14em] text-[#93C5FD]">Próximo passo</p>
          <h2 class="mt-3 max-w-2xl text-3xl font-semibold tracking-tight md:text-4xl">
            Se a sua operação precisa de mais clareza, previsibilidade e organização, esse é o momento de avançar.
          </h2>
          <p class="mt-5 max-w-2xl text-sm leading-8 text-white/70 md:text-base">
            Conheça os planos ou fale com nosso time para entender qual estrutura faz mais sentido para o seu momento.
          </p>

          <div class="mt-8 flex flex-col gap-3 sm:flex-row">
            <RouterLink to="/cadastro" class="inline-flex min-h-[48px] items-center justify-center rounded-xl bg-white px-6 py-3 text-sm font-semibold text-[var(--ct-navy)] transition-colors hover:bg-slate-100">
              Começar grátis
            </RouterLink>
            <RouterLink to="/contato" class="inline-flex min-h-[48px] items-center justify-center rounded-xl border border-white/20 px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-white/10">
              Falar com nosso time
            </RouterLink>
          </div>
        </div>
      </section>
    </main>

    <footer class="border-t border-[var(--ct-border)] bg-white">
      <div class="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-8 text-sm text-[var(--ct-text-muted)] md:flex-row md:items-center md:justify-between lg:px-8">
        <p>© ContablyTask. Organização operacional para escritórios contábeis.</p>
        <div class="flex flex-wrap gap-5">
          <RouterLink to="/sobre" class="hover:text-[var(--ct-ink)]">Sobre nós</RouterLink>
          <RouterLink to="/planos" class="hover:text-[var(--ct-ink)]">Planos</RouterLink>
          <RouterLink to="/como-funciona" class="hover:text-[var(--ct-ink)]">Como funciona</RouterLink>
          <RouterLink to="/contato" class="hover:text-[var(--ct-ink)]">Contato</RouterLink>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
:global(:root) {
  --ct-bg: #f8fafc;
  --ct-surface: #f8fbff;
  --ct-muted: #f1f5f9;
  --ct-border: #e2e8f0;
  --ct-ink: #0f172a;
  --ct-text-muted: #64748b;
  --ct-primary: #2563eb;
  --ct-primary-hover: #1d4ed8;
  --ct-primary-soft: #dbeafe;
  --ct-navy: #172554;
}

:global(body) {
  background: var(--ct-bg);
  color: var(--ct-ink);
}
</style>