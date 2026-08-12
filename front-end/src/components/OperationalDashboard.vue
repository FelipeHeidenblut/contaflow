<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

interface Task {
  id: string | number
  title: string
  description?: string
  status: string
  due_date?: string
  date?: string
  type: 'task' | 'receita_federal'
  grau_importancia?: string
}

interface TeamLoad {
  nome: string
  count: number
  percentual: number
}

const props = defineProps<{
  loading: boolean
  dashboard: {
    total_clientes: number
    tarefas_abertas: number
    tarefas_atrasadas: number
    plano: string
    status_pagamento: string
  }
  planLabel: string
  urgentCount: number
  completedCount: number
  awaitingCount: number
  onTimeCount: number
  totalStatus: number
  completionPercent: number
  onTimePercent: number
  overduePercent: number
  dailyFocus: Task[]
  upcoming: Task[]
  team: TeamLoad[]
  hasPremium: boolean
  completionRate: number
  fineRisk: { label: string; class: string; bar: string }
}>()

const formatDate = (date?: string) => {
  if (!date) return 'Sem prazo'
  const [, month, day] = date.split('-')
  return `${day}/${month}`
}

const dayName = (date?: string) => {
  if (!date) return ''
  return new Date(`${date}T00:00:00`)
    .toLocaleDateString('pt-BR', { weekday: 'short' })
    .replace('.', '')
}

const initials = (name: string) =>
  name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase()

const statusDot = (status: string) =>
  status === 'concluida'
    ? 'bg-emerald-500'
    : status === 'aguardando_cliente'
      ? 'bg-amber-400'
      : status === 'em_andamento'
        ? 'bg-[var(--ct-primary)]'
        : 'bg-slate-400'

const todayLabel = new Intl.DateTimeFormat('pt-BR', {
  weekday: 'long',
  day: '2-digit',
  month: 'long',
}).format(new Date())

const healthRingStyle = computed(() => {
  const completed = Math.max(0, Math.min(100, props.completionPercent))
  const onTime = Math.max(completed, Math.min(100, completed + props.onTimePercent))
  const overdue = Math.max(onTime, Math.min(100, onTime + props.overduePercent))
  return {
    background: `conic-gradient(#10b981 0% ${completed}%, var(--ct-primary) ${completed}% ${onTime}%, #ef4444 ${onTime}% ${overdue}%, var(--ct-muted) ${overdue}% 100%)`,
  }
})
</script>

<template>
  <div class="space-y-6">
    <header class="flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <div class="mb-2 flex items-center gap-3">
          <h1
            class="text-2xl font-semibold tracking-[-0.025em] text-[var(--ct-ink)] sm:text-[28px]"
          >
            Hoje no escritório
          </h1>
          <span
            class="rounded-md border border-[var(--ct-border)] bg-white px-2 py-1 text-[10px] font-bold uppercase tracking-[.1em] text-[var(--ct-primary)]"
            >{{ planLabel }}</span
          >
        </div>
        <p class="text-sm text-[var(--ct-text-muted)]">
          <span class="capitalize">{{ todayLabel }}</span> · Veja o que exige atenção agora.
        </p>
      </div>
      <div class="flex flex-wrap gap-2">
        <RouterLink
          to="/clientes?novo=1"
          class="rounded-lg border border-[var(--ct-border)] bg-white px-4 py-2.5 text-xs font-semibold text-[var(--ct-ink)] hover:bg-[var(--ct-muted)]"
          >Novo cliente</RouterLink
        >
        <RouterLink
          to="/obrigacoes?novo=1"
          class="rounded-lg bg-[var(--ct-primary)] px-4 py-2.5 text-xs font-semibold text-white hover:bg-[var(--ct-primary-hover)]"
          >Nova obrigação</RouterLink
        >
      </div>
    </header>

    <div
      v-if="!loading && dashboard.status_pagamento !== 'ativo'"
      class="flex items-center justify-between gap-4 rounded-xl border px-4 py-3"
      :class="
        dashboard.status_pagamento === 'inadimplente'
          ? 'border-red-200 bg-red-50'
          : 'border-amber-200 bg-amber-50'
      "
    >
      <div>
        <p
          class="text-sm font-semibold"
          :class="dashboard.status_pagamento === 'inadimplente' ? 'text-red-800' : 'text-amber-800'"
        >
          {{
            dashboard.status_pagamento === 'inadimplente'
              ? 'Assinatura requer atenção'
              : 'Pagamento em processamento'
          }}
        </p>
        <p class="mt-0.5 text-xs text-[var(--ct-text-muted)]">
          Verifique a assinatura para manter o acesso aos recursos.
        </p>
      </div>
      <RouterLink to="/faturamento" class="shrink-0 text-xs font-bold text-[var(--ct-primary)]"
        >Ver assinatura</RouterLink
      >
    </div>

    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <RouterLink
        v-for="(metric, index) in [
          {
            label: 'Clientes ativos',
            value: dashboard.total_clientes,
            to: '/clientes',
            helper: 'Carteira atual',
          },
          {
            label: 'Tarefas abertas',
            value: dashboard.tarefas_abertas,
            to: '/obrigacoes',
            helper: 'Em execução',
          },
          {
            label: 'Prioridade urgente',
            value: urgentCount,
            to: '/obrigacoes',
            helper: 'Exigem atenção',
          },
          {
            label: 'Tarefas atrasadas',
            value: dashboard.tarefas_atrasadas,
            to: '/obrigacoes',
            helper: 'Fora do prazo',
          },
        ]"
        :key="metric.label"
        :to="metric.to"
        class="group relative min-h-32 overflow-hidden rounded-xl border p-5 transition-colors"
        :class="
          index === 0
            ? 'border-[var(--ct-primary)] bg-[var(--ct-primary)] text-white hover:bg-[var(--ct-primary-hover)]'
            : 'border-[var(--ct-border)] bg-white hover:border-slate-300'
        "
      >
        <div v-if="loading" class="space-y-4">
          <div class="h-3 w-24 animate-pulse rounded bg-black/10"></div>
          <div class="h-8 w-14 animate-pulse rounded bg-black/10"></div>
        </div>
        <template v-else>
          <div class="flex items-start justify-between gap-3">
            <p
              class="text-[11px] font-semibold uppercase tracking-[.09em]"
              :class="index === 0 ? 'text-white/65' : 'text-[var(--ct-text-muted)]'"
            >
              {{ metric.label }}
            </p>
            <span class="text-sm opacity-40 transition-transform group-hover:translate-x-0.5"
              >↗</span
            >
          </div>
          <p
            class="mt-4 text-3xl font-semibold tabular-nums tracking-[-0.04em]"
            :class="index === 3 && metric.value ? 'text-red-600' : ''"
          >
            {{ metric.value }}
          </p>
          <p
            class="mt-2 text-[11px]"
            :class="index === 0 ? 'text-white/65' : 'text-[var(--ct-text-muted)]'"
          >
            {{ metric.helper }}
          </p>
        </template>
      </RouterLink>
    </section>

    <div class="grid gap-5 xl:grid-cols-12">
      <section
        class="overflow-hidden rounded-xl border border-[var(--ct-border)] bg-white xl:col-span-8"
      >
        <div class="flex items-center justify-between border-b border-[var(--ct-border)] px-5 py-4">
          <div>
            <h2 class="text-sm font-semibold text-[var(--ct-ink)]">Prioridades de hoje</h2>
            <p class="mt-1 text-xs text-[var(--ct-text-muted)]">
              Itens vencidos ou com atenção imediata.
            </p>
          </div>
          <RouterLink to="/obrigacoes" class="text-xs font-semibold text-[var(--ct-primary)]"
            >Ver todas</RouterLink
          >
        </div>
        <div v-if="loading" class="divide-y divide-[var(--ct-border)]">
          <div v-for="i in 3" :key="i" class="h-20 animate-pulse bg-[var(--ct-muted)]"></div>
        </div>
        <div v-else-if="dailyFocus.length" class="divide-y divide-[var(--ct-border)]">
          <RouterLink
            v-for="task in dailyFocus"
            :key="task.id"
            to="/obrigacoes"
            class="grid items-center gap-4 px-5 py-4 transition-colors hover:bg-[var(--ct-bg)] sm:grid-cols-[1.5rem_1fr_auto]"
          >
            <span
              class="flex h-6 w-6 items-center justify-center rounded-md"
              :class="
                task.grau_importancia === 'Urgente'
                  ? 'bg-red-50 text-red-600'
                  : task.status === 'aguardando_cliente'
                    ? 'bg-amber-50 text-amber-600'
                    : 'bg-[var(--ct-primary-soft)] text-[var(--ct-primary)]'
              "
              >•</span
            >
            <div class="min-w-0">
              <p class="truncate text-sm font-semibold text-[var(--ct-ink)]">{{ task.title }}</p>
              <p class="mt-1 text-xs text-[var(--ct-text-muted)]">
                {{
                  task.status === 'aguardando_cliente'
                    ? 'Aguardando cliente'
                    : task.grau_importancia || 'Prioridade normal'
                }}
              </p>
            </div>
            <div class="text-left sm:text-right">
              <p class="text-xs font-semibold text-[var(--ct-ink)]">
                {{ formatDate(task.due_date) }}
              </p>
              <p class="mt-1 text-[10px] uppercase tracking-wider text-slate-400">Prazo</p>
            </div>
          </RouterLink>
        </div>
        <div v-else class="px-5 py-14 text-center">
          <p class="text-sm font-semibold text-[var(--ct-ink)]">Nenhuma prioridade crítica</p>
          <p class="mt-1 text-xs text-[var(--ct-text-muted)]">
            O escritório está em dia com os itens mais urgentes.
          </p>
        </div>
      </section>

      <section class="rounded-xl border border-[var(--ct-border)] bg-white xl:col-span-4">
        <div class="border-b border-[var(--ct-border)] px-5 py-4">
          <h2 class="text-sm font-semibold text-[var(--ct-ink)]">Saúde da rotina</h2>
          <p class="mt-1 text-xs text-[var(--ct-text-muted)]">Situação das obrigações.</p>
        </div>
        <div class="p-5">
          <div v-if="loading" class="h-44 animate-pulse rounded-lg bg-[var(--ct-muted)]"></div>
          <template v-else>
            <div class="flex items-center gap-6">
              <div class="relative h-28 w-28 shrink-0 rounded-full" :style="healthRingStyle">
                <div
                  class="absolute inset-[11px] flex flex-col items-center justify-center rounded-full bg-white"
                >
                  <strong class="text-xl font-semibold">{{ completionPercent.toFixed(0) }}%</strong
                  ><span class="text-[9px] uppercase tracking-wider text-[var(--ct-text-muted)]"
                    >concluídas</span
                  >
                </div>
              </div>
              <dl class="min-w-0 flex-1 space-y-3 text-xs">
                <div class="flex items-center justify-between gap-3">
                  <dt class="flex items-center gap-2 text-[var(--ct-text-muted)]">
                    <span class="h-2 w-2 rounded-full bg-emerald-500"></span>Concluídas
                  </dt>
                  <dd class="font-semibold">{{ completedCount }}</dd>
                </div>
                <div class="flex items-center justify-between gap-3">
                  <dt class="flex items-center gap-2 text-[var(--ct-text-muted)]">
                    <span class="h-2 w-2 rounded-full bg-[var(--ct-primary)]"></span>Em dia
                  </dt>
                  <dd class="font-semibold">{{ onTimeCount }}</dd>
                </div>
                <div class="flex items-center justify-between gap-3">
                  <dt class="flex items-center gap-2 text-[var(--ct-text-muted)]">
                    <span class="h-2 w-2 rounded-full bg-red-500"></span>Atrasadas
                  </dt>
                  <dd class="font-semibold text-red-600">{{ dashboard.tarefas_atrasadas }}</dd>
                </div>
              </dl>
            </div>
            <div
              class="mt-5 flex items-center justify-between border-t border-[var(--ct-border)] pt-4"
            >
              <span class="text-xs text-[var(--ct-text-muted)]">Aguardando cliente</span
              ><strong class="text-sm text-amber-600">{{ awaitingCount }}</strong>
            </div>
          </template>
        </div>
      </section>

      <section
        class="overflow-hidden rounded-xl border border-[var(--ct-border)] bg-white xl:col-span-8"
      >
        <div class="flex items-center justify-between border-b border-[var(--ct-border)] px-5 py-4">
          <div>
            <h2 class="text-sm font-semibold text-[var(--ct-ink)]">Próximos 7 dias</h2>
            <p class="mt-1 text-xs text-[var(--ct-text-muted)]">
              Agenda consolidada de vencimentos.
            </p>
          </div>
          <RouterLink to="/calendario" class="text-xs font-semibold text-[var(--ct-primary)]"
            >Abrir calendário</RouterLink
          >
        </div>
        <div v-if="upcoming.length" class="divide-y divide-[var(--ct-border)]">
          <div
            v-for="task in upcoming"
            :key="`${task.type}-${task.id}`"
            class="grid items-center gap-3 px-5 py-3.5 sm:grid-cols-[1rem_1fr_auto]"
          >
            <span class="h-2 w-2 rounded-full" :class="statusDot(task.status)"></span>
            <div class="min-w-0">
              <p class="truncate text-sm font-medium text-[var(--ct-ink)]">{{ task.title }}</p>
              <p class="mt-0.5 text-[11px] text-[var(--ct-text-muted)]">
                {{ task.type === 'receita_federal' ? 'Prazo federal' : 'Tarefa interna' }}
              </p>
            </div>
            <div class="text-left sm:text-right">
              <p class="text-xs font-semibold text-[var(--ct-ink)]">
                {{ formatDate(task.due_date || task.date) }}
              </p>
              <p class="text-[10px] uppercase text-slate-400">
                {{ dayName(task.due_date || task.date) }}
              </p>
            </div>
          </div>
        </div>
        <p v-else class="px-5 py-12 text-center text-sm text-[var(--ct-text-muted)]">
          Nenhum prazo para os próximos dias.
        </p>
      </section>

      <section class="rounded-xl border border-[var(--ct-border)] bg-white xl:col-span-4">
        <div class="border-b border-[var(--ct-border)] px-5 py-4">
          <h2 class="text-sm font-semibold text-[var(--ct-ink)]">Capacidade da equipe</h2>
          <p class="mt-1 text-xs text-[var(--ct-text-muted)]">Tarefas abertas por responsável.</p>
        </div>
        <div v-if="team.length" class="divide-y divide-[var(--ct-border)] px-5">
          <div
            v-for="member in team.slice(0, 5)"
            :key="member.nome"
            class="flex items-center gap-3 py-3"
          >
            <span
              class="flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--ct-primary-soft)] text-[10px] font-bold text-[var(--ct-primary)]"
              >{{ initials(member.nome) }}</span
            >
            <div class="min-w-0 flex-1">
              <div class="mb-1.5 flex justify-between gap-3">
                <p class="truncate text-xs font-semibold text-[var(--ct-ink)]">{{ member.nome }}</p>
                <span class="text-[11px] text-[var(--ct-text-muted)]">{{ member.count }}</span>
              </div>
              <div class="h-1.5 rounded-full bg-[var(--ct-muted)]">
                <div
                  class="h-full rounded-full"
                  :class="member.count > 8 ? 'bg-red-500' : 'bg-[var(--ct-primary)]'"
                  :style="{ width: member.percentual + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>
        <p v-else class="px-5 py-12 text-center text-sm text-[var(--ct-text-muted)]">
          Sem tarefas atribuídas.
        </p>
      </section>
    </div>

    <section
      class="flex flex-col gap-4 rounded-xl border border-[var(--ct-border)] bg-white px-5 py-4 sm:flex-row sm:items-center sm:justify-between"
    >
      <div>
        <div class="flex items-center gap-2">
          <h2 class="text-sm font-semibold text-[var(--ct-ink)]">Resumo mensal</h2>
          <span
            class="rounded bg-[var(--ct-primary-soft)] px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-wider text-[var(--ct-primary)]"
            >Premium</span
          >
        </div>
        <p class="mt-1 text-xs text-[var(--ct-text-muted)]">
          Conclusão, risco e entregas do escritório.
        </p>
      </div>
      <div v-if="hasPremium" class="flex flex-wrap gap-8">
        <div>
          <p class="text-[10px] uppercase tracking-wider text-slate-400">Conclusão</p>
          <p class="mt-1 text-lg font-semibold">{{ completionRate }}%</p>
        </div>
        <div>
          <p class="text-[10px] uppercase tracking-wider text-slate-400">Risco</p>
          <p class="mt-1 text-lg font-semibold" :class="fineRisk.class">{{ fineRisk.label }}</p>
        </div>
        <div>
          <p class="text-[10px] uppercase tracking-wider text-slate-400">Entregas</p>
          <p class="mt-1 text-lg font-semibold text-[var(--ct-primary)]">{{ completedCount }}</p>
        </div>
      </div>
      <RouterLink v-else to="/faturamento" class="text-xs font-semibold text-[var(--ct-primary)]"
        >Conhecer planos →</RouterLink
      >
    </section>
  </div>
</template>
