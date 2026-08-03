<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import api from '../services/api'
import Layout from '../components/Layout.vue'
import { toast } from 'vue3-toastify'

interface TaskData {
  id: string | number
  title: string
  description?: string
  status: string
  due_date?: string
  date?: string
  type: 'task' | 'receita_federal'
  grau_importancia?: string
}

interface CalendarDay {
  date: number | null
  tasks: TaskData[]
}

const isLoading = ref(true)
const tasks = ref<TaskData[]>([])
const currentDate = ref(new Date())

const isDayModalOpen = ref(false)
const selectedDayTasks = ref<TaskData[]>([])
const selectedDayTitle = ref('')

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://api.contablytask.com.br'
const icsUrl = ref('')
const copied = ref(false)

const carregarIcsUrl = async () => {
  try {
    const res = await api.get('/api/v1/auth/me')
    if (res.data.tenant_id) {
      icsUrl.value = `${API_BASE_URL}/api/v1/calendario/feed/${res.data.tenant_id}.ics`
    } else {
      console.warn('Backend não retornou tenant_id na rota /me')
    }
  } catch (error) {
    console.error('Erro ao buscar tenant_id para o link ICS:', error)
  }
}

const copyLink = async () => {
  try {
    await navigator.clipboard.writeText(icsUrl.value)
    copied.value = true
    toast.success('Link copiado! Cole no Google Agenda ou Outlook.')
    setTimeout(() => (copied.value = false), 3000)
  } catch (error) {
    toast.error('Não foi possível copiar o link.')
  }
}

const currentMonth = computed(() =>
  currentDate.value.toLocaleDateString('pt-BR', { month: 'long' }),
)
const currentYear = computed(() => currentDate.value.getFullYear())

const calendarDays = computed<CalendarDay[]>(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  const firstDayOfMonth = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()

  const days: CalendarDay[] = []

  for (let i = 0; i < firstDayOfMonth; i++) {
    days.push({ date: null, tasks: [] })
  }

  for (let day = 1; day <= daysInMonth; day++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
    const dayTasks = tasks.value.filter((t) => (t.due_date || t.date) === dateStr)
    days.push({ date: day, tasks: dayTasks })
  }

  return days
})

const totalPrazos = computed(() => tasks.value.length)
const totalFederais = computed(
  () => tasks.value.filter((task) => task.type === 'receita_federal').length,
)
const totalPendentes = computed(
  () => tasks.value.filter((task) => task.status === 'pendente').length,
)
const totalEmAndamento = computed(
  () => tasks.value.filter((task) => task.status === 'em_andamento').length,
)

const prevMonth = () => {
  currentDate.value = new Date(
    currentDate.value.getFullYear(),
    currentDate.value.getMonth() - 1,
    1,
  )
}

const nextMonth = () => {
  currentDate.value = new Date(
    currentDate.value.getFullYear(),
    currentDate.value.getMonth() + 1,
    1,
  )
}

const openDayModal = (day: CalendarDay) => {
  if (day.date && day.tasks.length > 0) {
    const dateObj = new Date(
      currentDate.value.getFullYear(),
      currentDate.value.getMonth(),
      day.date,
    )

    selectedDayTitle.value = dateObj.toLocaleDateString('pt-BR', {
      weekday: 'long',
      day: 'numeric',
      month: 'long',
    })

    selectedDayTasks.value = day.tasks
    isDayModalOpen.value = true
  }
}

const fetchData = async () => {
  isLoading.value = true
  try {
    const tasksRes = await api.get('/api/v1/obrigacoes')
    const apiTasks: TaskData[] = tasksRes.data.map((t: any) => ({ ...t, type: 'task' }))

    let federalTasks: TaskData[] = []
    try {
      const fiscalRes = await api.get('/api/v1/fiscal-deadlines')
      federalTasks = fiscalRes.data.map((f: any) => ({
        ...f,
        date: f.deadline_date,
        type: 'receita_federal',
      }))
    } catch (fiscalError) {
      console.warn('Rota de prazos fiscais com erro.')
    }

    tasks.value = [...apiTasks, ...federalTasks]
  } catch (error) {
    toast.error('Erro ao carregar o calendário.')
  } finally {
    isLoading.value = false
  }
}

const getStatusColor = (status: string) => {
  if (status === 'concluida') return 'bg-emerald-500'
  if (status === 'em_andamento') return 'bg-[var(--ct-primary)]'
  if (status === 'aguardando_cliente') return 'bg-amber-400'
  return 'bg-slate-400'
}

const getStatusBadge = (status: string) => {
  const styles: Record<string, string> = {
    concluida: 'bg-emerald-100 text-emerald-700 border-emerald-200',
    em_andamento: 'bg-blue-100 text-blue-700 border-blue-200',
    aguardando_cliente: 'bg-amber-100 text-amber-700 border-amber-200',
    pendente: 'bg-slate-100 text-slate-600 border-slate-200',
  }

  return `inline-flex rounded-md border px-2 py-0.5 text-[10px] font-bold ${styles[status] || styles.pendente}`
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    concluida: 'Concluída',
    em_andamento: 'Em andamento',
    aguardando_cliente: 'Aguardando cliente',
    pendente: 'Pendente',
  }
  return labels[status] || 'Pendente'
}

const isToday = (day: number) => {
  const today = new Date()
  return (
    day === today.getDate() &&
    currentDate.value.getMonth() === today.getMonth() &&
    currentDate.value.getFullYear() === today.getFullYear()
  )
}

onMounted(() => {
  fetchData()
  carregarIcsUrl()
})
</script>

<template>
  <Layout title="Calendário de Prazos">
    <div class="space-y-6">
      <!-- topo -->
      <header class="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
        <div>
          <h1 class="text-2xl font-semibold tracking-tight text-[var(--ct-ink)]">
            Calendário de prazos
          </h1>
          <p class="mt-1 text-sm text-[var(--ct-text-muted)]">
            Acompanhe vencimentos, obrigações internas e prazos fiscais em um só lugar.
          </p>
        </div>
      </header>

      <!-- indicadores -->
      <section class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div class="rounded-xl border border-[var(--ct-border)] bg-white p-4 shadow-sm">
          <p class="text-xs font-medium text-[var(--ct-text-muted)]">Total de prazos</p>
          <p class="mt-2 text-3xl font-semibold text-[var(--ct-ink)] [font-variant-numeric:tabular-nums]">
            {{ totalPrazos }}
          </p>
        </div>

        <div class="rounded-xl border border-[var(--ct-border)] bg-white p-4 shadow-sm">
          <p class="text-xs font-medium text-[var(--ct-text-muted)]">Prazos federais</p>
          <p class="mt-2 text-3xl font-semibold text-[var(--ct-ink)] [font-variant-numeric:tabular-nums]">
            {{ totalFederais }}
          </p>
        </div>

        <div class="rounded-xl border border-[var(--ct-border)] bg-white p-4 shadow-sm">
          <p class="text-xs font-medium text-[var(--ct-text-muted)]">Pendentes</p>
          <p class="mt-2 text-3xl font-semibold text-[var(--ct-ink)] [font-variant-numeric:tabular-nums]">
            {{ totalPendentes }}
          </p>
        </div>

        <div class="rounded-xl border border-[var(--ct-border)] bg-white p-4 shadow-sm">
          <p class="text-xs font-medium text-[var(--ct-text-muted)]">Em andamento</p>
          <p class="mt-2 text-3xl font-semibold text-[var(--ct-ink)] [font-variant-numeric:tabular-nums]">
            {{ totalEmAndamento }}
          </p>
        </div>
      </section>

      <!-- card ics -->
      <section
        v-if="icsUrl"
        class="flex flex-col gap-4 rounded-2xl border border-[var(--ct-border)] bg-white p-5 shadow-sm lg:flex-row lg:items-center lg:justify-between"
      >
        <div class="flex items-start gap-4">
          <div class="flex h-11 w-11 items-center justify-center rounded-xl bg-[var(--ct-primary-soft)] text-[var(--ct-primary)]">
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
          </div>

          <div>
            <p class="text-sm font-semibold text-[var(--ct-ink)]">
              Sincronizar com minha agenda
            </p>
            <p class="mt-1 text-sm text-[var(--ct-text-muted)]">
              Use este link no Google Agenda ou Outlook para acompanhar seus prazos fora da plataforma.
            </p>
          </div>
        </div>

        <div class="flex w-full flex-col gap-2 sm:flex-row lg:max-w-xl">
          <input
            type="text"
            readonly
            :value="icsUrl"
            class="w-full rounded-xl border border-[var(--ct-border)] bg-slate-50 px-3 py-2.5 text-xs text-slate-500 outline-none"
          />
          <button
            @click="copyLink"
            class="inline-flex items-center justify-center rounded-xl bg-[var(--ct-primary)] px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[var(--ct-primary-hover)] whitespace-nowrap"
          >
            {{ copied ? 'Copiado!' : 'Copiar link' }}
          </button>
        </div>
      </section>

      <!-- calendario -->
      <section class="rounded-2xl border border-[var(--ct-border)] bg-white p-4 shadow-sm md:p-6">
        <div class="mb-8 flex items-center justify-between">
          <div>
            <h2 class="text-2xl font-semibold capitalize tracking-tight text-[var(--ct-ink)]">
              {{ currentMonth }}
              <span class="font-medium text-slate-300">{{ currentYear }}</span>
            </h2>
            <p class="mt-1 text-sm text-[var(--ct-text-muted)]">
              Visualize seus prazos por dia e clique para ver os detalhes.
            </p>
          </div>

          <div class="flex items-center gap-2">
            <button
              @click="prevMonth"
              class="rounded-xl border border-[var(--ct-border)] bg-white p-2.5 text-slate-500 transition-colors hover:bg-slate-50 hover:text-[var(--ct-ink)]"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
              </svg>
            </button>

            <button
              @click="nextMonth"
              class="rounded-xl border border-[var(--ct-border)] bg-white p-2.5 text-slate-500 transition-colors hover:bg-slate-50 hover:text-[var(--ct-ink)]"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
              </svg>
            </button>
          </div>
        </div>

        <div v-if="isLoading" class="grid grid-cols-2 gap-3 md:grid-cols-4 xl:grid-cols-7">
          <div
            v-for="n in 14"
            :key="n"
            class="h-28 animate-pulse rounded-xl border border-slate-100 bg-slate-50"
          ></div>
        </div>

        <div v-else class="space-y-4">
          <!-- semana -->
          <div class="grid grid-cols-7 gap-2">
            <div class="py-2 text-center text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-400">
              Dom
            </div>
            <div class="py-2 text-center text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-400">
              Seg
            </div>
            <div class="py-2 text-center text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-400">
              Ter
            </div>
            <div class="py-2 text-center text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-400">
              Qua
            </div>
            <div class="py-2 text-center text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-400">
              Qui
            </div>
            <div class="py-2 text-center text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-400">
              Sex
            </div>
            <div class="py-2 text-center text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-400">
              Sáb
            </div>
          </div>

          <!-- grid -->
          <div class="grid grid-cols-7 gap-2">
            <div
              v-for="(day, index) in calendarDays"
              :key="index"
              @click="openDayModal(day)"
              class="flex min-h-[118px] flex-col rounded-2xl border p-2.5 transition-all"
              :class="[
                day.date
                  ? 'border-[var(--ct-border)] bg-white'
                  : 'border-transparent bg-slate-50/40',
                day.tasks.length > 0
                  ? 'cursor-pointer hover:border-[var(--ct-primary)]/25 hover:bg-slate-50'
                  : '',
              ]"
            >
              <template v-if="day.date">
                <div class="mb-2 flex justify-end">
                  <span
                    class="inline-flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold"
                    :class="
                      isToday(day.date)
                        ? 'bg-[var(--ct-primary)] text-white shadow-sm'
                        : 'text-slate-400'
                    "
                  >
                    {{ day.date }}
                  </span>
                </div>

                <div class="flex-1 space-y-1 overflow-hidden">
                  <template v-for="(task, tIndex) in day.tasks" :key="task.id">
                    <div
                      v-if="tIndex < 3"
                      class="group flex items-center gap-1.5 rounded-lg px-1.5 py-1"
                      :class="
                        task.type === 'receita_federal'
                          ? 'bg-amber-50'
                          : 'bg-slate-50'
                      "
                      :title="task.description || task.title"
                    >
                      <template v-if="task.type === 'receita_federal'">
                        <span class="text-[10px]">🏛️</span>
                        <span class="truncate text-[11px] font-semibold text-amber-700">
                          {{ task.title }}
                        </span>
                      </template>

                      <template v-else>
                        <div
                          class="h-2 w-2 flex-shrink-0 rounded-full"
                          :class="getStatusColor(task.status)"
                        ></div>
                        <span class="truncate text-[11px] font-medium text-slate-600">
                          {{ task.title }}
                        </span>
                      </template>
                    </div>
                  </template>

                  <div
                    v-if="day.tasks.length > 3"
                    class="rounded-md border border-blue-100 bg-blue-50 py-1 text-center text-[10px] font-bold text-blue-700"
                  >
                    + {{ day.tasks.length - 3 }} item(ns)
                  </div>
                </div>
              </template>
            </div>
          </div>

          <!-- legenda -->
          <div class="flex flex-wrap items-center gap-x-6 gap-y-2 border-t border-[var(--ct-border)] pt-5">
            <div class="flex items-center gap-2">
              <span class="text-sm">🏛️</span>
              <span class="text-xs font-medium text-[var(--ct-text-muted)]">Prazo federal</span>
            </div>

            <div class="flex items-center gap-2">
              <div class="h-2.5 w-2.5 rounded-full bg-emerald-500"></div>
              <span class="text-xs font-medium text-[var(--ct-text-muted)]">Concluída</span>
            </div>

            <div class="flex items-center gap-2">
              <div class="h-2.5 w-2.5 rounded-full bg-[var(--ct-primary)]"></div>
              <span class="text-xs font-medium text-[var(--ct-text-muted)]">Em andamento</span>
            </div>

            <div class="flex items-center gap-2">
              <div class="h-2.5 w-2.5 rounded-full bg-amber-400"></div>
              <span class="text-xs font-medium text-[var(--ct-text-muted)]">Aguardando cliente</span>
            </div>
          </div>
        </div>
      </section>

      <!-- modal dia -->
      <div
        v-if="isDayModalOpen"
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4 backdrop-blur-[2px]"
        @click="isDayModalOpen = false"
      >
        <div
          class="w-full max-w-xl overflow-hidden rounded-2xl border border-[var(--ct-border)] bg-white shadow-2xl"
          @click.stop
        >
          <div class="bg-[var(--ct-navy)] px-6 py-5">
            <div class="flex items-start justify-between gap-4">
              <div>
                <p class="text-[11px] font-bold uppercase tracking-[0.14em] text-white/50">
                  Prazos do dia
                </p>
                <h3 class="mt-1 text-xl font-semibold capitalize tracking-tight text-white">
                  {{ selectedDayTitle }}
                </h3>
              </div>

              <button
                @click="isDayModalOpen = false"
                class="rounded-lg p-1 text-white/50 transition-colors hover:bg-white/10 hover:text-white"
              >
                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>
          </div>

          <div class="max-h-[60vh] space-y-3 overflow-y-auto p-6">
            <div
              v-for="task in selectedDayTasks"
              :key="task.id"
              class="rounded-xl border p-4"
              :class="
                task.type === 'receita_federal'
                  ? 'border-amber-200 bg-amber-50'
                  : 'border-[var(--ct-border)] bg-slate-50/70'
              "
            >
              <div class="flex items-start gap-3">
                <div class="mt-0.5 flex-shrink-0">
                  <span v-if="task.type === 'receita_federal'" class="text-xl">🏛️</span>
                  <div
                    v-else
                    class="h-3 w-3 rounded-full"
                    :class="getStatusColor(task.status)"
                  ></div>
                </div>

                <div class="min-w-0 flex-1">
                  <p class="text-sm font-semibold text-[var(--ct-ink)]">
                    {{ task.title }}
                  </p>

                  <p
                    v-if="task.description"
                    class="mt-1 text-xs leading-relaxed text-[var(--ct-text-muted)]"
                  >
                    {{ task.description }}
                  </p>

                  <div class="mt-3 flex flex-wrap items-center gap-2">
                    <span v-if="task.type !== 'receita_federal'" :class="getStatusBadge(task.status)">
                      {{ getStatusLabel(task.status) }}
                    </span>

                    <span
                      v-if="task.grau_importancia"
                      class="inline-flex rounded-md border border-slate-200 bg-white px-2 py-0.5 text-[10px] font-bold uppercase text-slate-500"
                    >
                      ⚡ {{ task.grau_importancia }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="flex justify-end border-t border-[var(--ct-border)] bg-slate-50 px-6 py-4">
            <RouterLink
              to="/obrigacoes"
              class="inline-flex items-center rounded-xl bg-[var(--ct-primary)] px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[var(--ct-primary-hover)]"
            >
              Gerenciar tarefas
            </RouterLink>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>