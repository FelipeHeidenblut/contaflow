<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'

interface Task {
  id: string | number
  title: string
  description?: string
  status: string
  due_date?: string
  grau_importancia?: string
  client_id?: string | number
  assigned_to?: string | number | null
  created_at?: string
  is_recurring?: boolean
  recurrence_day?: number | null
}

interface Client {
  id: string | number
  razao_social?: string
  nome?: string
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
  userName: string
  tasks: Task[]
  clients: Client[]
  members: { id: string | number; name: string }[]
  lookupsReady: boolean
  userId: string
  role: string
  readOnly: boolean
}>()

const clock = ref(new Date())
let timer: ReturnType<typeof setInterval> | undefined
onMounted(() => {
  timer = setInterval(() => {
    clock.value = new Date()
  }, 60000)
})
onUnmounted(() => clearInterval(timer))
const todayIso = computed(() =>
  new Intl.DateTimeFormat('en-CA', {
    timeZone: 'America/Sao_Paulo',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(clock.value),
)
const scope = ref<'all' | 'mine'>('all')
const scopeLabel = computed(() =>
  scope.value === 'mine'
    ? 'Minhas tarefas'
    : ['admin', 'gerente'].includes(props.role)
      ? 'Todo o escritório'
      : 'Minha carteira',
)
const scopedTasks = computed(() =>
  scope.value === 'mine'
    ? props.tasks.filter((task) => String(task.assigned_to) === props.userId)
    : props.tasks,
)
const canManage = computed(() => ['admin', 'gerente'].includes(props.role))
const canWrite = computed(() => !props.readOnly && !hasCriticalBillingStatus.value)
const taskLink = (task: Task) => ({ path: '/obrigacoes', query: { tarefa: String(task.id) } })
const assigneeName = (task: Task) =>
  props.members.find((member) => String(member.id) === String(task.assigned_to))?.name ||
  (task.assigned_to ? 'Responsável indisponível' : 'Sem responsável')
const steps = computed(() => [
  { label: 'Cadastre um cliente', done: props.clients.length > 0, to: '/clientes?novo=1' },
  { label: 'Crie uma obrigação', done: props.tasks.length > 0, to: '/obrigacoes?novo=1' },
  ...(props.dashboard.plano !== 'free'
    ? [
        {
          label: 'Convide sua equipe',
          done: props.members.some((member) => String(member.id) !== props.userId),
          to: '/membros?novo=1',
        },
      ]
    : []),
])
const completedSteps = computed(() => steps.value.filter((step) => step.done).length)
const team = computed(() =>
  props.members
    .map((member) => {
      const tasks = activeTasks.value.filter(
        (task) => String(task.assigned_to) === String(member.id),
      )
      return {
        id: member.id,
        nome: member.name,
        count: tasks.length,
        overdue: tasks.filter((task) => task.due_date && task.due_date < todayIso.value).length,
      }
    })
    .sort((a, b) => b.overdue - a.overdue || b.count - a.count),
)
const unassigned = computed(() => activeTasks.value.filter((task) => !task.assigned_to).length)

const greeting = computed(() => {
  const hour = Number(
    new Intl.DateTimeFormat('pt-BR', {
      timeZone: 'America/Sao_Paulo',
      hour: 'numeric',
      hourCycle: 'h23',
    }).format(clock.value),
  )
  if (hour < 12) return 'Bom dia'
  if (hour < 18) return 'Boa tarde'
  return 'Boa noite'
})

const firstName = computed(() => props.userName.trim().split(/\s+/)[0] || 'Olá')

const hasCriticalBillingStatus = computed(() =>
  ['inadimplente', 'estornado', 'cancelado', 'chargeback'].includes(
    props.dashboard.status_pagamento,
  ),
)

const billingAlertTitle = computed(() => {
  const labels: Record<string, string> = {
    inadimplente: 'Assinatura requer atenção',
    estornado: 'Pagamento estornado',
    cancelado: 'Assinatura cancelada',
    chargeback: 'Pagamento em contestação',
  }
  return labels[props.dashboard.status_pagamento] || 'Pagamento em processamento'
})

const monthLabel = computed(() =>
  new Intl.DateTimeFormat('pt-BR', {
    timeZone: 'America/Sao_Paulo',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  }).format(clock.value),
)

const clientNames = computed(() => {
  const names = new Map<string, string>()
  props.clients.forEach((client) => {
    names.set(String(client.id), client.razao_social || client.nome || 'Cliente sem nome')
  })
  return names
})

const clientName = (id?: string | number) =>
  id === undefined ? 'Sem cliente' : clientNames.value.get(String(id)) || 'Cliente'

const activeTasks = computed(() => scopedTasks.value.filter((task) => task.status !== 'concluida'))
const completedTasks = computed(() =>
  scopedTasks.value.filter((task) => task.status === 'concluida'),
)
const dueToday = computed(
  () => activeTasks.value.filter((task) => task.due_date === todayIso.value).length,
)
const overdueTasks = computed(() =>
  activeTasks.value.filter((task) => task.due_date && task.due_date < todayIso.value),
)
const awaitingTasks = computed(() =>
  activeTasks.value.filter((task) => task.status === 'aguardando_cliente'),
)
const inProgressTasks = computed(() =>
  activeTasks.value.filter((task) => task.status === 'em_andamento'),
)
const pendingTasks = computed(() => activeTasks.value.filter((task) => task.status === 'pendente'))
const onTimePercent = computed(() =>
  activeTasks.value.length
    ? Math.max(
        0,
        Math.round(
          ((activeTasks.value.length - overdueTasks.value.length) / activeTasks.value.length) * 100,
        ),
      )
    : null,
)
const completionPercent = computed(() =>
  scopedTasks.value.length
    ? Math.round((completedTasks.value.length / scopedTasks.value.length) * 100)
    : 0,
)

const metrics = computed(() => [
  {
    label: 'Atrasadas',
    value: overdueTasks.value.length,
    helper: 'Obrigações abertas com prazo vencido',
    icon: 'alert',
    tone: 'red',
  },
  {
    label: 'Vencendo hoje',
    value: dueToday.value,
    helper: 'Entregas abertas para hoje',
    icon: 'clock',
    tone: 'amber',
  },
  {
    label: 'Em andamento',
    value: inProgressTasks.value.length,
    helper: 'Trabalho iniciado e ainda não concluído',
    icon: 'clipboard',
    tone: 'blue',
  },
])

const flowItems = computed(() => {
  const total = Math.max(scopedTasks.value.length, 1)
  return [
    { label: 'A fazer', value: pendingTasks.value.length, color: 'text-blue-600' },
    { label: 'Em andamento', value: inProgressTasks.value.length, color: 'text-cyan-600' },
    { label: 'Aguardando cliente', value: awaitingTasks.value.length, color: 'text-amber-600' },
    { label: 'Concluídas', value: completedTasks.value.length, color: 'text-emerald-600' },
  ].map((item) => ({ ...item, percent: Math.round((item.value / total) * 100) }))
})

const alerts = computed(() => [
  {
    label: `${overdueTasks.value.length} ${overdueTasks.value.length === 1 ? 'tarefa atrasada' : 'tarefas atrasadas'}`,
    helper: overdueTasks.value.length ? 'Revise os prazos vencidos' : 'Nenhum atraso encontrado',
    tone: 'red',
  },
  {
    label: `${dueToday.value} ${dueToday.value === 1 ? 'tarefa vence' : 'tarefas vencem'} hoje`,
    helper: dueToday.value ? 'Priorize as entregas do dia' : 'Agenda do dia livre',
    tone: 'amber',
  },
  {
    label: `${awaitingTasks.value.length} ${awaitingTasks.value.length === 1 ? 'item aguarda' : 'itens aguardam'} cliente`,
    helper: awaitingTasks.value.length
      ? 'Dependem de retorno externo'
      : 'Nenhuma dependência externa',
    tone: 'cyan',
  },
])

const priorityWeight: Record<string, number> = { Urgente: 4, Alta: 3, Média: 2, Baixa: 1 }
const priorities = computed(() =>
  activeTasks.value
    .slice()
    .sort((a, b) => {
      const overdueA = a.due_date && a.due_date < todayIso.value ? 1 : 0
      const overdueB = b.due_date && b.due_date < todayIso.value ? 1 : 0
      if (overdueA !== overdueB) return overdueB - overdueA
      const dueTodayA = a.due_date === todayIso.value ? 1 : 0
      const dueTodayB = b.due_date === todayIso.value ? 1 : 0
      if (dueTodayA !== dueTodayB) return dueTodayB - dueTodayA
      const priority =
        (priorityWeight[b.grau_importancia || 'Média'] || 0) -
        (priorityWeight[a.grau_importancia || 'Média'] || 0)
      if (priority) return priority
      return (a.due_date || '9999').localeCompare(b.due_date || '9999')
    })
    .slice(0, 5),
)

const recentTasks = computed(() =>
  scopedTasks.value
    .slice()
    .sort((a, b) => new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime())
    .slice(0, 4),
)

const clientsWithPending = computed(() => {
  const grouped = new Map<
    string,
    { id: string; name: string; pending: number; overdue: number; lastActivity?: string }
  >()
  activeTasks.value.forEach((task) => {
    const id = String(task.client_id || '')
    if (!id) return
    const current = grouped.get(id) || {
      id,
      name: clientName(task.client_id),
      pending: 0,
      overdue: 0,
      lastActivity: task.created_at,
    }
    current.pending += 1
    if (task.due_date && task.due_date < todayIso.value) current.overdue += 1
    if (
      task.created_at &&
      (!current.lastActivity || new Date(task.created_at) > new Date(current.lastActivity))
    ) {
      current.lastActivity = task.created_at
    }
    grouped.set(id, current)
  })
  return Array.from(grouped.values())
    .sort((a, b) => b.pending - a.pending || b.overdue - a.overdue)
    .slice(0, 5)
})

const recurringTasks = computed(() =>
  activeTasks.value
    .filter((task) => task.is_recurring)
    .slice()
    .sort((a, b) => (a.due_date || '9999').localeCompare(b.due_date || '9999'))
    .slice(0, 5),
)

const formatDate = (date?: string) => {
  if (!date) return 'Sem prazo'
  const parsed = new Date(`${date.slice(0, 10)}T00:00:00`)
  return Number.isNaN(parsed.getTime())
    ? 'Sem prazo'
    : parsed.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
}

const formatCreatedAt = (date?: string) => {
  if (!date) return 'Data indisponível'
  const parsed = new Date(date)
  return Number.isNaN(parsed.getTime())
    ? 'Data indisponível'
    : parsed.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' })
}

const statusLabel = (task: Task) => {
  if (task.due_date && task.due_date < todayIso.value && task.status !== 'concluida')
    return 'Atrasada'
  if (task.due_date === todayIso.value && task.status !== 'concluida') return 'Vence hoje'
  if (task.status === 'aguardando_cliente') return 'Aguardando cliente'
  if (task.status === 'em_andamento') return 'Em andamento'
  if (task.status === 'concluida') return 'Concluída'
  return 'Pendente'
}

const statusClass = (task: Task) => {
  const label = statusLabel(task)
  if (label === 'Atrasada') return 'bg-red-50 text-red-600'
  if (label === 'Vence hoje') return 'bg-amber-50 text-amber-700'
  if (label === 'Aguardando cliente') return 'bg-cyan-50 text-cyan-700'
  if (label === 'Em andamento') return 'bg-blue-50 text-blue-700'
  if (label === 'Concluída') return 'bg-emerald-50 text-emerald-700'
  return 'bg-slate-100 text-slate-600'
}

const initials = (name: string) =>
  name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase()
</script>

<template>
  <div class="space-y-4 pb-4">
    <header class="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
      <div>
        <div class="flex flex-wrap items-center gap-3">
          <h1 class="text-[28px] font-semibold tracking-[-0.035em] text-[#101a38] sm:text-[32px]">
            {{ greeting }}, {{ firstName }} <span aria-hidden="true">👋</span>
          </h1>
          <span class="rounded-full bg-blue-50 px-2.5 py-1 text-[11px] font-semibold text-blue-700">
            {{ planLabel }}
          </span>
        </div>
        <p class="mt-1 text-sm text-[#6b7890]">
          Aqui está o resumo da operação do seu escritório hoje.
        </p>
      </div>
      <div class="flex flex-col gap-2 sm:flex-row">
        <RouterLink
          to="/calendario"
          class="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl border border-[#dce2eb] bg-white px-4 text-sm font-medium text-[#26344f] shadow-sm hover:bg-slate-50"
        >
          <svg
            class="h-4 w-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.8"
              d="M7 3v3m10-3v3M4 9h16M5 5h14a1 1 0 0 1 1 1v14H4V6a1 1 0 0 1 1-1Z"
            />
          </svg>
          <span class="capitalize">{{ monthLabel }}</span>
          <svg
            class="h-3.5 w-3.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="m7 10 5 5 5-5"
            />
          </svg>
        </RouterLink>
        <RouterLink
          v-if="canWrite"
          to="/obrigacoes?novo=1"
          class="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-[var(--ct-primary)] px-5 text-sm font-semibold text-white shadow-sm hover:bg-[var(--ct-primary-hover)]"
        >
          <svg
            class="h-5 w-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path stroke-linecap="round" stroke-width="2" d="M12 5v14M5 12h14" />
          </svg>
          Nova obrigação
        </RouterLink>
      </div>
    </header>

    <div
      v-if="!loading && dashboard.status_pagamento !== 'ativo'"
      class="flex flex-col justify-between gap-3 rounded-xl border px-4 py-3 sm:flex-row sm:items-center"
      :class="
        hasCriticalBillingStatus ? 'border-red-200 bg-red-50' : 'border-amber-200 bg-amber-50'
      "
    >
      <div>
        <p
          class="text-sm font-semibold"
          :class="hasCriticalBillingStatus ? 'text-red-800' : 'text-amber-800'"
        >
          {{ billingAlertTitle }}
        </p>
        <p class="mt-0.5 text-xs text-slate-600">
          Verifique a assinatura para manter o acesso aos recursos.
        </p>
      </div>
      <RouterLink
        v-if="role === 'admin'"
        to="/faturamento"
        class="text-xs font-bold text-[var(--ct-primary)]"
        >Ver assinatura</RouterLink
      >
    </div>

    <section
      v-if="
        !loading && lookupsReady && role === 'admin' && completedSteps < steps.length && canWrite
      "
      class="rounded-xl border border-blue-200 bg-blue-50 p-5"
      aria-label="Primeiros passos"
    >
      <h2 class="font-semibold text-slate-900">
        Configure seu escritório: {{ completedSteps }} de {{ steps.length }} etapas concluídas
      </h2>
      <p class="mt-1 text-sm text-slate-600">
        Comece com um cliente real e organize a primeira entrega. Convidar a equipe é opcional.
      </p>
      <progress
        class="my-3 h-2 w-full accent-blue-600"
        :value="completedSteps"
        :max="steps.length"
        aria-label="Progresso da configuração"
      />
      <ol class="grid gap-3 sm:grid-cols-3">
        <li
          v-for="(step, index) in steps"
          :key="step.label"
          class="rounded-lg bg-white p-3 text-sm"
        >
          <span v-if="step.done" class="text-emerald-700">✓ {{ step.label }} — concluído</span>
          <RouterLink v-else :to="step.to" class="font-semibold text-blue-700 underline"
            >{{ index + 1 }}. {{ step.label }}</RouterLink
          >
        </li>
      </ol>
    </section>
    <div class="flex flex-wrap items-center justify-between gap-3">
      <p class="text-sm text-slate-600">{{ scopeLabel }} · Prazos no horário de Brasília</p>
      <div
        class="flex rounded-lg border border-slate-200 bg-white p-1"
        role="group"
        aria-label="Escopo dos indicadores"
      >
        <button
          v-for="option in ['all', 'mine'] as const"
          :key="option"
          type="button"
          :aria-pressed="scope === option"
          class="rounded-md px-3 py-2 text-sm"
          :class="scope === option ? 'bg-blue-100 font-semibold text-blue-800' : 'text-slate-600'"
          @click="scope = option"
        >
          {{
            option === 'mine'
              ? 'Minhas tarefas'
              : canManage
                ? 'Todo o escritório'
                : 'Minha carteira'
          }}
        </button>
      </div>
    </div>
    <p v-if="!loading && !lookupsReady" role="status" class="text-sm text-amber-800">
      Alguns dados de clientes ou da equipe estão indisponíveis. Atualize a página para tentar
      novamente.
    </p>
    <section class="grid gap-3 sm:grid-cols-3">
      <article
        v-for="metric in metrics"
        :key="metric.label"
        class="min-h-[108px] rounded-xl border border-[#e0e5ed] bg-white p-4 shadow-[0_2px_8px_rgba(15,23,42,0.035)]"
      >
        <div v-if="loading" class="flex h-full items-center gap-4">
          <div class="h-12 w-12 animate-pulse rounded-full bg-slate-100"></div>
          <div class="flex-1 space-y-2">
            <div class="h-3 w-20 animate-pulse rounded bg-slate-100"></div>
            <div class="h-7 w-12 animate-pulse rounded bg-slate-100"></div>
          </div>
        </div>
        <div v-else class="flex items-center gap-4">
          <span
            class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full"
            :class="{
              'bg-blue-50 text-blue-600': metric.tone === 'blue',
              'bg-amber-50 text-amber-600': metric.tone === 'amber',
              'bg-red-50 text-red-600': metric.tone === 'red',
              'bg-emerald-50 text-emerald-600': metric.tone === 'green',
              'bg-cyan-50 text-cyan-600': metric.tone === 'cyan',
            }"
          >
            <svg
              class="h-6 w-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                v-if="metric.icon === 'clipboard'"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="1.9"
                d="M9 5h6m-7 0H6v16h12V5h-2m-8 0a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2H8V5Zm2 7h4m-4 4h4"
              />
              <path
                v-else-if="metric.icon === 'clock'"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="1.9"
                d="M12 7v5l3 2m6-2a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
              />
              <path
                v-else-if="metric.icon === 'alert'"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="1.9"
                d="M12 8v5m0 3.5v.5m9-5a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
              />
              <path
                v-else-if="metric.icon === 'check'"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="1.9"
                d="m7 12 3 3 7-7m4 4a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
              />
              <path
                v-else
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="1.9"
                d="M12 3 5 6v5c0 4.7 2.7 8 7 10 4.3-2 7-5.3 7-10V6l-7-3Zm-3 9 2 2 4-4"
              />
            </svg>
          </span>
          <div class="min-w-0">
            <p class="truncate text-xs font-medium text-[#46546d]">{{ metric.label }}</p>
            <p
              class="mt-0.5 text-[25px] font-semibold leading-none tracking-[-0.03em] text-[#101a38]"
            >
              {{ metric.value }}
            </p>
            <p class="mt-2 truncate text-[10px] text-[#8190a8]">{{ metric.helper }}</p>
          </div>
        </div>
      </article>
    </section>

    <p v-if="!loading" class="text-sm text-slate-600">
      Histórico completo: {{ completedTasks.length }} concluídas ({{
        scopedTasks.length ? `${completionPercent}%` : 'sem dados'
      }}). Obrigações abertas: {{ activeTasks.length }} · No prazo:
      {{ onTimePercent === null ? 'sem dados' : `${onTimePercent}%` }}.
    </p>
    <div class="grid gap-4 xl:grid-cols-12">
      <section
        class="overflow-hidden rounded-xl border border-[#e0e5ed] bg-white shadow-sm xl:col-span-12"
      >
        <div class="flex items-center justify-between border-b border-[#edf0f5] px-4 py-3.5">
          <h2 class="text-sm font-semibold text-[#17213d]">O que fazer agora</h2>
          <RouterLink to="/obrigacoes" class="text-[11px] font-semibold text-[var(--ct-primary)]"
            >Ver todas</RouterLink
          >
        </div>
        <div v-if="loading" class="space-y-2 p-4">
          <div v-for="i in 5" :key="i" class="h-10 animate-pulse rounded bg-slate-100"></div>
        </div>
        <div v-else-if="priorities.length" class="divide-y divide-[#f0f2f6] px-4">
          <RouterLink
            v-for="task in priorities"
            :key="task.id"
            :to="taskLink(task)"
            class="grid grid-cols-[1fr_auto] items-center gap-3 py-2.5"
          >
            <span class="min-w-0"
              ><span class="block truncate text-sm font-semibold text-[#26344f]">{{
                task.title
              }}</span
              ><span class="mt-0.5 block truncate text-xs text-[#6b7890]"
                >{{ clientName(task.client_id) }} · {{ formatDate(task.due_date) }} ·
                {{ assigneeName(task) }}</span
              ></span
            >
            <span class="rounded-md px-2 py-1 text-[9px] font-medium" :class="statusClass(task)">{{
              statusLabel(task)
            }}</span>
          </RouterLink>
        </div>
        <p v-else class="px-4 py-12 text-center text-xs text-[#8190a8]">
          {{
            scopedTasks.length
              ? 'Tudo em dia: nenhuma obrigação aberta neste escopo.'
              : 'Comece criando uma obrigação para acompanhar seus próximos prazos.'
          }}
          <RouterLink
            v-if="canWrite"
            to="/obrigacoes?novo=1"
            class="mt-3 block font-semibold text-blue-700 underline"
            >Criar obrigação</RouterLink
          >
        </p>
      </section>
      <section
        class="overflow-hidden rounded-xl border border-[#e0e5ed] bg-white shadow-sm xl:col-span-8"
      >
        <div class="flex items-center justify-between px-4 pt-4">
          <h2 class="text-sm font-semibold text-[#17213d]">Fluxo de tarefas</h2>
          <RouterLink
            to="/obrigacoes"
            class="rounded-lg border border-[#e0e5ed] px-3 py-1.5 text-[11px] font-medium text-[#52617a] hover:bg-slate-50"
            >Histórico completo</RouterLink
          >
        </div>
        <div v-if="loading" class="m-4 h-40 animate-pulse rounded-lg bg-slate-100"></div>
        <div v-else-if="!scopedTasks.length" class="p-6 text-sm text-slate-600">
          Sem tarefas neste escopo. Os indicadores aparecerão quando houver obrigações.
          <RouterLink
            v-if="canWrite"
            to="/obrigacoes?novo=1"
            class="mt-3 block font-semibold text-blue-700 underline"
            >Criar primeira obrigação</RouterLink
          >
        </div>
        <div v-else class="overflow-x-auto px-4 pb-3 pt-2">
          <div class="min-w-[480px]">
            <div class="grid grid-cols-4 divide-x divide-dashed divide-[#dce2eb] text-center">
              <div v-for="item in flowItems" :key="item.label" class="px-3 py-1">
                <p class="text-[11px] font-medium text-[#52617a]">{{ item.label }}</p>
                <p class="mt-1 text-xl font-semibold text-[#101a38]">{{ item.value }}</p>
                <p class="text-[10px] text-[#8190a8]">{{ item.percent }}%</p>
              </div>
            </div>
            <div class="mt-5 space-y-3">
              <div
                v-for="item in flowItems"
                :key="item.label"
                class="flex items-center gap-3 text-xs"
              >
                <span class="w-32 shrink-0">{{ item.label }}</span>
                <div class="h-2 flex-1 rounded-full bg-slate-100">
                  <div
                    class="h-2 rounded-full bg-blue-500"
                    :style="{ width: `${item.percent}%` }"
                  />
                </div>
                <span class="w-12 text-right">{{ item.percent }}%</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section
        class="overflow-hidden rounded-xl border border-[#e0e5ed] bg-white shadow-sm xl:col-span-4"
      >
        <div class="border-b border-[#edf0f5] px-4 py-3.5">
          <h2 class="text-sm font-semibold text-[#17213d]">Alertas importantes</h2>
        </div>
        <div v-if="loading" class="space-y-2 p-4">
          <div v-for="i in 3" :key="i" class="h-12 animate-pulse rounded-lg bg-slate-100"></div>
        </div>
        <div v-else class="divide-y divide-[#edf0f5]">
          <RouterLink
            v-for="alert in alerts"
            :key="alert.label"
            to="/obrigacoes"
            class="flex items-center gap-3 px-4 py-3 hover:bg-slate-50"
          >
            <span
              class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full"
              :class="
                alert.tone === 'red'
                  ? 'bg-red-50 text-red-600'
                  : alert.tone === 'amber'
                    ? 'bg-amber-50 text-amber-600'
                    : 'bg-cyan-50 text-cyan-600'
              "
            >
              <span class="text-sm font-bold">{{
                alert.tone === 'red' ? '!' : alert.tone === 'amber' ? '◷' : '○'
              }}</span>
            </span>
            <span class="min-w-0 flex-1"
              ><span class="block truncate text-xs font-semibold text-[#26344f]">{{
                alert.label
              }}</span
              ><span class="mt-0.5 block truncate text-[10px] text-[#8190a8]">{{
                alert.helper
              }}</span></span
            >
            <span class="text-slate-400">›</span>
          </RouterLink>
        </div>
        <RouterLink
          to="/obrigacoes"
          class="block border-t border-[#edf0f5] px-4 py-2.5 text-[11px] font-semibold text-[var(--ct-primary)]"
          >Ver todas as obrigações</RouterLink
        >
      </section>

      <section
        class="overflow-hidden rounded-xl border border-[#e0e5ed] bg-white shadow-sm xl:col-span-4"
      >
        <div class="flex items-center justify-between border-b border-[#edf0f5] px-4 py-3.5">
          <h2 class="text-sm font-semibold text-[#17213d]">Tarefas por responsável</h2>
          <RouterLink
            v-if="canManage"
            to="/membros"
            class="text-[11px] font-semibold text-[var(--ct-primary)]"
            >Equipe</RouterLink
          >
        </div>
        <div v-if="loading" class="space-y-3 p-4">
          <div v-for="i in 5" :key="i" class="h-10 animate-pulse rounded bg-slate-100"></div>
        </div>
        <div v-else-if="lookupsReady && team.length" class="space-y-3.5 p-4">
          <div v-for="member in team.slice(0, 5)" :key="member.id" class="flex items-center gap-3">
            <span
              class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-blue-50 text-[9px] font-bold text-blue-700"
              >{{ initials(member.nome) }}</span
            >
            <div class="min-w-0 flex-1">
              <div class="mb-1 flex items-center justify-between gap-2">
                <p class="truncate text-[10px] font-medium text-[#26344f]">{{ member.nome }}</p>
              </div>
              <p class="text-xs text-slate-600">
                {{ member.count }} abertas ·
                <span :class="member.overdue ? 'font-semibold text-red-700' : ''"
                  >{{ member.overdue }} atrasadas</span
                >
              </p>
            </div>
          </div>
        </div>
        <p v-else class="px-4 py-12 text-center text-xs text-[#8190a8]">
          Nenhum responsável disponível neste escopo.
        </p>
        <p v-if="!loading" class="border-t border-slate-100 px-4 py-3 text-xs text-slate-600">
          {{ unassigned }} obrigação(ões) sem responsável. Contagens do escopo selecionado, sem
          estimativa de capacidade.
        </p>
      </section>

      <section
        class="overflow-hidden rounded-xl border border-[#e0e5ed] bg-white shadow-sm xl:col-span-4"
      >
        <div class="flex items-center justify-between border-b border-[#edf0f5] px-4 py-3.5">
          <h2 class="text-sm font-semibold text-[#17213d]">Tarefas recentes</h2>
          <RouterLink to="/obrigacoes" class="text-[11px] font-semibold text-[var(--ct-primary)]"
            >Ver todas</RouterLink
          >
        </div>
        <div v-if="loading" class="space-y-2 p-4">
          <div v-for="i in 4" :key="i" class="h-11 animate-pulse rounded bg-slate-100"></div>
        </div>
        <div v-else-if="recentTasks.length" class="divide-y divide-[#f0f2f6] px-4">
          <RouterLink
            v-for="task in recentTasks"
            :key="task.id"
            :to="taskLink(task)"
            class="flex items-center gap-3 py-3"
          >
            <span
              class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full"
              :class="statusClass(task)"
            >
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.8"
                  d="M7 3h7l4 4v14H7V3Zm7 0v5h5M10 12h5m-5 4h5"
                />
              </svg>
            </span>
            <span class="min-w-0 flex-1"
              ><span class="block truncate text-[11px] font-semibold text-[#26344f]">{{
                task.title
              }}</span
              ><span class="mt-0.5 block truncate text-[10px] text-[#8190a8]">{{
                clientName(task.client_id)
              }}</span></span
            >
            <span class="shrink-0 text-[9px] text-[#8190a8]">{{
              formatCreatedAt(task.created_at)
            }}</span>
          </RouterLink>
        </div>
        <p v-else class="px-4 py-12 text-center text-xs text-[#8190a8]">
          Nenhuma obrigação neste escopo.
          <RouterLink
            v-if="canWrite"
            to="/obrigacoes?novo=1"
            class="mt-3 block font-semibold text-blue-700 underline"
            >Criar primeira obrigação</RouterLink
          >
        </p>
      </section>

      <section
        class="overflow-hidden rounded-xl border border-[#e0e5ed] bg-white shadow-sm xl:col-span-5"
      >
        <div class="flex items-center justify-between border-b border-[#edf0f5] px-4 py-3.5">
          <h2 class="text-sm font-semibold text-[#17213d]">Clientes com mais pendências</h2>
          <RouterLink to="/clientes" class="text-[11px] font-semibold text-[var(--ct-primary)]"
            >Ver clientes</RouterLink
          >
        </div>
        <div v-if="loading" class="m-4 h-36 animate-pulse rounded bg-slate-100"></div>
        <div v-else-if="clientsWithPending.length" class="overflow-x-auto">
          <div class="min-w-[480px]">
            <div
              class="grid grid-cols-[1fr_80px_80px_90px] border-b border-[#edf0f5] px-4 py-2 text-[9px] font-medium text-[#8190a8]"
            >
              <span>Cliente</span><span>Pendências</span><span>Atrasadas</span
              ><span>Atividade</span>
            </div>
            <RouterLink
              v-for="client in clientsWithPending"
              :key="client.id"
              to="/clientes"
              class="grid grid-cols-[1fr_80px_80px_90px] items-center border-b border-[#f0f2f6] px-4 py-2.5 last:border-0 hover:bg-slate-50"
            >
              <span class="truncate text-[10px] font-medium text-[#26344f]">{{ client.name }}</span
              ><span class="text-[10px] font-semibold text-amber-600">{{ client.pending }}</span
              ><span
                class="text-[10px] font-semibold"
                :class="client.overdue ? 'text-red-600' : 'text-emerald-600'"
                >{{ client.overdue }}</span
              ><span class="text-[9px] text-[#8190a8]">{{
                formatCreatedAt(client.lastActivity)
              }}</span>
            </RouterLink>
          </div>
        </div>
        <p v-else class="px-4 py-12 text-center text-xs text-[#8190a8]">
          {{
            clients.length
              ? 'Nenhum cliente com pendências neste escopo.'
              : 'Cadastre seu primeiro cliente para começar a organizar as entregas.'
          }}
          <RouterLink
            v-if="canManage && canWrite && !clients.length"
            to="/clientes?novo=1"
            class="mt-3 block font-semibold text-blue-700 underline"
            >Cadastrar cliente</RouterLink
          >
        </p>
      </section>

      <section
        class="overflow-hidden rounded-xl border border-[#e0e5ed] bg-white shadow-sm xl:col-span-7"
      >
        <div class="flex items-center justify-between border-b border-[#edf0f5] px-4 py-3.5">
          <h2 class="text-sm font-semibold text-[#17213d]">Próximas recorrências</h2>
          <RouterLink to="/obrigacoes" class="text-[11px] font-semibold text-[var(--ct-primary)]"
            >Ver recorrências</RouterLink
          >
        </div>
        <div v-if="loading" class="m-4 h-36 animate-pulse rounded bg-slate-100"></div>
        <div v-else-if="recurringTasks.length" class="overflow-x-auto">
          <div class="min-w-[620px]">
            <div
              class="grid grid-cols-[1.2fr_1fr_100px_80px] border-b border-[#edf0f5] px-4 py-2 text-[9px] font-medium text-[#8190a8]"
            >
              <span>Recorrência</span><span>Cliente</span><span>Próxima execução</span
              ><span>Frequência</span>
            </div>
            <RouterLink
              v-for="task in recurringTasks"
              :key="task.id"
              :to="taskLink(task)"
              class="grid grid-cols-[1.2fr_1fr_100px_80px] items-center border-b border-[#f0f2f6] px-4 py-2.5 last:border-0 hover:bg-slate-50"
            >
              <span class="truncate text-[10px] font-medium text-[#26344f]">{{ task.title }}</span
              ><span class="truncate text-[10px] text-[#52617a]">{{
                clientName(task.client_id)
              }}</span
              ><span class="text-[10px] text-[#26344f]">{{ formatDate(task.due_date) }}</span
              ><span class="text-[10px] text-[#52617a]">Mensal</span>
            </RouterLink>
          </div>
        </div>
        <p v-else class="px-4 py-12 text-center text-xs text-[#8190a8]">
          Nenhuma recorrência ativa neste escopo. Ao criar uma obrigação, marque a opção de
          recorrência para repetir a entrega mensalmente.
          <RouterLink
            v-if="canWrite"
            to="/obrigacoes?novo=1"
            class="mt-3 block font-semibold text-blue-700 underline"
            >Criar obrigação recorrente</RouterLink
          >
        </p>
      </section>
    </div>
  </div>
</template>
