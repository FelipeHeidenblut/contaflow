<script setup lang="ts">
import { RouterLink } from 'vue-router'
import PublicLayout from '@/components/PublicLayout.vue'

const benefits = [
  {
    number: '01',
    title: 'Prazos visíveis',
    description:
      'Obrigações, vencimentos e prioridades organizados em uma rotina que toda a equipe entende.',
  },
  {
    number: '02',
    title: 'Clientes centralizados',
    description:
      'Dados, documentos e histórico de cada empresa reunidos sem depender de planilhas paralelas.',
  },
  {
    number: '03',
    title: 'Equipe coordenada',
    description:
      'Responsáveis e carga de trabalho visíveis para distribuir demandas com mais segurança.',
  },
]

const workflow = [
  [
    'Cadastre ou importe',
    'Traga sua carteira de clientes e mantenha os dados essenciais em um único lugar.',
  ],
  ['Organize a rotina', 'Crie obrigações, defina prazos, responsáveis e nível de importância.'],
  [
    'Acompanhe a execução',
    'Veja o que está pendente, atrasado, aguardando o cliente ou concluído.',
  ],
]

const tasks = [
  {
    title: 'DCTFWeb · Padaria Central',
    meta: 'Hoje · Ana Costa',
    status: 'Em andamento',
    tone: 'blue',
  },
  {
    title: 'Folha de pagamento · Grupo Norte',
    meta: 'Amanhã · Rafael Lima',
    status: 'Pendente',
    tone: 'slate',
  },
  {
    title: 'DAS · Martins Comércio',
    meta: '22 ago · Ana Costa',
    status: 'Aguardando',
    tone: 'amber',
  },
]
</script>

<template>
  <PublicLayout>
    <section class="border-b border-[var(--ct-border)] bg-white">
      <div class="ct-container grid items-center gap-14 py-16 lg:grid-cols-[0.9fr_1.1fr] lg:py-24">
        <div>
          <p class="ct-eyebrow">Gestão para escritórios contábeis</p>
          <h1 class="ct-display mt-5">Sua operação contábil sem tarefas espalhadas.</h1>
          <p class="ct-body-lg mt-6">
            Centralize clientes, obrigações, documentos e responsáveis em um fluxo simples para o
            escritório inteiro.
          </p>
          <div class="mt-8 flex flex-col gap-3 sm:flex-row">
            <RouterLink to="/cadastro" class="ct-button-primary">Criar conta grátis</RouterLink>
            <RouterLink to="/como-funciona" class="ct-button-secondary"
              >Conhecer o produto</RouterLink
            >
          </div>
          <p class="mt-5 text-xs text-[var(--ct-text-muted)]">
            Comece no plano gratuito. Sem fidelidade.
          </p>
        </div>

        <div class="overflow-hidden rounded-xl border border-slate-300 bg-[var(--ct-bg)]">
          <div
            class="flex h-11 items-center justify-between border-b border-[var(--ct-border)] bg-white px-4"
          >
            <div class="flex items-center gap-2 text-xs font-semibold text-slate-700">
              <span class="h-2 w-2 rounded-full bg-emerald-500"></span> Central de trabalho
            </div>
            <span class="text-[11px] text-slate-400">Agosto de 2026</span>
          </div>
          <div class="grid md:grid-cols-[156px_1fr]">
            <aside
              class="hidden border-r border-[var(--ct-border)] bg-[var(--ct-navy)] p-4 text-white md:block"
            >
              <div class="mb-6 text-xs font-semibold">ContablyTask</div>
              <div class="space-y-1 text-[11px]">
                <p class="rounded-md bg-white/10 px-2 py-2">Visão geral</p>
                <p class="px-2 py-2 text-white/55">Clientes</p>
                <p class="px-2 py-2 text-white/55">Obrigações</p>
                <p class="px-2 py-2 text-white/55">Documentos</p>
                <p class="px-2 py-2 text-white/55">Calendário</p>
              </div>
            </aside>
            <div class="p-4 sm:p-6">
              <div class="mb-5 flex items-end justify-between">
                <div>
                  <p class="text-xs text-slate-400">Segunda-feira, 10 de agosto</p>
                  <p class="mt-1 text-base font-semibold text-slate-900">
                    Prioridades do escritório
                  </p>
                </div>
                <span
                  class="rounded-md bg-[var(--ct-primary)] px-2.5 py-1.5 text-[10px] font-semibold text-white"
                  >Nova obrigação</span
                >
              </div>
              <div
                class="mb-5 grid grid-cols-3 overflow-hidden rounded-lg border border-[var(--ct-border)] bg-white"
              >
                <div class="border-r border-[var(--ct-border)] p-3">
                  <p class="text-[9px] uppercase tracking-wider text-slate-400">Clientes</p>
                  <p class="mt-1 text-xl font-semibold">38</p>
                </div>
                <div class="border-r border-[var(--ct-border)] p-3">
                  <p class="text-[9px] uppercase tracking-wider text-slate-400">Em aberto</p>
                  <p class="mt-1 text-xl font-semibold">12</p>
                </div>
                <div class="p-3">
                  <p class="text-[9px] uppercase tracking-wider text-slate-400">Atrasadas</p>
                  <p class="mt-1 text-xl font-semibold text-red-600">2</p>
                </div>
              </div>
              <div class="overflow-hidden rounded-lg border border-[var(--ct-border)] bg-white">
                <div class="border-b border-[var(--ct-border)] px-4 py-3 text-xs font-semibold">
                  Próximas obrigações
                </div>
                <div
                  v-for="task in tasks"
                  :key="task.title"
                  class="flex items-center justify-between gap-4 border-b border-[var(--ct-border)] px-4 py-3 last:border-0"
                >
                  <div class="min-w-0">
                    <p class="truncate text-xs font-medium text-slate-800">{{ task.title }}</p>
                    <p class="mt-1 text-[10px] text-slate-400">{{ task.meta }}</p>
                  </div>
                  <span
                    class="shrink-0 rounded-md px-2 py-1 text-[9px] font-semibold"
                    :class="
                      task.tone === 'blue'
                        ? 'bg-[var(--ct-primary-soft)] text-[var(--ct-primary)]'
                        : task.tone === 'amber'
                          ? 'bg-amber-50 text-amber-700'
                          : 'bg-slate-100 text-slate-600'
                    "
                    >{{ task.status }}</span
                  >
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="ct-section">
      <div class="ct-container">
        <div class="max-w-2xl">
          <p class="ct-eyebrow">Uma rotina mais previsível</p>
          <h2 class="ct-section-title mt-4">O essencial para trabalhar com clareza.</h2>
        </div>
        <div
          class="mt-12 grid border-y border-[var(--ct-border)] md:grid-cols-3 md:divide-x md:divide-[var(--ct-border)]"
        >
          <article
            v-for="benefit in benefits"
            :key="benefit.number"
            class="border-b border-[var(--ct-border)] px-0 py-7 last:border-0 md:border-b-0 md:px-7 md:first:pl-0 md:last:pr-0"
          >
            <p class="text-xs font-semibold text-[var(--ct-primary)]">{{ benefit.number }}</p>
            <h3 class="mt-5 text-lg font-semibold tracking-tight">{{ benefit.title }}</h3>
            <p class="mt-2 text-sm leading-6 text-[var(--ct-text-muted)]">
              {{ benefit.description }}
            </p>
          </article>
        </div>
      </div>
    </section>

    <section class="border-y border-[var(--ct-border)] bg-white">
      <div class="ct-container grid gap-14 py-16 lg:grid-cols-2 lg:py-24">
        <div>
          <p class="ct-eyebrow">Do cadastro à entrega</p>
          <h2 class="ct-section-title mt-4">Um fluxo que acompanha o trabalho real.</h2>
          <p class="ct-body-lg mt-5">
            A plataforma dá contexto para cada demanda sem transformar a operação em um processo
            complicado.
          </p>
        </div>
        <ol class="border-t border-[var(--ct-border)]">
          <li
            v-for="(step, index) in workflow"
            :key="step[0]"
            class="grid grid-cols-[2.5rem_1fr] gap-4 border-b border-[var(--ct-border)] py-6"
          >
            <span class="text-xs font-semibold text-[var(--ct-primary)]">0{{ index + 1 }}</span>
            <div>
              <h3 class="font-semibold">{{ step[0] }}</h3>
              <p class="mt-2 text-sm leading-6 text-[var(--ct-text-muted)]">{{ step[1] }}</p>
            </div>
          </li>
        </ol>
      </div>
    </section>

    <section class="ct-section">
      <div class="ct-container grid gap-8 lg:grid-cols-[1fr_auto] lg:items-end">
        <div>
          <p class="ct-eyebrow">Feito para começar simples</p>
          <h2 class="ct-section-title mt-4">Organize o escritório hoje e evolua no seu ritmo.</h2>
          <p class="ct-body-lg mt-5">
            O plano gratuito atende a operação inicial. Quando a equipe e a carteira crescerem, a
            estrutura já estará pronta.
          </p>
        </div>
        <RouterLink to="/planos" class="ct-button-secondary">Comparar planos</RouterLink>
      </div>
    </section>

    <section class="bg-[var(--ct-navy)] text-white">
      <div
        class="ct-container flex flex-col items-start justify-between gap-8 py-14 md:flex-row md:items-center"
      >
        <div>
          <h2 class="text-2xl font-semibold tracking-tight">
            Menos improviso. Mais controle da rotina.
          </h2>
          <p class="mt-2 text-sm text-white/65">
            Crie seu escritório e comece a organizar as próximas entregas.
          </p>
        </div>
        <RouterLink to="/cadastro" class="ct-button-primary">Começar gratuitamente</RouterLink>
      </div>
    </section>
  </PublicLayout>
</template>
