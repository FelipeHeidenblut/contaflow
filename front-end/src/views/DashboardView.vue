<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import api from '../services/api'
import Layout from '../components/Layout.vue'
import { toast } from 'vue3-toastify'

const router = useRouter()

interface TaskData {
  id: string | number
  title: string
  description?: string
  status: string
  due_date?: string
  date?: string
  type: 'task' | 'receita_federal'
  grau_importancia?: string
  client_id?: string | number
  assigned_to?: string | number | null
}

interface Membro {
  id: string | number
  name: string
}

const isLoading = ref(true)

const dashData = ref({
  total_clientes: 0,
  tarefas_abertas: 0,
  tarefas_atrasadas: 0,
  plano: '',
  status_pagamento: '',
})

const tasks = ref<TaskData[]>([])
const membros = ref<Membro[]>([])

const officeTasks = computed(() => tasks.value.filter((t) => t.type === 'task'))

const countUrgentes = computed(
  () =>
    officeTasks.value.filter((t) => t.grau_importancia === 'Urgente' && t.status !== 'concluida')
      .length,
)

const countConcluidas = computed(
  () => officeTasks.value.filter((t) => t.status === 'concluida').length,
)

const countAguardandoCliente = computed(
  () => officeTasks.value.filter((t) => t.status === 'aguardando_cliente').length,
)

const totalStatus = computed(() => dashData.value.tarefas_abertas + countConcluidas.value)

const percConcluidas = computed(() =>
  totalStatus.value > 0 ? (countConcluidas.value / totalStatus.value) * 100 : 0,
)

const percAtrasadas = computed(() =>
  totalStatus.value > 0 ? (dashData.value.tarefas_atrasadas / totalStatus.value) * 100 : 0,
)

const percNoPrazo = computed(() =>
  totalStatus.value > 0
    ? ((dashData.value.tarefas_abertas - dashData.value.tarefas_atrasadas) / totalStatus.value) *
      100
    : 0,
)

const tarefasNoPrazo = computed(
  () => dashData.value.tarefas_abertas - dashData.value.tarefas_atrasadas,
)

const cargaEquipe = computed(() => {
  const tarefasAtribuidas = officeTasks.value.filter(
    (t) => t.status !== 'concluida' && t.assigned_to,
  )
  const carga: Record<string, { nome: string; count: number; percentual: number }> = {}
  const LIMITE_CAPACIDADE = 8

  membros.value.forEach((m) => {
    carga[String(m.id)] = { nome: m.name, count: 0, percentual: 0 }
  })

  tarefasAtribuidas.forEach((t) => {
    const id = String(t.assigned_to)
    if (carga[id]) carga[id].count++
  })

  Object.values(carga).forEach((m) => {
    m.percentual = Math.min((m.count / LIMITE_CAPACIDADE) * 100, 100)
  })

  return Object.values(carga).sort((a, b) => b.count - a.count)
})

const totalTarefasHistoricas = computed(() => officeTasks.value.length)

const taxaConclusao = computed(() => {
  if (totalTarefasHistoricas.value === 0) return 0
  return Math.round((countConcluidas.value / totalTarefasHistoricas.value) * 100)
})

const riscoMultas = computed(() => {
  if (dashData.value.tarefas_atrasadas > 5)
    return { label: 'Alto risco', class: 'text-red-600', bg: 'bg-red-50', bar: 'bg-red-500' }
  if (dashData.value.tarefas_atrasadas > 0)
    return {
      label: 'Atenção',
      class: 'text-amber-600',
      bg: 'bg-amber-50',
      bar: 'bg-amber-500',
    }
  return {
    label: 'Conforme',
    class: 'text-emerald-600',
    bg: 'bg-emerald-50',
    bar: 'bg-emerald-500',
  }
})

const hasRelatorioPremium = computed(() => {
  return dashData.value.plano === 'profissional' || dashData.value.plano === 'business'
})

const focoDoDiaTasks = computed(() => {
  const today = new Date()
  const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
  const abertas = officeTasks.value.filter(
    (t) => t.status !== 'concluida' && t.due_date && t.due_date <= todayStr,
  )
  const prioridadePeso: Record<string, number> = { Urgente: 4, Alta: 3, Média: 2, Baixa: 1 }

  return abertas
    .sort((a, b) => {
      const pesoA = prioridadePeso[a.grau_importancia || 'Média'] || 0
      const pesoB = prioridadePeso[b.grau_importancia || 'Média'] || 0
      if (pesoB !== pesoA) return pesoB - pesoA
      const dataA = a.due_date ? new Date(a.due_date).getTime() : 0
      const dataB = b.due_date ? new Date(b.due_date).getTime() : 0
      return dataA - dataB
    })
    .slice(0, 3)
})

const proximosPrazos = computed(() => {
  const today = new Date()
  const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
  const nextWeek = new Date(today)
  nextWeek.setDate(today.getDate() + 7)
  const nextWeekStr = `${nextWeek.getFullYear()}-${String(nextWeek.getMonth() + 1).padStart(2, '0')}-${String(nextWeek.getDate()).padStart(2, '0')}`

  return tasks.value
    .filter((t) => {
      const date = t.due_date || t.date
      return date && date > todayStr && date <= nextWeekStr
    })
    .sort((a, b) => (a.due_date || a.date || '').localeCompare(b.due_date || b.date || ''))
    .slice(0, 6)
})

const fetchData = async () => {
  isLoading.value = true
  try {
    const [dashRes, tasksRes] = await Promise.all([
      api.get('/api/v1/dashboard/'),
      api.get('/api/v1/obrigacoes'),
    ])

    dashData.value = dashRes.data
    const apiTasks: TaskData[] = tasksRes.data.map((t: any) => ({ ...t, type: 'task' }))

    try {
      const membrosRes = await api.get('/api/v1/membros')
      membros.value = membrosRes.data
    } catch (error) {
      membros.value = []
    }

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
    toast.error('Erro ao carregar os dados do dashboard.')
  } finally {
    isLoading.value = false
  }
}

const goToClients = () => router.push('/clientes')
const goToTasks = () => router.push('/obrigacoes')

const getStatusColor = (status: string) => {
  if (status === 'concluida') return 'bg-emerald-500'
  if (status === 'em_andamento') return 'bg-[var(--ct-primary)]'
  if (status === 'aguardando_cliente') return 'bg-amber-400'
  if (status === 'pendente') return 'bg-slate-400'
  return 'bg-slate-400'
}

const formatDate = (dateString?: string) => {
  if (!dateString) return '-'
  const [year, month, day] = dateString.split('-')
  return `${day}/${month}`
}

const getDayName = (dateString?: string) => {
  if (!dateString) return '-'
  const date = new Date(dateString + 'T00:00:00')
  return date.toLocaleDateString('pt-BR', { weekday: 'short' }).replace('.', '')
}

const getIniciaisMembro = (nome: string) => {
  if (!nome) return '?'
  const partes = nome
    .trim()
    .split(' ')
    .filter((p) => p)

  if (partes.length === 0) return '?'
  if (partes.length === 1) return (partes[0]?.charAt(0) || '?').toUpperCase()

  const primeiraLetra = partes[0]?.charAt(0) || ''
  const ultimaLetra = partes[partes.length - 1]?.charAt(0) || ''
  return (primeiraLetra + ultimaLetra).toUpperCase() || '?'
}

const planoBadgeClass = computed(() => {
  if (dashData.value.status_pagamento === 'aguardando_pagamento')
    return 'bg-amber-100 text-amber-700 border border-amber-200'
  if (dashData.value.status_pagamento === 'inadimplente')
    return 'bg-red-100 text-red-700 border border-red-200'
  if (dashData.value.plano === 'free') return 'bg-slate-100 text-slate-600 border border-slate-200'
  if (dashData.value.plano === 'basico')
    return 'bg-blue-100 text-blue-700 border border-blue-200'
  if (dashData.value.plano === 'profissional')
    return 'bg-[var(--ct-primary-soft)] text-[var(--ct-primary)] border border-[#BFDBFE]'
  if (dashData.value.plano === 'business')
    return 'bg-violet-100 text-violet-700 border border-violet-200'
  return 'bg-slate-100 text-slate-600 border border-slate-200'
})

const planoLabel = computed(() => {
  if (dashData.value.status_pagamento === 'aguardando_pagamento') return 'Pagamento pendente'
  if (dashData.value.status_pagamento === 'inadimplente') return 'Conta bloqueada'

  const map: Record<string, string> = {
    free: 'Free',
    basico: 'Básico',
    profissional: 'Profissional',
    business: 'Business',
  }

  return map[dashData.value.plano] || 'Free'
})

onMounted(() => fetchData())
</script>

<template>
  <Layout title="Dashboard">
    <div class="space-y-6 text-[var(--ct-ink)]">
      <!-- Cabeçalho -->
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 class="flex items-center gap-3 text-[28px] font-semibold tracking-tight text-[var(--ct-ink)]">
            Visão geral
            <span class="rounded-full px-2.5 py-1 text-[10px] font-medium uppercase tracking-[0.14em]" :class="planoBadgeClass">
              {{ planoLabel }}
            </span>
          </h1>
          <p class="mt-1 text-sm text-[var(--ct-text-muted)]">Acompanhe métricas, equipe e próximos prazos do escritório.</p>
        </div>
      </div>

      <!-- Banners -->
      <div v-if="!isLoading && dashData.plano === 'free' && dashData.status_pagamento === 'ativo'" class="flex flex-col items-start justify-between gap-4 rounded-xl border border-[#BFDBFE] bg-[var(--ct-primary-soft)]/50 p-4 sm:flex-row sm:items-center">
        <div class="flex items-start gap-3">
          <div class="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg bg-white text-[var(--ct-primary)]">
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" /></svg>
          </div>
          <div>
            <p class="font-medium text-[var(--ct-ink)]">Você está no plano Free</p>
            <p class="text-xs text-[var(--ct-text-muted)]">Cadastre até 5 clientes e faça upgrade para liberar mais recursos.</p>
          </div>
        </div>
        <RouterLink to="/faturamento" class="w-full rounded-lg bg-[var(--ct-primary)] px-4 py-2 text-center text-xs font-semibold text-white transition-colors hover:bg-[var(--ct-primary-hover)] sm:w-auto">Fazer upgrade</RouterLink>
      </div>

      <div v-else-if="!isLoading && dashData.status_pagamento === 'aguardando_pagamento'" class="flex flex-col items-start justify-between gap-4 rounded-xl border border-amber-200 bg-amber-50 p-4 sm:flex-row sm:items-center">
        <div class="flex items-start gap-3">
          <div class="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg bg-white text-amber-500">
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          </div>
          <div>
            <p class="font-medium text-amber-800">Pagamento pendente</p>
            <p class="text-xs text-amber-700">Estamos aguardando a compensação para liberar todas as funcionalidades.</p>
          </div>
        </div>
        <RouterLink to="/faturamento" class="w-full rounded-lg bg-amber-500 px-4 py-2 text-center text-xs font-semibold text-white transition-colors hover:bg-amber-600 sm:w-auto">Verificar pagamento</RouterLink>
      </div>

      <div v-else-if="!isLoading && dashData.status_pagamento === 'inadimplente'" class="flex flex-col items-start justify-between gap-4 rounded-xl border border-red-200 bg-red-50 p-4 sm:flex-row sm:items-center">
        <div class="flex items-start gap-3">
          <div class="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg bg-white text-red-500">
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
          </div>
          <div>
            <p class="font-medium text-red-800">Conta bloqueada</p>
            <p class="text-xs text-red-700">Detectamos um problema com sua assinatura. Regularize para voltar a usar o sistema.</p>
          </div>
        </div>
        <RouterLink to="/faturamento" class="w-full rounded-lg bg-red-500 px-4 py-2 text-center text-xs font-semibold text-white transition-colors hover:bg-red-600 sm:w-auto">Regularizar agora</RouterLink>
      </div>

      <!-- KPIs com Skeleton -->
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <!-- Clientes -->
        <div v-if="isLoading" class="rounded-xl border border-[var(--ct-border)] bg-white p-5 shadow-sm">
          <div class="mb-3 flex items-center justify-between"><div class="h-3 w-24 animate-pulse rounded bg-slate-200"></div><div class="h-8 w-8 animate-pulse rounded-lg bg-slate-200"></div></div>
          <div class="h-8 w-16 animate-pulse rounded bg-slate-200"></div>
        </div>
        <button v-else type="button" @click="goToClients" class="group flex flex-col gap-3 rounded-xl border border-transparent bg-white p-5 text-left shadow-sm transition-all hover:-translate-y-0.5 hover:border-[var(--ct-border)] hover:shadow-md cursor-pointer">
          <div class="flex items-center justify-between">
            <p class="text-xs font-medium text-[var(--ct-text-muted)]">Total de clientes</p>
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--ct-primary-soft)]">
              <svg class="h-4 w-4 text-[var(--ct-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
            </div>
          </div>
          <div class="flex items-end justify-between">
            <p class="text-3xl font-semibold tracking-tight text-[var(--ct-ink)] [font-variant-numeric:tabular-nums]">{{ dashData.total_clientes }}</p>
            <svg class="h-4 w-4 text-slate-300 opacity-0 transition-opacity group-hover:opacity-100" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M13 6l6 6-6 6" /></svg>
          </div>
        </button>

        <!-- Tarefas abertas -->
        <div v-if="isLoading" class="rounded-xl border border-[var(--ct-border)] bg-white p-5 shadow-sm">
          <div class="mb-3 flex items-center justify-between"><div class="h-3 w-24 animate-pulse rounded bg-slate-200"></div><div class="h-8 w-8 animate-pulse rounded-lg bg-slate-200"></div></div>
          <div class="h-8 w-16 animate-pulse rounded bg-slate-200"></div>
        </div>
        <button v-else type="button" @click="goToTasks" class="group flex flex-col gap-3 rounded-xl border border-transparent bg-white p-5 text-left shadow-sm transition-all hover:-translate-y-0.5 hover:border-[var(--ct-border)] hover:shadow-md cursor-pointer">
          <div class="flex items-center justify-between">
            <p class="text-xs font-medium text-[var(--ct-text-muted)]">Tarefas abertas</p>
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-50">
              <svg class="h-4 w-4 text-[var(--ct-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            </div>
          </div>
          <div class="flex items-end justify-between">
            <p class="text-3xl font-semibold tracking-tight text-[var(--ct-ink)] [font-variant-numeric:tabular-nums]">{{ dashData.tarefas_abertas }}</p>
            <svg class="h-4 w-4 text-slate-300 opacity-0 transition-opacity group-hover:opacity-100" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M13 6l6 6-6 6" /></svg>
          </div>
        </button>

        <!-- Urgentes -->
        <div v-if="isLoading" class="rounded-xl border border-[var(--ct-border)] bg-white p-5 shadow-sm">
          <div class="mb-3 flex items-center justify-between"><div class="h-3 w-16 animate-pulse rounded bg-slate-200"></div><div class="h-8 w-8 animate-pulse rounded-lg bg-slate-200"></div></div>
          <div class="h-8 w-12 animate-pulse rounded bg-slate-200"></div>
        </div>
        <button v-else type="button" @click="goToTasks" class="group flex flex-col gap-3 rounded-xl border border-transparent bg-white p-5 text-left shadow-sm transition-all hover:-translate-y-0.5 hover:border-[var(--ct-border)] hover:shadow-md cursor-pointer">
          <div class="flex items-center justify-between">
            <p class="text-xs font-medium text-[var(--ct-text-muted)]">Urgentes</p>
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-50">
              <svg class="h-4 w-4 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
            </div>
          </div>
          <div class="flex items-end justify-between">
            <p class="text-3xl font-semibold tracking-tight text-amber-600 [font-variant-numeric:tabular-nums]">{{ countUrgentes }}</p>
            <svg class="h-4 w-4 text-slate-300 opacity-0 transition-opacity group-hover:opacity-100" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M13 6l6 6-6 6" /></svg>
          </div>
        </button>

        <!-- Atrasadas -->
        <div v-if="isLoading" class="rounded-xl border border-[var(--ct-border)] bg-white p-5 shadow-sm">
          <div class="mb-3 flex items-center justify-between"><div class="h-3 w-20 animate-pulse rounded bg-slate-200"></div><div class="h-8 w-8 animate-pulse rounded-lg bg-slate-200"></div></div>
          <div class="h-8 w-12 animate-pulse rounded bg-slate-200"></div>
        </div>
        <button v-else type="button" @click="goToTasks" class="group flex flex-col gap-3 rounded-xl border border-transparent bg-white p-5 text-left shadow-sm transition-all hover:-translate-y-0.5 hover:border-[var(--ct-border)] hover:shadow-md cursor-pointer">
          <div class="flex items-center justify-between">
            <p class="text-xs font-medium text-[var(--ct-text-muted)]">Atrasadas</p>
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-red-50">
              <svg class="h-4 w-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            </div>
          </div>
          <div class="flex items-end justify-between">
            <p class="text-3xl font-semibold tracking-tight text-red-500 [font-variant-numeric:tabular-nums]">{{ dashData.tarefas_atrasadas }}</p>
            <svg class="h-4 w-4 text-slate-300 opacity-0 transition-opacity group-hover:opacity-100" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M13 6l6 6-6 6" /></svg>
          </div>
        </button>
      </div>

      <!-- Conteúdo principal -->
      <div class="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <div class="space-y-6 xl:col-span-1">
          <!-- Saúde -->
          <div class="rounded-xl border border-[var(--ct-border)] bg-white p-5 shadow-sm">
            <h3 class="mb-5 text-sm font-semibold tracking-tight text-[var(--ct-ink)]">Saúde dos prazos</h3>

            <div v-if="isLoading" class="space-y-4">
              <div class="h-3 w-full animate-pulse rounded bg-slate-200"></div>
              <div class="grid grid-cols-2 gap-3">
                <div class="h-16 animate-pulse rounded-xl bg-slate-200"></div>
                <div class="h-16 animate-pulse rounded-xl bg-slate-200"></div>
                <div class="h-16 animate-pulse rounded-xl bg-slate-200"></div>
                <div class="h-16 animate-pulse rounded-xl bg-slate-200"></div>
              </div>
            </div>

            <div v-else-if="totalStatus === 0" class="py-6 text-center text-xs text-[var(--ct-text-muted)]">Nenhuma tarefa cadastrada.</div>

            <div v-else class="space-y-5">
              <div>
                <div class="mb-2 flex justify-between">
                  <span class="text-[11px] font-medium text-[var(--ct-text-muted)]">Distribuição global</span>
                  <span class="text-[11px] font-semibold text-[var(--ct-ink)] [font-variant-numeric:tabular-nums]">{{ totalStatus }} total</span>
                </div>
                <div class="flex h-2 w-full overflow-hidden rounded-full bg-slate-100">
                  <div :style="{ width: percConcluidas + '%' }" class="h-2 bg-emerald-500 transition-all duration-500"></div>
                  <div :style="{ width: percNoPrazo + '%' }" class="h-2 bg-[var(--ct-primary)] transition-all duration-500"></div>
                  <div :style="{ width: percAtrasadas + '%' }" class="h-2 bg-red-500 transition-all duration-500"></div>
                </div>
              </div>

              <div class="grid grid-cols-2 gap-2">
                <div class="rounded-lg bg-slate-50 p-3 text-center">
                  <p class="text-[10px] font-semibold uppercase tracking-[0.12em] text-slate-400">Concluídas</p>
                  <p class="mt-1 text-xl font-semibold text-emerald-600 [font-variant-numeric:tabular-nums]">{{ countConcluidas }}</p>
                </div>
                <div class="rounded-lg bg-slate-50 p-3 text-center">
                  <p class="text-[10px] font-semibold uppercase tracking-[0.12em] text-slate-400">Pendentes</p>
                  <p class="mt-1 text-xl font-semibold text-[var(--ct-ink)] [font-variant-numeric:tabular-nums]">{{ tarefasNoPrazo }}</p>
                </div>
                <div class="rounded-lg bg-amber-50 p-3 text-center">
                  <p class="text-[10px] font-semibold uppercase tracking-[0.12em] text-amber-600">Aguardando</p>
                  <p class="mt-1 text-xl font-semibold text-amber-700 [font-variant-numeric:tabular-nums]">{{ countAguardandoCliente }}</p>
                </div>
                <div class="rounded-lg bg-red-50 p-3 text-center">
                  <p class="text-[10px] font-semibold uppercase tracking-[0.12em] text-red-500">Atrasadas</p>
                  <p class="mt-1 text-xl font-semibold text-red-600 [font-variant-numeric:tabular-nums]">{{ dashData.tarefas_atrasadas }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Foco do dia -->
          <div class="min-h-[200px] rounded-xl bg-[var(--ct-navy)] p-5 text-white shadow-sm">
            <h3 class="mb-4 text-sm font-semibold tracking-tight">Foco do dia</h3>

            <div v-if="isLoading" class="space-y-3">
              <div class="h-14 animate-pulse rounded-lg bg-white/5"></div>
              <div class="h-14 animate-pulse rounded-lg bg-white/5"></div>
              <div class="h-14 animate-pulse rounded-lg bg-white/5"></div>
            </div>

            <div v-else-if="focoDoDiaTasks.length > 0" class="space-y-2.5">
              <RouterLink to="/obrigacoes" v-for="task in focoDoDiaTasks" :key="task.id" class="block rounded-lg border border-white/10 bg-white/5 p-3.5 transition-all hover:bg-white/10">
                <div class="mb-1.5 flex items-start justify-between gap-2">
                  <span class="text-xs font-semibold leading-tight">{{ task.title }}</span>
                  <div class="flex flex-col items-end gap-1">
                    <span v-if="task.status === 'aguardando_cliente'" class="rounded bg-amber-400 px-1.5 py-0.5 text-[10px] font-semibold uppercase text-slate-900">Aguardando</span>
                    <span v-else-if="task.grau_importancia === 'Urgente'" class="rounded bg-red-500 px-1.5 py-0.5 text-[10px] font-semibold uppercase text-white">Urgente</span>
                    <span v-else-if="task.grau_importancia === 'Alta'" class="rounded bg-[var(--ct-primary)] px-1.5 py-0.5 text-[10px] font-semibold uppercase text-white">Alta</span>
                  </div>
                </div>
                <div class="mt-2 flex items-center justify-between text-[11px] text-white/70">
                  <span>Prazo: {{ formatDate(task.due_date) }}</span>
                  <span>Ver →</span>
                </div>
              </RouterLink>
            </div>

            <div v-else class="flex h-full flex-col items-center justify-center pt-4 text-center">
              <div class="mb-2 flex h-10 w-10 items-center justify-center rounded-full bg-white/5 text-xl">🎉</div>
              <p class="text-xs text-white/70">Tudo sob controle. Nenhuma pendência urgente.</p>
            </div>
          </div>
        </div>

        <!-- Próximos prazos -->
        <div class="rounded-xl border border-[var(--ct-border)] bg-white p-5 shadow-sm xl:col-span-2">
          <div class="mb-5 flex items-center justify-between">
            <h3 class="text-sm font-semibold tracking-tight text-[var(--ct-ink)]">Próximos 7 dias</h3>
            <RouterLink to="/calendario" class="text-[11px] font-semibold text-[var(--ct-primary)] transition-colors hover:text-[var(--ct-primary-hover)]">Ver calendário →</RouterLink>
          </div>

          <div v-if="isLoading" class="space-y-3">
            <div class="h-14 animate-pulse rounded-lg bg-slate-100"></div>
            <div class="h-14 animate-pulse rounded-lg bg-slate-100"></div>
            <div class="h-14 animate-pulse rounded-lg bg-slate-100"></div>
            <div class="h-14 animate-pulse rounded-lg bg-slate-100"></div>
          </div>

          <div v-else class="space-y-2.5">
            <div v-for="task in proximosPrazos" :key="task.id" class="flex items-center justify-between rounded-lg border border-[var(--ct-border)] p-3.5 transition-colors hover:bg-slate-50">
              <div class="flex items-center gap-3">
                <div class="h-2.5 w-2.5 flex-shrink-0 rounded-full" :class="getStatusColor(task.status)"></div>
                <div>
                  <p class="text-xs font-semibold text-[var(--ct-ink)]">{{ task.title }}</p>
                  <p class="text-[11px] text-[var(--ct-text-muted)]">{{ task.type === 'receita_federal' ? 'Prazo federal' : 'Tarefa interna' }}</p>
                </div>
              </div>
              <div class="text-right">
                <p class="text-xs font-semibold text-[var(--ct-ink)] [font-variant-numeric:tabular-nums]">{{ formatDate(task.due_date || task.date) }}</p>
                <p class="text-[10px] font-semibold uppercase tracking-[0.08em] text-slate-400">{{ getDayName(task.due_date || task.date) }}</p>
              </div>
            </div>

            <div v-if="proximosPrazos.length === 0" class="py-6 text-center text-xs text-[var(--ct-text-muted)]">Nenhum prazo para os próximos 7 dias. 🎉</div>
          </div>
        </div>
      </div>

      <!-- Equipe -->
      <div class="rounded-xl border border-[var(--ct-border)] bg-white p-5 shadow-sm">
        <div class="mb-5 flex items-center justify-between">
          <div>
            <h3 class="text-sm font-semibold tracking-tight text-[var(--ct-ink)]">Capacidade da equipe</h3>
            <p class="mt-0.5 text-xs text-[var(--ct-text-muted)]">Distribuição de tarefas em aberto.</p>
          </div>
        </div>

        <div v-if="isLoading" class="space-y-3">
          <div class="flex items-center gap-4"><div class="h-9 w-9 animate-pulse rounded-full bg-slate-200"></div><div class="flex-1 space-y-2"><div class="h-3 w-32 animate-pulse rounded bg-slate-200"></div><div class="h-2 w-full animate-pulse rounded-full bg-slate-200"></div></div></div>
          <div class="flex items-center gap-4"><div class="h-9 w-9 animate-pulse rounded-full bg-slate-200"></div><div class="flex-1 space-y-2"><div class="h-3 w-32 animate-pulse rounded bg-slate-200"></div><div class="h-2 w-full animate-pulse rounded-full bg-slate-200"></div></div></div>
        </div>

        <div v-else-if="cargaEquipe.length === 0" class="py-6 text-center text-xs text-[var(--ct-text-muted)]">Nenhum membro cadastrado ou sem tarefas atribuídas.</div>

        <div v-else class="grid grid-cols-1 gap-5 md:grid-cols-2">
          <div v-for="membro in cargaEquipe" :key="membro.nome" class="flex items-center gap-3">
            <div class="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-[var(--ct-primary-soft)] font-semibold text-[var(--ct-primary)] text-xs ring-2 ring-white">
              {{ getIniciaisMembro(membro.nome) }}
            </div>
            <div class="min-w-0 flex-1">
              <div class="mb-1.5 flex items-center justify-between">
                <p class="truncate text-xs font-semibold text-[var(--ct-ink)]">{{ membro.nome }}</p>
                <span class="text-[11px] font-semibold [font-variant-numeric:tabular-nums]" :class="membro.count > 8 ? 'text-red-600' : 'text-[var(--ct-text-muted)]'">
                  {{ membro.count }} tarefas
                </span>
              </div>
              <div class="h-1.5 w-full rounded-full bg-slate-100">
                <div class="h-1.5 rounded-full transition-all duration-500" :class="membro.count > 8 ? 'bg-red-500' : 'bg-[var(--ct-primary)]'" :style="{ width: membro.percentual + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Premium -->
      <div class="relative overflow-hidden rounded-xl border border-[var(--ct-border)] bg-white p-5 shadow-sm">
        <div v-if="isLoading" class="blur-sm">
          <div class="mb-5 flex items-center justify-between"><div class="space-y-2"><div class="h-4 w-40 animate-pulse rounded bg-slate-200"></div><div class="h-3 w-56 animate-pulse rounded bg-slate-200"></div></div></div>
          <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
            <div class="h-28 animate-pulse rounded-lg bg-slate-100"></div>
            <div class="h-28 animate-pulse rounded-lg bg-slate-100"></div>
            <div class="h-28 animate-pulse rounded-lg bg-slate-100"></div>
          </div>
        </div>

        <div :class="{ 'pointer-events-none select-none blur-sm': !hasRelatorioPremium && !isLoading }">
          <div class="mb-5 flex items-center justify-between">
            <div>
              <h3 class="flex items-center gap-2 text-sm font-semibold tracking-tight text-[var(--ct-ink)]">
                Relatório de produtividade
                <span class="rounded bg-[var(--ct-navy)] px-1.5 py-0.5 text-[10px] font-semibold uppercase text-white">Premium</span>
              </h3>
              <p class="mt-0.5 text-xs text-[var(--ct-text-muted)]">Análise quantitativa do desempenho do escritório.</p>
            </div>
          </div>

          <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
            <div class="rounded-lg border border-[var(--ct-border)] bg-slate-50 p-4">
              <p class="mb-2 text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-400">Taxa de conclusão</p>
              <div class="mb-2 flex items-end gap-2">
                <p class="text-3xl font-semibold text-[var(--ct-ink)] [font-variant-numeric:tabular-nums]">{{ taxaConclusao }}%</p>
              </div>
              <div class="h-2 w-full rounded-full bg-slate-200">
                <div class="h-2 rounded-full bg-[var(--ct-primary)]" :style="{ width: taxaConclusao + '%' }"></div>
              </div>
            </div>

            <div class="rounded-lg border border-[var(--ct-border)] bg-slate-50 p-4">
              <p class="mb-2 text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-400">Risco de multas</p>
              <div class="mb-2 flex items-end gap-2">
                <p class="text-3xl font-semibold [font-variant-numeric:tabular-nums]" :class="riscoMultas.class">{{ riscoMultas.label }}</p>
              </div>
              <div class="flex h-2 w-full overflow-hidden rounded-full bg-slate-200">
                <div class="h-2" :class="riscoMultas.bar" :style="{ width: (dashData.tarefas_atrasadas > 0 ? '100' : '0') + '%' }"></div>
              </div>
            </div>

            <div class="rounded-lg border border-[var(--ct-border)] bg-slate-50 p-4">
              <p class="mb-2 text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-400">Volume de entregas</p>
              <div class="mb-2 flex items-end gap-2">
                <p class="text-3xl font-semibold text-[var(--ct-primary)] [font-variant-numeric:tabular-nums]">{{ countConcluidas }}</p>
                <span class="mb-1 text-[11px] text-[var(--ct-text-muted)]">tarefas</span>
              </div>
              <div class="flex h-2 gap-1">
                <div class="h-full flex-1 rounded-sm bg-[#DBEAFE]"></div>
                <div class="h-full flex-1 rounded-sm bg-[#93C5FD]"></div>
                <div class="h-full flex-1 rounded-sm bg-[#60A5FA]"></div>
                <div class="h-full flex-1 rounded-sm bg-[var(--ct-primary)]"></div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="!hasRelatorioPremium && !isLoading" class="absolute inset-0 z-10 flex flex-col items-center justify-center bg-gradient-to-t from-white via-white/95 to-white/60 backdrop-blur-[2px]">
          <div class="max-w-xs p-5 text-center">
            <div class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-[var(--ct-navy)] text-white shadow-sm">
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
            </div>
            <h4 class="mb-1.5 text-base font-semibold text-[var(--ct-ink)]">Recurso premium</h4>
            <p class="mb-4 text-xs text-[var(--ct-text-muted)]">Os relatórios avançados estão disponíveis apenas nos planos Profissional e Business.</p>
            <RouterLink to="/faturamento" class="inline-flex items-center gap-2 rounded-lg bg-[var(--ct-primary)] px-5 py-2 text-xs font-semibold text-white transition-colors hover:bg-[var(--ct-primary-hover)]">Fazer upgrade agora</RouterLink>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<style scoped>
:global(:root) {
  --ct-bg: #F8FAFC;
  --ct-surface: #FFFFFF;
  --ct-muted: #F1F5F9;
  --ct-border: #E2E8F0;

  --ct-ink: #0F172A;
  --ct-text-muted: #64748B;

  --ct-primary: #2563EB;
  --ct-primary-hover: #1D4ED8;
  --ct-primary-soft: #DBEAFE;
  --ct-navy: #172554;
}
</style>