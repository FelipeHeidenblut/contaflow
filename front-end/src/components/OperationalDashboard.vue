<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import AppNavIcon from './AppNavIcon.vue'

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
    weekday: 'long',
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
const inProgressTasks = computed(() =>
  activeTasks.value.filter((task) => task.status === 'em_andamento'),
)
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
const metrics = computed(() => [
  {
    label: 'Tarefas em atraso',
    value: overdueTasks.value.length,
    helper: 'Obrigações abertas com prazo vencido',
    icon: 'alert',
    tone: 'red',
  },
  {
    label: 'Tarefas para hoje',
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
  const onTime = activeTasks.value.filter(
    (task) => !task.due_date || task.due_date >= todayIso.value,
  )
  const total = Math.max(scopedTasks.value.length, 1)
  return [
    { label: 'Em atraso', value: overdueTasks.value.length },
    { label: 'Pendentes', value: onTime.filter((task) => task.status !== 'em_andamento').length },
    {
      label: 'Em andamento',
      value: onTime.filter((task) => task.status === 'em_andamento').length,
    },
    { label: 'Concluídas', value: completedTasks.value.length },
  ].map((item) => ({ ...item, percent: Math.round((item.value / total) * 100) }))
})

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

const formatDeadlineDate = (date: string) => {
  const difference = (Date.parse(date) - Date.parse(todayIso.value)) / 86400000
  const parsed = new Date(`${date}T12:00:00Z`)
  const weekday =
    difference === 0
      ? 'Hoje'
      : difference === 1
        ? 'Amanhã'
        : parsed.toLocaleDateString('pt-BR', { weekday: 'long', timeZone: 'UTC' })
  const label = parsed
    .toLocaleDateString('pt-BR', { day: 'numeric', month: 'short', timeZone: 'UTC' })
    .replace('.', '')
  return `${weekday.charAt(0).toUpperCase() + weekday.slice(1)}, ${label}`
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
    return 'Em atraso'
  if (task.status === 'aguardando_cliente') return 'Aguardando cliente'
  if (task.status === 'em_andamento') return 'Em andamento'
  if (task.status === 'concluida') return 'Concluída'
  return 'Pendente'
}

const statusClass = (task: Task) => {
  const label = statusLabel(task)
  if (label === 'Em atraso') return 'bg-red-50 text-red-600'
  if (label === 'Aguardando cliente') return 'bg-cyan-50 text-cyan-700'
  if (label === 'Em andamento') return 'bg-blue-50 text-blue-700'
  if (label === 'Concluída') return 'bg-emerald-50 text-emerald-700'
  return 'bg-amber-50 text-amber-600'
}

const taskTab = ref<'priority' | 'today' | 'overdue' | 'next' | 'date'>('today')
const selectedDate = ref('')
const visibleTasks = computed(() => {
  const tasks =
    taskTab.value === 'priority'
      ? priorities.value
      : activeTasks.value
          .filter((task) => {
            if (taskTab.value === 'today') return task.due_date === todayIso.value
            if (taskTab.value === 'overdue')
              return !!task.due_date && task.due_date < todayIso.value
            if (taskTab.value === 'date') return task.due_date === selectedDate.value
            return !!task.due_date && task.due_date > todayIso.value
          })
          .slice()
          .sort((a, b) => (a.due_date || '').localeCompare(b.due_date || ''))
  return tasks.slice(0, 5)
})
const monthOffset = ref(0)
const calendarMonth = computed(() => {
  const [year, month] = todayIso.value.split('-').map(Number)
  return new Date(Date.UTC(year!, month! - 1 + monthOffset.value, 1))
})
const calendarTitle = computed(() =>
  calendarMonth.value.toLocaleDateString('pt-BR', {
    timeZone: 'UTC',
    month: 'long',
    year: 'numeric',
  }),
)
const calendarDays = computed(() => {
  const first = calendarMonth.value
  const count = new Date(Date.UTC(first.getUTCFullYear(), first.getUTCMonth() + 1, 0)).getUTCDate()
  return Array.from({ length: Math.ceil((first.getUTCDay() + count) / 7) * 7 }, (_, i) => {
    const date = new Date(
      Date.UTC(first.getUTCFullYear(), first.getUTCMonth(), i - first.getUTCDay() + 1),
    )
    const iso = date.toISOString().slice(0, 10)
    return {
      iso,
      day: date.getUTCDate(),
      current: date.getUTCMonth() === first.getUTCMonth(),
      count: activeTasks.value.filter((task) => task.due_date === iso).length,
    }
  })
})
const selectDate = (date: string) => {
  selectedDate.value = date
  taskTab.value = 'date'
}
const nextDates = computed(() => {
  const counts = new Map<string, number>()
  activeTasks.value.forEach((task) => {
    if (task.due_date && task.due_date >= todayIso.value)
      counts.set(task.due_date, (counts.get(task.due_date) || 0) + 1)
  })
  return [...counts].sort(([a], [b]) => a.localeCompare(b)).slice(0, 5)
})
const statusColors = ['#ff6474', '#ffd34f', '#2f80ff', '#1bc39b']
const donutStyle = computed(() => {
  if (!scopedTasks.value.length) return { background: '#eef2f7' }
  let offset = 0
  const segments = flowItems.value.map((item, i) => {
    const start = offset
    offset += (item.value / scopedTasks.value.length) * 100
    return `${statusColors[i]} ${start}% ${offset}%`
  })
  return { background: `conic-gradient(${segments.join(',')})` }
})
</script>

<template>
  <div class="ct-reference-dashboard space-y-4 pb-6">
    <header class="relative flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 class="text-2xl font-semibold tracking-tight sm:text-[34px]">Olá, {{ firstName }}!</h1>
        <p class="mt-2 text-[17px] leading-relaxed text-slate-500">
          Aqui está um resumo das suas tarefas e prazos de hoje.
        </p>
      </div>
      <div class="flex flex-wrap items-center gap-3">
        <span class="ct-dashboard-date text-[13px] text-slate-500">{{ monthLabel }}</span>
        <details class="static sm:relative">
          <summary
            aria-label="Opções do dashboard"
            class="cursor-pointer list-none rounded-md px-2 py-1 text-slate-500 hover:bg-blue-50"
          >
            ⋯
          </summary>
          <div
            class="absolute right-0 top-full z-20 mt-2 max-h-[70vh] w-[min(600px,calc(100vw-32px))] overflow-y-auto rounded-xl border border-slate-200 bg-white p-5 shadow-lg"
          >
            <div class="flex flex-wrap items-center justify-between gap-3">
              <p class="text-sm text-slate-500">{{ scopeLabel }} · Prazos no horário de Brasília</p>
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
                  class="rounded-md px-3 py-1.5 text-sm"
                  :class="
                    scope === option ? 'bg-blue-50 font-semibold text-blue-600' : 'text-slate-500'
                  "
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
            <div
              class="flex flex-wrap gap-2 px-5 py-4"
              role="group"
              aria-label="Prazos das tarefas"
            >
              <button
                v-for="tab in [
                  { id: 'priority', label: 'Prioridades' },
                  { id: 'today', label: 'Hoje' },
                  { id: 'overdue', label: 'Tarefas em atraso' },
                  { id: 'next', label: 'Próximas' },
                ] as const"
                :key="tab.id"
                type="button"
                :aria-pressed="taskTab === tab.id"
                class="rounded-lg px-3 py-1.5 text-sm"
                :class="
                  taskTab === tab.id
                    ? 'bg-blue-50 font-semibold text-blue-600'
                    : 'text-slate-500 hover:bg-slate-50'
                "
                @click="taskTab = tab.id"
              >
                {{ tab.label }}</button
              ><span
                v-if="taskTab === 'date'"
                class="rounded-lg bg-blue-50 px-3 py-1.5 text-sm text-blue-600"
                >{{ formatDate(selectedDate) }}</span
              >
            </div>
            <RouterLink v-if="canWrite" to="/obrigacoes?novo=1" class="ct-button-primary mb-4"
              >+ Nova obrigação</RouterLink
            >
            <p class="mt-5 text-sm text-slate-500">
              No prazo entre as abertas:
              {{ onTimePercent === null ? 'sem dados' : `${onTimePercent}%` }}. Atraso é um alerta
              de prazo, independente do status.
            </p>
            <details class="ct-dashboard-card p-5">
              <summary class="cursor-pointer text-lg font-semibold">
                Mais detalhes: equipe, clientes e recorrências
              </summary>
              <div class="mt-6 grid gap-8 lg:grid-cols-3">
                <section>
                  <h2 class="mb-4 text-lg font-semibold">Tarefas por responsável</h2>
                  <p
                    v-for="member in team.slice(0, 5)"
                    :key="member.id"
                    class="border-b border-slate-100 py-3 text-sm"
                  >
                    <strong>{{ member.nome }}</strong
                    ><span class="mt-1 block text-slate-500"
                      >{{ member.count }} abertas · {{ member.overdue }} atrasadas</span
                    >
                  </p>
                  <p class="mt-3 text-sm text-slate-500">{{ unassigned }} sem responsável.</p>
                </section>
                <section>
                  <h2 class="mb-4 text-lg font-semibold">Clientes com pendências</h2>
                  <RouterLink
                    v-for="client in clientsWithPending"
                    :key="client.id"
                    to="/clientes"
                    class="block border-b border-slate-100 py-3 text-sm"
                    >{{ client.name
                    }}<span class="mt-1 block text-slate-500"
                      >{{ client.pending }} pendências · {{ client.overdue }} atrasadas</span
                    ></RouterLink
                  >
                  <p v-if="!clientsWithPending.length" class="text-sm text-slate-500">
                    Nenhuma pendência neste escopo.
                  </p>
                </section>
                <section>
                  <h2 class="mb-4 text-lg font-semibold">Obrigações recorrentes</h2>
                  <RouterLink
                    v-for="task in recurringTasks"
                    :key="task.id"
                    :to="taskLink(task)"
                    class="block border-b border-slate-100 py-3 text-sm"
                    >{{ task.title
                    }}<span class="mt-1 block text-slate-500"
                      >{{ task.due_date === todayIso ? 'Hoje' : formatDate(task.due_date) }} ·
                      {{ clientName(task.client_id) }}</span
                    ></RouterLink
                  >
                  <p v-if="!recurringTasks.length" class="text-sm text-slate-500">
                    Nenhuma recorrência ativa.
                  </p>
                </section>
              </div>
            </details>
          </div>
        </details>
      </div>
    </header>
    <div
      v-if="!loading && dashboard.status_pagamento !== 'ativo'"
      role="status"
      class="rounded-xl border border-amber-200 bg-amber-50 p-4 text-[15px]"
    >
      <strong>{{ billingAlertTitle }}</strong
      ><RouterLink v-if="role === 'admin'" to="/faturamento" class="ml-3 underline"
        >Ver assinatura</RouterLink
      >
    </div>
    <p v-if="!loading && !lookupsReady" role="status" class="text-[15px] text-amber-800">
      Dados de clientes ou da equipe indisponíveis. Atualize a página para tentar novamente.
    </p>
    <div v-if="loading" aria-label="Carregando dashboard" class="grid gap-4 sm:grid-cols-4">
      <div v-for="n in 4" :key="n" class="h-28 animate-pulse rounded-xl bg-slate-200/60" />
    </div>
    <template v-else>
      <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4" aria-label="Indicadores">
        <button
          v-for="metric in metrics.slice(0, 2)"
          :key="metric.label"
          type="button"
          class="ct-dashboard-card min-h-[127px] flex items-center gap-5 p-5 text-left"
          @click="taskTab = metric.tone === 'red' ? 'overdue' : 'today'"
        >
          <span
            class="flex h-[57px] w-[57px] shrink-0 items-center justify-center rounded-full text-xl"
            :class="metric.tone === 'red' ? 'bg-rose-50 text-rose-500' : 'bg-blue-50 text-blue-500'"
            ><AppNavIcon :name="metric.tone === 'red' ? 'clock' : 'calendar'"
          /></span>
          <div>
            <strong class="text-3xl font-semibold">{{ metric.value }}</strong>
            <p class="mt-2 text-sm text-slate-500">{{ metric.label }}</p>
          </div>
          <span class="ml-auto text-slate-400">›</span>
        </button>
        <article class="ct-dashboard-card min-h-[127px] flex items-center gap-5 p-5">
          <span
            class="flex h-[57px] w-[57px] shrink-0 items-center justify-center rounded-full bg-emerald-50 text-xl text-emerald-500"
            ><svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.8"
              class="h-6 w-6"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="9" />
              <path d="m7 12 3 3 7-7" /></svg
          ></span>
          <div>
            <strong class="text-3xl font-semibold">{{ completedTasks.length }}</strong>
            <p class="mt-2 text-sm leading-5 text-slate-500">
              Tarefas concluídas<br />no histórico
            </p>
          </div>
        </article>
        <RouterLink
          to="/clientes"
          class="ct-dashboard-card min-h-[127px] flex items-center gap-5 p-5"
          ><span
            class="flex h-[57px] w-[57px] shrink-0 items-center justify-center rounded-full bg-violet-50 text-xl text-violet-500"
            ><AppNavIcon name="users"
          /></span>
          <div>
            <strong class="text-3xl font-semibold">{{ dashboard.total_clientes }}</strong>
            <p class="mt-2 text-sm leading-5 text-slate-500">Clientes ativos</p>
          </div>
          <span class="ml-auto text-slate-400">›</span></RouterLink
        >
      </section>
      <div class="ct-dashboard-workspace grid items-start gap-4 xl:grid-cols-[minmax(0,1fr)_306px]">
        <div class="ct-dashboard-main min-w-0 space-y-4">
          <section class="ct-dashboard-tasks ct-dashboard-card overflow-hidden">
            <div class="flex flex-wrap items-center justify-between gap-3 px-5 py-5">
              <h2 class="text-lg font-semibold">
                {{
                  taskTab === 'today'
                    ? 'Tarefas de hoje'
                    : taskTab === 'overdue'
                      ? 'Tarefas em atraso'
                      : taskTab === 'next'
                        ? 'Próximas tarefas'
                        : taskTab === 'date'
                          ? `Tarefas de ${formatDate(selectedDate)}`
                          : 'Tarefas prioritárias'
                }}
              </h2>
              <RouterLink to="/obrigacoes" class="text-sm text-blue-600">Ver todas</RouterLink>
            </div>
            <div class="overflow-x-auto px-5 pb-3">
              <table class="w-full min-w-[650px] text-left text-sm">
                <thead class="bg-[#f5f7fb] text-slate-500">
                  <tr>
                    <th class="w-10 rounded-l-lg p-3">
                      <span class="sr-only">Abrir obrigação</span>
                    </th>
                    <th class="p-3 font-medium">Tarefa</th>
                    <th class="p-3 font-medium">Cliente</th>
                    <th class="p-3 font-medium">Responsável</th>
                    <th class="p-3 font-medium">Prazo</th>
                    <th class="p-3 font-medium">Status</th>
                    <th class="w-10 rounded-r-lg p-3"><span class="sr-only">Ações</span></th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="task in visibleTasks"
                    :key="task.id"
                    class="border-b border-slate-100 last:border-0"
                  >
                    <td class="p-3">
                      <RouterLink
                        :to="taskLink(task)"
                        :aria-label="`Abrir ${task.title}`"
                        class="inline-flex h-3.5 w-3.5 rounded-[3px] border border-blue-200 hover:bg-blue-50"
                      />
                    </td>
                    <td class="p-3">
                      <RouterLink
                        :to="taskLink(task)"
                        class="font-medium text-slate-800 hover:text-blue-600 hover:underline"
                        >{{ task.title }}</RouterLink
                      >
                    </td>
                    <td class="p-3 text-slate-500">{{ clientName(task.client_id) }}</td>
                    <td class="p-3 text-slate-500">{{ assigneeName(task) }}</td>
                    <td
                      class="whitespace-nowrap p-3"
                      :class="
                        task.due_date && task.due_date <= todayIso
                          ? 'text-rose-500'
                          : 'text-slate-500'
                      "
                    >
                      {{ task.due_date === todayIso ? 'Hoje' : formatDate(task.due_date) }}
                    </td>
                    <td class="p-3">
                      <span
                        class="inline-block whitespace-nowrap rounded-full px-2 py-1 text-xs"
                        :class="statusClass(task)"
                        >{{ statusLabel(task) }}</span
                      >
                    </td>
                    <td class="p-3">
                      <RouterLink
                        :to="taskLink(task)"
                        :aria-label="`Mais detalhes de ${task.title}`"
                        class="inline-flex px-2 text-base text-slate-500"
                        >⋮</RouterLink
                      >
                    </td>
                  </tr>
                  <tr v-if="!visibleTasks.length">
                    <td colspan="7" class="ct-dashboard-empty-cell">
                      <div
                        class="flex min-h-[230px] flex-col items-center justify-center gap-4 px-5 text-center"
                      >
                        <p class="text-[15px] text-slate-500">
                          {{
                            scopedTasks.length
                              ? taskTab === 'today'
                                ? 'Nenhuma obrigação aberta para hoje.'
                                : 'Nenhuma obrigação aberta neste filtro.'
                              : 'Comece organizando sua primeira entrega.'
                          }}
                        </p>
                        <RouterLink
                          v-if="canWrite"
                          to="/obrigacoes?novo=1"
                          class="inline-block text-sm font-medium text-blue-600"
                          >Criar obrigação →</RouterLink
                        >
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>
          <div class="ct-dashboard-insights grid items-start gap-4 lg:grid-cols-[1.27fr_1fr]">
            <section class="ct-dashboard-status ct-dashboard-card p-5">
              <h2 class="text-lg font-semibold">Tarefas por status</h2>

              <div class="mt-7 flex flex-wrap items-center gap-6">
                <div
                  class="relative flex h-[174px] w-[174px] shrink-0 items-center justify-center rounded-full"
                  :style="donutStyle"
                  role="img"
                  :aria-label="`${scopedTasks.length} tarefas no escopo selecionado`"
                >
                  <div
                    class="flex h-[118px] w-[118px] flex-col items-center justify-center rounded-full bg-white"
                  >
                    <strong class="text-3xl">{{ scopedTasks.length }}</strong
                    ><span class="text-sm text-slate-500">tarefas</span>
                  </div>
                </div>
                <ul class="min-w-36 flex-1 text-xs">
                  <li
                    v-for="(item, i) in flowItems"
                    :key="item.label"
                    class="flex items-center gap-2 border-b border-slate-50 py-3 last:border-0"
                  >
                    <span
                      class="h-2.5 w-2.5 rounded"
                      :style="{ background: statusColors[i] }"
                    /><span class="flex-1 text-slate-500">{{ item.label }}</span
                    ><strong class="font-medium">{{ item.value }}</strong
                    ><span class="w-9 text-right text-slate-400"
                      >{{
                        scopedTasks.length
                          ? Math.round((item.value / scopedTasks.length) * 100)
                          : 0
                      }}%</span
                    >
                  </li>
                </ul>
              </div>
            </section>
            <section class="ct-dashboard-deadlines ct-dashboard-card p-5">
              <div class="flex justify-between">
                <h2 class="text-lg font-semibold">Prazos próximos</h2>
                <RouterLink to="/calendario" class="text-sm text-blue-600">Ver todos</RouterLink>
              </div>
              <div class="mt-5">
                <button
                  v-for="[date, count] in nextDates"
                  :key="date"
                  type="button"
                  class="flex w-full items-center justify-between border-b border-slate-100 py-2 text-left text-xs last:border-0"
                  @click="selectDate(date)"
                >
                  <span class="flex items-center gap-3 text-slate-600"
                    ><AppNavIcon name="calendar" class="h-4 w-4 shrink-0" />{{
                      formatDeadlineDate(date)
                    }}</span
                  >
                  <span
                    class="rounded-full px-2 py-1"
                    :class="
                      date === todayIso ? 'bg-rose-50 text-rose-500' : 'bg-blue-50 text-blue-600'
                    "
                    >{{ count }}</span
                  >
                </button>
                <p v-if="!nextDates.length" class="text-sm leading-6 text-slate-500">
                  Sem próximos vencimentos neste escopo.
                </p>
              </div>
            </section>
          </div>
        </div>
        <aside class="ct-dashboard-side space-y-4">
          <section class="ct-dashboard-calendar ct-dashboard-card p-5">
            <div class="flex items-center justify-between">
              <h2 class="text-lg font-semibold">Calendário</h2>
              <RouterLink to="/calendario" class="text-sm text-blue-600">Ver calendário</RouterLink>
            </div>
            <div class="ct-dashboard-month my-5 flex items-center justify-between">
              <h3 class="text-sm font-semibold">
                {{ calendarTitle.charAt(0).toUpperCase() + calendarTitle.slice(1) }}
              </h3>
              <div>
                <button
                  type="button"
                  class="px-3 py-1 text-slate-500"
                  aria-label="Mês anterior"
                  @click="monthOffset--"
                >
                  ‹</button
                ><button
                  type="button"
                  class="px-3 py-1 text-slate-500"
                  aria-label="Próximo mês"
                  @click="monthOffset++"
                >
                  ›
                </button>
              </div>
            </div>
            <div class="grid grid-cols-7 gap-y-1.5 text-center text-[13px]">
              <span
                v-for="(day, i) in ['D', 'S', 'T', 'Q', 'Q', 'S', 'S']"
                :key="i"
                class="py-2 text-slate-400"
                >{{ day }}</span
              ><button
                v-for="day in calendarDays"
                :key="day.iso"
                type="button"
                class="relative mx-auto flex h-[29px] w-[29px] items-center justify-center rounded-full"
                :class="
                  day.iso === todayIso
                    ? 'bg-blue-500 text-white'
                    : selectedDate === day.iso && taskTab === 'date'
                      ? 'bg-blue-100 text-blue-700'
                      : day.current
                        ? 'text-slate-600 hover:bg-blue-50'
                        : 'text-slate-300'
                "
                :aria-label="`${day.iso}: ${day.count} obrigações abertas`"
                :aria-pressed="selectedDate === day.iso && taskTab === 'date'"
                @click="selectDate(day.iso)"
              >
                {{ day.day
                }}<span
                  v-if="day.count"
                  class="absolute bottom-0.5 h-1 w-1 rounded-full"
                  :class="day.iso === todayIso ? 'bg-white' : 'bg-amber-400'"
                />
              </button>
            </div>
          </section>
          <section class="ct-dashboard-activity ct-dashboard-card p-5">
            <div class="flex items-center justify-between">
              <h2 class="text-lg font-semibold">Atividades recentes</h2>
              <RouterLink to="/obrigacoes" class="text-sm text-blue-600">Ver todas</RouterLink>
            </div>
            <div class="ct-dashboard-activity-list">
              <RouterLink
                v-for="task in recentTasks"
                :key="task.id"
                :to="taskLink(task)"
                class="relative mt-4 flex min-w-0 gap-3"
                ><span
                  class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-50 text-blue-500"
                  ><AppNavIcon name="folder"
                /></span>
                <div>
                  <p class="text-xs font-semibold">Obrigação criada</p>
                  <p class="mt-1 break-words text-xs text-slate-500">{{ task.title }}</p>
                  <p class="mt-1 text-xs text-slate-500">
                    {{ formatCreatedAt(task.created_at) }}
                  </p>
                </div></RouterLink
              >
            </div>
            <p v-if="!recentTasks.length" class="py-5 text-[15px] text-slate-500">
              Nenhuma obrigação cadastrada neste escopo.
            </p>
          </section>
        </aside>
      </div>
    </template>
  </div>
</template>
