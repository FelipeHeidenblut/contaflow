<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'
import Layout from '../components/Layout.vue'
import { toast } from 'vue3-toastify'
import OperationalDashboard from '../components/OperationalDashboard.vue'

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

interface FederalDeadline {
  id: string | number
  title: string
  description?: string
  deadline_date: string
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
    const [dashResult, tasksResult, membrosResult, fiscalResult] = await Promise.allSettled([
      api.get('/api/v1/dashboard/'),
      api.get('/api/v1/obrigacoes'),
      api.get('/api/v1/membros'),
      api.get('/api/v1/fiscal-deadlines'),
    ])

    if (dashResult.status === 'rejected') throw dashResult.reason
    if (tasksResult.status === 'rejected') throw tasksResult.reason

    dashData.value = dashResult.value.data
    const apiTasks: TaskData[] = tasksResult.value.data.map((t: Omit<TaskData, 'type'>) => ({
      ...t,
      type: 'task',
    }))

    membros.value = membrosResult.status === 'fulfilled' ? membrosResult.value.data : []

    const federalTasks: TaskData[] =
      fiscalResult.status === 'fulfilled'
        ? fiscalResult.value.data.map((f: FederalDeadline) => ({
            ...f,
            date: f.deadline_date,
            type: 'receita_federal',
          }))
        : []
    if (fiscalResult.status === 'rejected') {
      console.warn('Rota de prazos fiscais com erro.')
    }

    tasks.value = [...apiTasks, ...federalTasks]
  } catch {
    toast.error('Erro ao carregar os dados do dashboard.')
  } finally {
    isLoading.value = false
  }
}

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
    <OperationalDashboard
      :loading="isLoading"
      :dashboard="dashData"
      :plan-label="planoLabel"
      :urgent-count="countUrgentes"
      :completed-count="countConcluidas"
      :awaiting-count="countAguardandoCliente"
      :on-time-count="tarefasNoPrazo"
      :total-status="totalStatus"
      :completion-percent="percConcluidas"
      :on-time-percent="percNoPrazo"
      :overdue-percent="percAtrasadas"
      :daily-focus="focoDoDiaTasks"
      :upcoming="proximosPrazos"
      :team="cargaEquipe"
      :has-premium="hasRelatorioPremium"
      :completion-rate="taxaConclusao"
      :fine-risk="riscoMultas"
    />
  </Layout>
</template>
