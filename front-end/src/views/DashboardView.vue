<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import api from '../services/api'
import Layout from '../components/Layout.vue'
import { toast } from 'vue3-toastify'

const router = useRouter()

// ==========================================
// 1. TIPAGEM ESTRITA
// ==========================================
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

// ==========================================
// 2. ESTADOS TIPADOS
// ==========================================
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

// ==========================================
// 3. MÁGICA DOS DADOS (COMPUTED PROPERTIES)
// ==========================================
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

// ==========================================
// 4. CAPACIDADE DA EQUIPE (NOVO FORMATO)
// ==========================================
const cargaEquipe = computed(() => {
  const tarefasAtribuidas = officeTasks.value.filter(
    (t) => t.status !== 'concluida' && t.assigned_to,
  )
  const carga: Record<string, { nome: string; count: number; percentual: number }> = {}

  // Limite de tarefas para considerar sobrecarga (ex: 8 tarefas = 100% da capacidade visual)
  const LIMITE_CAPACIDADE = 8

  membros.value.forEach((m) => {
    carga[String(m.id)] = { nome: m.name, count: 0, percentual: 0 }
  })

  tarefasAtribuidas.forEach((t) => {
    const id = String(t.assigned_to)
    if (carga[id]) carga[id].count++
  })

  // Calcula o percentual da barra de capacidade
  Object.values(carga).forEach((m) => {
    m.percentual = Math.min((m.count / LIMITE_CAPACIDADE) * 100, 100)
  })

  return Object.values(carga).sort((a, b) => b.count - a.count)
})

// ==========================================
// 5. RELATÓRIO AVANÇADO
// ==========================================
const totalTarefasHistoricas = computed(() => officeTasks.value.length)

const taxaConclusao = computed(() => {
  if (totalTarefasHistoricas.value === 0) return 0
  return Math.round((countConcluidas.value / totalTarefasHistoricas.value) * 100)
})

const riscoMultas = computed(() => {
  if (dashData.value.tarefas_atrasadas > 5)
    return { label: 'Alto Risco', class: 'text-red-500', bg: 'bg-red-50' }
  if (dashData.value.tarefas_atrasadas > 0)
    return { label: 'Atenção', class: 'text-yellow-600', bg: 'bg-yellow-50' }
  return { label: 'Conforme', class: 'text-emerald-600', bg: 'bg-emerald-50' }
})

const hasRelatorioPremium = computed(() => {
  return dashData.value.plano === 'profissional' || dashData.value.plano === 'business'
})

// ==========================================
// 6. FOCO DO DIA E PRÓXIMOS PRAZOS
// ==========================================
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

// ==========================================
// 7. CHAMADAS À API E NAVEGAÇÃO
// ==========================================
const fetchData = async () => {
  isLoading.value = true
  try {
    const [dashRes, tasksRes] = await Promise.all([
      api.get('/api/v1/dashboard'),
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

// ==========================================
// 8. HELPERS FORMATAÇÃO E SELOS
// ==========================================
const getStatusColor = (status: string) => {
  if (status === 'concluida') return 'bg-[#19341a]'
  if (status === 'em_andamento') return 'bg-[#ff8a65]'
  if (status === 'aguardando_cliente') return 'bg-yellow-400'
  if (status === 'pendente') return 'bg-gray-400'
  return 'bg-gray-400'
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
    return 'bg-yellow-100 text-yellow-800'
  if (dashData.value.status_pagamento === 'inadimplente') return 'bg-red-100 text-red-800'
  if (dashData.value.plano === 'free') return 'bg-gray-100 text-gray-600'
  if (dashData.value.plano === 'basico') return 'bg-blue-100 text-blue-800'
  if (dashData.value.plano === 'profissional') return 'bg-[#eaf3ea] text-[#19341a]'
  if (dashData.value.plano === 'business') return 'bg-purple-100 text-purple-800'
  return 'bg-gray-100 text-gray-600'
})

const planoLabel = computed(() => {
  if (dashData.value.status_pagamento === 'aguardando_pagamento') return 'Pagamento Pendente'
  if (dashData.value.status_pagamento === 'inadimplente') return 'Conta Bloqueada'
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
    <!-- Cabeçalho com Selo do Plano -->
    <div class="mb-10 flex items-center justify-between flex-wrap gap-4">
      <div>
        <h1 class="text-3xl font-extrabold text-[#19341a] flex items-center gap-3 tracking-tight">
          Visão Geral
          <span
            class="text-[10px] font-bold px-2.5 py-1 rounded-full uppercase tracking-wider"
            :class="planoBadgeClass"
          >
            {{ planoLabel }}
          </span>
        </h1>
        <p class="text-[#2a2a2a]/50 text-sm mt-1">
          Acompanhe as métricas e o calendário do seu escritório.
        </p>
      </div>
    </div>

    <div v-if="isLoading" class="text-center text-[#2a2a2a]/50 py-10">Carregando métricas...</div>

    <div v-else class="space-y-10">
      <!-- BANNERS DE AÇÃO -->
      <div
        v-if="dashData.plano === 'free' && dashData.status_pagamento === 'ativo'"
        class="p-5 bg-[#eaf3ea] border border-[#19341a]/10 rounded-2xl flex flex-col sm:flex-row items-center justify-between gap-4"
      >
        <div class="flex items-center gap-3">
          <div
            class="h-10 w-10 rounded-xl bg-white flex items-center justify-center text-[#19341a] flex-shrink-0"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"
              ></path>
            </svg>
          </div>
          <div>
            <p class="font-bold text-[#19341a]">Você está no plano Free</p>
            <p class="text-sm text-gray-500">
              Você pode cadastrar até 5 clientes. Faça upgrade para liberar recursos ilimitados!
            </p>
          </div>
        </div>
        <RouterLink
          to="/faturamento"
          class="w-full sm:w-auto bg-[#ff8a65] text-white text-sm font-bold px-5 py-2.5 rounded-xl hover:bg-[#f07047] transition-colors text-center shadow-sm"
          >Fazer Upgrade</RouterLink
        >
      </div>

      <div
        v-else-if="dashData.status_pagamento === 'aguardando_pagamento'"
        class="p-5 bg-yellow-50 border border-yellow-100 rounded-2xl flex flex-col sm:flex-row items-center justify-between gap-4"
      >
        <div class="flex items-center gap-3">
          <div
            class="h-10 w-10 rounded-xl bg-white flex items-center justify-center text-yellow-500 flex-shrink-0"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              ></path>
            </svg>
          </div>
          <div>
            <p class="font-bold text-yellow-800">Pagamento Pendente</p>
            <p class="text-sm text-yellow-600">
              Estamos aguardando a compensação do seu pagamento para liberar todas as
              funcionalidades.
            </p>
          </div>
        </div>
        <RouterLink
          to="/faturamento"
          class="w-full sm:w-auto bg-yellow-500 text-white text-sm font-bold px-5 py-2.5 rounded-xl hover:bg-yellow-600 transition-colors text-center shadow-sm"
          >Verificar Pagamento</RouterLink
        >
      </div>

      <div
        v-else-if="dashData.status_pagamento === 'inadimplente'"
        class="p-5 bg-red-50 border border-red-100 rounded-2xl flex flex-col sm:flex-row items-center justify-between gap-4"
      >
        <div class="flex items-center gap-3">
          <div
            class="h-10 w-10 rounded-xl bg-white flex items-center justify-center text-red-500 flex-shrink-0"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              ></path>
            </svg>
          </div>
          <div>
            <p class="font-bold text-red-800">Conta Bloqueada</p>
            <p class="text-sm text-red-600">
              Detectamos um problema com sua assinatura. Regularize para voltar a usar o sistema.
            </p>
          </div>
        </div>
        <RouterLink
          to="/faturamento"
          class="w-full sm:w-auto bg-red-500 text-white text-sm font-bold px-5 py-2.5 rounded-xl hover:bg-red-600 transition-colors text-center shadow-sm"
          >Regularizar Agora</RouterLink
        >
      </div>

      <!-- Linha de KPIs (Mais limpos e arejados) -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div
          @click="goToClients"
          class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col gap-4 transition-all hover:shadow-md hover:-translate-y-1 cursor-pointer"
        >
          <div class="flex items-center justify-between">
            <p class="text-sm font-medium text-gray-400">Total de Clientes</p>
            <div class="h-9 w-9 rounded-lg bg-[#eaf3ea] flex items-center justify-center">
              <svg
                class="w-5 h-5 text-[#19341a]"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                ></path>
              </svg>
            </div>
          </div>
          <p class="text-4xl font-extrabold text-[#19341a] tracking-tight">
            {{ dashData.total_clientes }}
          </p>
        </div>

        <div
          @click="goToTasks"
          class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col gap-4 transition-all hover:shadow-md hover:-translate-y-1 cursor-pointer"
        >
          <div class="flex items-center justify-between">
            <p class="text-sm font-medium text-gray-400">Tarefas Abertas</p>
            <div class="h-9 w-9 rounded-lg bg-[#fff3e0] flex items-center justify-center">
              <svg
                class="w-5 h-5 text-[#ff8a65]"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                ></path>
              </svg>
            </div>
          </div>
          <p class="text-4xl font-extrabold text-[#19341a] tracking-tight">
            {{ dashData.tarefas_abertas }}
          </p>
        </div>

        <div
          @click="goToTasks"
          class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col gap-4 transition-all hover:shadow-md hover:-translate-y-1 cursor-pointer"
        >
          <div class="flex items-center justify-between">
            <p class="text-sm font-medium text-gray-400">Urgentes</p>
            <div class="h-9 w-9 rounded-lg bg-yellow-50 flex items-center justify-center">
              <svg
                class="w-5 h-5 text-yellow-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                ></path>
              </svg>
            </div>
          </div>
          <p class="text-4xl font-extrabold text-yellow-600 tracking-tight">{{ countUrgentes }}</p>
        </div>

        <div
          @click="goToTasks"
          class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col gap-4 transition-all hover:shadow-md hover:-translate-y-1 cursor-pointer"
        >
          <div class="flex items-center justify-between">
            <p class="text-sm font-medium text-gray-400">Atrasadas</p>
            <div class="h-9 w-9 rounded-lg bg-red-50 flex items-center justify-center">
              <svg
                class="w-5 h-5 text-red-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                ></path>
              </svg>
            </div>
          </div>
          <p class="text-4xl font-extrabold text-red-500 tracking-tight">
            {{ dashData.tarefas_atrasadas }}
          </p>
        </div>
      </div>

      <!-- Grid Principal (Respiro maior) -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div class="lg:col-span-1 space-y-8">
          <!-- Saúde dos Prazos -->
          <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <h3 class="text-lg font-bold text-[#19341a] mb-6 tracking-tight">Saúde dos Prazos</h3>
            <div v-if="totalStatus === 0" class="text-center text-gray-400 py-8">
              Nenhuma tarefa cadastrada.
            </div>
            <div v-else class="space-y-6">
              <div>
                <div class="flex justify-between mb-2">
                  <span class="text-xs font-medium text-gray-500">Distribuição Global</span>
                  <span class="text-xs font-bold text-gray-700">{{ totalStatus }} total</span>
                </div>
                <div class="w-full bg-gray-100 rounded-full h-3 flex overflow-hidden">
                  <div
                    :style="{ width: percConcluidas + '%' }"
                    class="bg-[#19341a] h-3 transition-all duration-500"
                  ></div>
                  <div
                    :style="{ width: percNoPrazo + '%' }"
                    class="bg-[#8ecba0] h-3 transition-all duration-500"
                  ></div>
                  <div
                    :style="{ width: percAtrasadas + '%' }"
                    class="bg-red-500 h-3 transition-all duration-500"
                  ></div>
                </div>
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div class="flex flex-col items-center bg-[#f9fafb] p-3 rounded-xl">
                  <p class="text-[10px] uppercase font-bold text-gray-400">Concluídas</p>
                  <p class="text-xl font-extrabold text-[#19341a]">{{ countConcluidas }}</p>
                </div>
                <div class="flex flex-col items-center bg-[#f9fafb] p-3 rounded-xl">
                  <p class="text-[10px] uppercase font-bold text-gray-400">Pendentes</p>
                  <p class="text-xl font-extrabold text-gray-700">{{ tarefasNoPrazo }}</p>
                </div>
                <div class="flex flex-col items-center bg-yellow-50 p-3 rounded-xl">
                  <p class="text-[10px] uppercase font-bold text-yellow-600">Aguard. Cliente</p>
                  <p class="text-xl font-extrabold text-yellow-700">{{ countAguardandoCliente }}</p>
                </div>
                <div class="flex flex-col items-center bg-red-50 p-3 rounded-xl">
                  <p class="text-[10px] uppercase font-bold text-red-500">Atrasadas</p>
                  <p class="text-xl font-extrabold text-red-600">
                    {{ dashData.tarefas_atrasadas }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Foco do Dia -->
          <div
            class="bg-[#19341a] p-6 rounded-2xl shadow-sm text-white flex flex-col min-h-[240px]"
          >
            <h3 class="text-lg font-bold mb-4 tracking-tight">Foco do Dia</h3>
            <div v-if="focoDoDiaTasks.length > 0" class="flex-1 space-y-3">
              <RouterLink
                to="/obrigacoes"
                v-for="task in focoDoDiaTasks"
                :key="task.id"
                class="block bg-white/5 p-4 rounded-xl border border-white/10 hover:bg-white/10 transition-all"
              >
                <div class="flex justify-between items-start mb-1 gap-2">
                  <span class="font-bold text-sm leading-tight">{{ task.title }}</span>
                  <div class="flex flex-col items-end gap-1">
                    <span
                      v-if="task.status === 'aguardando_cliente'"
                      class="text-[9px] bg-yellow-500 text-black px-1.5 py-0.5 rounded uppercase font-bold"
                      >Aguardando</span
                    >
                    <span
                      v-else-if="task.grau_importancia === 'Urgente'"
                      class="text-[9px] bg-red-500 text-white px-1.5 py-0.5 rounded uppercase font-bold"
                      >Urgente</span
                    >
                    <span
                      v-else-if="task.grau_importancia === 'Alta'"
                      class="text-[9px] bg-orange-500 text-white px-1.5 py-0.5 rounded uppercase font-bold"
                      >Alta</span
                    >
                  </div>
                </div>
                <div class="text-white/50 text-xs flex justify-between items-center mt-2">
                  <span>Prazo: {{ formatDate(task.due_date) }}</span>
                  <span>Ver →</span>
                </div>
              </RouterLink>
            </div>
            <div v-else class="flex-1 flex flex-col items-center justify-center text-center">
              <div class="w-12 h-12 bg-white/5 rounded-full flex items-center justify-center mb-3">
                🎉
              </div>
              <p class="text-white/60 text-sm">Tudo sob controle! Nenhuma pendência urgente.</p>
            </div>
          </div>
        </div>

        <!-- Próximos 7 Dias -->
        <div class="lg:col-span-2 bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg font-bold text-[#19341a] tracking-tight">Próximos 7 Dias</h3>
            <RouterLink
              to="/calendario"
              class="text-xs font-bold text-[#ff8a65] hover:text-[#f07047] transition-colors"
              >Ver Calendário →</RouterLink
            >
          </div>
          <div class="space-y-4">
            <div
              v-for="task in proximosPrazos"
              :key="task.id"
              class="flex items-center justify-between p-4 rounded-xl hover:bg-gray-50 border border-gray-100 transition-colors"
            >
              <div class="flex items-center gap-4">
                <div
                  class="w-2.5 h-2.5 rounded-full flex-shrink-0"
                  :class="getStatusColor(task.status)"
                ></div>
                <div>
                  <p class="text-sm font-semibold text-[#19341a]">{{ task.title }}</p>
                  <p class="text-xs text-gray-400">
                    {{ task.type === 'receita_federal' ? 'Prazo Federal' : 'Tarefa Interna' }}
                  </p>
                </div>
              </div>
              <div class="text-right">
                <p class="text-sm font-bold text-gray-700">
                  {{ formatDate(task.due_date || task.date) }}
                </p>
                <p class="text-[10px] uppercase font-bold text-gray-400">
                  {{ getDayName(task.due_date || task.date) }}
                </p>
              </div>
            </div>
            <div v-if="proximosPrazos.length === 0" class="text-center py-8 text-gray-400 text-sm">
              Nenhum prazo para os próximos 7 dias. 🎉
            </div>
          </div>
        </div>
      </div>

      <!-- CAPACIDADE DA EQUIPE (Estilo Karbon) -->
      <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h3 class="text-lg font-bold text-[#19341a] tracking-tight">Capacidade da Equipe</h3>
            <p class="text-xs text-gray-400 mt-1">Distribuição de tarefas em aberto.</p>
          </div>
        </div>
        <div v-if="cargaEquipe.length === 0" class="text-center py-8 text-gray-400 text-sm">
          Nenhum membro cadastrado ou sem tarefas atribuídas.
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div v-for="membro in cargaEquipe" :key="membro.nome" class="flex items-center gap-4">
            <div
              class="w-10 h-10 rounded-full bg-[#eaf3ea] text-[#19341a] flex items-center justify-center font-bold flex-shrink-0"
            >
              {{ getIniciaisMembro(membro.nome) }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex justify-between items-center mb-1">
                <p class="text-sm font-bold text-[#19341a] truncate">{{ membro.nome }}</p>
                <span
                  class="text-xs font-bold"
                  :class="membro.count > 5 ? 'text-orange-500' : 'text-gray-400'"
                >
                  {{ membro.count }} tarefas
                </span>
              </div>
              <!-- Barra de Capacidade -->
              <div class="w-full bg-gray-100 rounded-full h-2">
                <div
                  class="h-2 rounded-full transition-all duration-500"
                  :class="membro.count > 5 ? 'bg-orange-500' : 'bg-[#19341a]'"
                  :style="{ width: membro.percentual + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- RELATÓRIO AVANÇADO (PREMIUM) -->
      <div
        class="relative bg-white p-6 rounded-2xl shadow-sm border border-gray-100 overflow-hidden"
      >
        <div :class="{ 'blur-sm pointer-events-none select-none': !hasRelatorioPremium }">
          <div class="flex items-center justify-between mb-6">
            <div>
              <h3 class="text-lg font-bold text-[#19341a] flex items-center gap-2 tracking-tight">
                Relatório de Produtividade
                <span
                  class="text-[9px] font-bold bg-[#19341a] text-white px-1.5 py-0.5 rounded uppercase"
                  >Premium</span
                >
              </h3>
              <p class="text-xs text-gray-400 mt-1">
                Análise quantitativa do desempenho do seu escritório.
              </p>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="bg-[#f9fafb] p-5 rounded-xl border border-gray-100">
              <p class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">
                Taxa de Conclusão
              </p>
              <div class="flex items-end gap-2 mb-3">
                <p class="text-4xl font-extrabold text-[#19341a]">{{ taxaConclusao }}%</p>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2.5">
                <div
                  class="bg-[#19341a] h-2.5 rounded-full"
                  :style="{ width: taxaConclusao + '%' }"
                ></div>
              </div>
            </div>

            <div class="bg-[#f9fafb] p-5 rounded-xl border border-gray-100">
              <p class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">
                Risco de Multas
              </p>
              <div class="flex items-end gap-2 mb-3">
                <p class="text-4xl font-extrabold" :class="riscoMultas.class">
                  {{ riscoMultas.label }}
                </p>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2.5 flex overflow-hidden">
                <div
                  class="bg-red-500 h-2.5"
                  :style="{ width: (dashData.tarefas_atrasadas > 0 ? '100' : '0') + '%' }"
                ></div>
              </div>
            </div>

            <div class="bg-[#f9fafb] p-5 rounded-xl border border-gray-100">
              <p class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">
                Volume de Entregas
              </p>
              <div class="flex items-end gap-2 mb-3">
                <p class="text-4xl font-extrabold text-[#ff8a65]">{{ countConcluidas }}</p>
                <span class="text-sm text-gray-400 mb-1">tarefas</span>
              </div>
              <div class="flex gap-1 h-2.5">
                <div class="flex-1 bg-[#ff8a65]/30 rounded-sm h-full"></div>
                <div class="flex-1 bg-[#ff8a65]/50 rounded-sm h-full"></div>
                <div class="flex-1 bg-[#ff8a65]/70 rounded-sm h-full"></div>
                <div class="flex-1 bg-[#ff8a65] rounded-sm h-full"></div>
              </div>
            </div>
          </div>
        </div>

        <div
          v-if="!hasRelatorioPremium"
          class="absolute inset-0 flex flex-col items-center justify-center bg-white/40 backdrop-blur-[2px] z-10"
        >
          <div class="text-center p-6 max-w-sm">
            <div
              class="w-14 h-14 bg-[#19341a] text-white rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg"
            >
              <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                ></path>
              </svg>
            </div>
            <h4 class="text-xl font-extrabold text-[#19341a] mb-2">Recurso Premium</h4>
            <p class="text-gray-500 text-sm mb-5">
              Os Relatórios Avançados de Produtividade estão disponíveis apenas para os planos
              Profissional e Business.
            </p>
            <RouterLink
              to="/faturamento"
              class="inline-flex items-center gap-2 bg-[#ff8a65] text-white font-bold px-6 py-2.5 rounded-xl hover:bg-[#f07047] transition-colors shadow-sm"
            >
              Fazer Upgrade Agora
            </RouterLink>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>
