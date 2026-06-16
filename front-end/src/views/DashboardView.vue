<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'
import Layout from '../components/Layout.vue'
import { toast } from 'vue3-toastify'

// ==========================================
// 1. TIPAGEM ESTRITA (O fim do tipo 'any')
// ==========================================
interface TaskData {
  id: string | number
  title: string
  description?: string
  status: string
  due_date?: string
  date?: string // Usado pelas obrigações da Receita Federal
  type: 'task' | 'receita_federal'
  grau_importancia?: string
  client_id?: string | number
}

interface CalendarDay {
  date: number | null
  tasks: TaskData[]
}

// ==========================================
// 2. ESTADOS TIPADOS
// ==========================================
const isLoading = ref(true)

const dashData = ref({
  total_clientes: 0,
  tarefas_abertas: 0,
  tarefas_atrasadas: 0,
})

// Tipagem aplicada: O TypeScript agora tem certeza absoluta que é um Array de TaskData
const tasks = ref<TaskData[]>([])
const currentDate = ref(new Date())

// ==========================================
// 3. MÁGICA DOS DADOS (COMPUTED PROPERTIES)
// ==========================================

// Filtra apenas as tarefas normais (ignora Receita Federal para as estatísticas internas)
const officeTasks = computed(() => tasks.value.filter(t => t.type === 'task'))

// Cálculos para os novos Cards e Gráfico
const countUrgentes = computed(() => 
  officeTasks.value.filter(t => t.grau_importancia === 'Urgente' && t.status !== 'concluida').length
)
const countConcluidas = computed(() => 
  officeTasks.value.filter(t => t.status === 'concluida').length
)
const totalStatus = computed(() => dashData.value.tarefas_abertas + countConcluidas.value)

// Percentagens para a Barra de "Saúde dos Prazos"
const percConcluidas = computed(() => totalStatus.value > 0 ? (countConcluidas.value / totalStatus.value) * 100 : 0)
const percAtrasadas = computed(() => totalStatus.value > 0 ? (dashData.value.tarefas_atrasadas / totalStatus.value) * 100 : 0)
const percNoPrazo = computed(() => totalStatus.value > 0 ? ((dashData.value.tarefas_abertas - dashData.value.tarefas_atrasadas) / totalStatus.value) * 100 : 0)

const tarefasNoPrazo = computed(() => dashData.value.tarefas_abertas - dashData.value.tarefas_atrasadas)

// Inteligência do Foco do Dia (As 3 Tarefas mais críticas)
const focoDoDiaTasks = computed(() => {
  const abertas = officeTasks.value.filter(t => t.status !== 'concluida')
  
  const prioridadePeso: Record<string, number> = { 'Urgente': 4, 'Alta': 3, 'Média': 2, 'Baixa': 1 }
  
  return abertas.sort((a, b) => {
    const pesoA = prioridadePeso[a.grau_importancia || 'Média'] || 0
    const pesoB = prioridadePeso[b.grau_importancia || 'Média'] || 0
    
    if (pesoB !== pesoA) return pesoB - pesoA // Ordena por prioridade primeiro
    
    // Se a prioridade for igual, ordena pela data mais próxima
    const dataA = a.due_date ? new Date(a.due_date).getTime() : 0
    const dataB = b.due_date ? new Date(b.due_date).getTime() : 0
    return dataA - dataB
  }).slice(0, 3)
})

// ==========================================
// 4. LÓGICA DO CALENDÁRIO TIPADO
// ==========================================
const currentMonth = computed(() => currentDate.value.toLocaleDateString('pt-BR', { month: 'long' }))
const currentYear = computed(() => currentDate.value.getFullYear())

const calendarDays = computed<CalendarDay[]>(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()

  const firstDayOfMonth = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()

  // Tipagem aplicada: days é estritamente um array de CalendarDay
  let days: CalendarDay[] = []

  for (let i = 0; i < firstDayOfMonth; i++) {
    days.push({ date: null, tasks: [] })
  }

  for (let day = 1; day <= daysInMonth; day++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
    
    // O Vue agora entende que dayTasks é TaskData[]
    const dayTasks = tasks.value.filter((t) => (t.due_date || t.date) === dateStr)
    
    days.push({ date: day, tasks: dayTasks })
  }

  return days
})

const prevMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1, 1)
}
const nextMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 1)
}

// ==========================================
// 5. CHAMADAS À API
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

// ==========================================
// 6. HELPERS FORMATAÇÃO
// ==========================================
const getStatusColor = (status: string) => {
  if (status === 'concluida') return 'bg-[#19341a]' 
  if (status === 'em_andamento') return 'bg-[#ff8a65]' 
  if (status === 'aguardando_cliente') return 'bg-yellow-400'
  return 'bg-gray-400'
}

const formatDate = (dateString?: string) => {
  if (!dateString) return '-'
  const [year, month, day] = dateString.split('-')
  return `${day}/${month}`
}

const isToday = (day: number) => {
  const today = new Date()
  return (
    day === today.getDate() &&
    currentDate.value.getMonth() === today.getMonth() &&
    currentDate.value.getFullYear() === today.getFullYear()
  )
}

onMounted(() => fetchData())
</script>

<template>
  <Layout title="Dashboard">
    <div class="mb-8">
      <h1 class="text-3xl font-extrabold text-[#19341a]">Visão Geral</h1>
      <p class="text-[#2a2a2a]/60 text-sm mt-1">Acompanhe as métricas e o calendário do seu escritório.</p>
    </div>

    <div v-if="isLoading" class="text-center text-[#2a2a2a]/50 py-10">Carregando métricas...</div>

    <div v-else>
      <!-- Linha de Cards (4 Colunas) com "Urgentes" -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        <!-- Clientes -->
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200/80 flex items-center gap-5 transition-all hover:shadow-md hover:-translate-y-1">
          <div class="h-14 w-14 rounded-xl bg-[#eaf3ea] flex items-center justify-center flex-shrink-0">
            <svg class="w-7 h-7 text-[#19341a]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
          </div>
          <div>
            <p class="text-sm font-medium text-[#2a2a2a]/60">Total de Clientes</p>
            <p class="text-3xl font-extrabold text-[#19341a]">{{ dashData.total_clientes }}</p>
          </div>
        </div>

        <!-- Abertas -->
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200/80 flex items-center gap-5 transition-all hover:shadow-md hover:-translate-y-1">
          <div class="h-14 w-14 rounded-xl bg-[#fff3e0] flex items-center justify-center flex-shrink-0">
            <svg class="w-7 h-7 text-[#ff8a65]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          </div>
          <div>
            <p class="text-sm font-medium text-[#2a2a2a]/60">Tarefas Abertas</p>
            <p class="text-3xl font-extrabold text-[#19341a]">{{ dashData.tarefas_abertas }}</p>
          </div>
        </div>

        <!-- Urgentes -->
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200/80 flex items-center gap-5 transition-all hover:shadow-md hover:-translate-y-1">
          <div class="h-14 w-14 rounded-xl bg-yellow-50 flex items-center justify-center flex-shrink-0">
            <svg class="w-7 h-7 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
          </div>
          <div>
            <p class="text-sm font-medium text-[#2a2a2a]/60">Urgentes</p>
            <p class="text-3xl font-extrabold text-yellow-600">{{ countUrgentes }}</p>
          </div>
        </div>

        <!-- Atrasadas -->
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200/80 flex items-center gap-5 transition-all hover:shadow-md hover:-translate-y-1">
          <div class="h-14 w-14 rounded-xl bg-red-50 flex items-center justify-center flex-shrink-0">
             <svg class="w-7 h-7 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          </div>
          <div>
            <p class="text-sm font-medium text-[#2a2a2a]/60">Atrasadas</p>
            <p class="text-3xl font-extrabold text-red-500">{{ dashData.tarefas_atrasadas }}</p>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-1 space-y-6">
          
          <!-- Saúde dos Prazos com "Concluídas" -->
          <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200/80">
            <h3 class="text-lg font-bold text-[#19341a] mb-6">Saúde dos Prazos</h3>
            <div v-if="totalStatus === 0" class="text-center text-[#2a2a2a]/40 py-8">
              Nenhuma tarefa cadastrada.
            </div>
            <div v-else class="space-y-6">
              <div>
                <div class="flex justify-between mb-1">
                  <span class="text-sm font-medium text-[#2a2a2a]/70">Distribuição Global</span>
                  <span class="text-sm font-medium text-[#2a2a2a]/50">{{ totalStatus }} total</span>
                </div>
                <!-- Barra de Progresso Tripla -->
                <div class="w-full bg-gray-100 rounded-full h-4 flex overflow-hidden">
                  <div :style="{ width: percConcluidas + '%' }" class="bg-[#19341a] h-4 transition-all duration-500" title="Concluídas"></div>
                  <div :style="{ width: percNoPrazo + '%' }" class="bg-[#8ecba0] h-4 transition-all duration-500" title="No Prazo"></div>
                  <div :style="{ width: percAtrasadas + '%' }" class="bg-red-500 h-4 transition-all duration-500" title="Atrasadas"></div>
                </div>
              </div>
              <div class="grid grid-cols-3 gap-2">
                <div class="flex flex-col items-center bg-[#eaf3ea] p-2 rounded-lg">
                  <p class="text-[10px] uppercase font-bold text-[#19341a]/60">Concluídas</p>
                  <p class="text-lg font-extrabold text-[#19341a]">{{ countConcluidas }}</p>
                </div>
                <div class="flex flex-col items-center bg-gray-50 p-2 rounded-lg">
                  <p class="text-[10px] uppercase font-bold text-gray-500">Pendente</p>
                  <p class="text-lg font-extrabold text-gray-700">{{ tarefasNoPrazo }}</p>
                </div>
                <div class="flex flex-col items-center bg-red-50 p-2 rounded-lg">
                  <p class="text-[10px] uppercase font-bold text-red-500">Atrasadas</p>
                  <p class="text-lg font-extrabold text-red-600">{{ dashData.tarefas_atrasadas }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Foco do Dia (Lista de Tarefas Críticas) -->
          <div class="bg-gradient-to-br from-[#19341a] to-[#2a4830] p-6 rounded-2xl shadow-sm text-white flex flex-col min-h-[220px]">
            <h3 class="text-lg font-bold mb-1">Foco do Dia</h3>
            
            <div v-if="focoDoDiaTasks.length > 0" class="flex-1 mt-4 space-y-3">
              <RouterLink 
                to="/obrigacoes" 
                v-for="task in focoDoDiaTasks" 
                :key="task.id"
                class="block bg-white/10 p-3 rounded-xl border border-white/20 hover:bg-white/20 transition-all group"
              >
                <div class="flex justify-between items-start mb-1 gap-2">
                  <span class="font-bold text-sm leading-tight group-hover:text-[#ff8a65] transition-colors">{{ task.title }}</span>
                  <span v-if="task.grau_importancia === 'Urgente'" class="text-[9px] bg-red-500 text-white px-1.5 py-0.5 rounded uppercase font-bold tracking-wider">Urgente</span>
                  <span v-else-if="task.grau_importancia === 'Alta'" class="text-[9px] bg-orange-500 text-white px-1.5 py-0.5 rounded uppercase font-bold tracking-wider">Alta</span>
                </div>
                <div class="text-white/60 text-xs flex justify-between items-center mt-2">
                  <span>Prazo: {{ formatDate(task.due_date) }}</span>
                  <span>Ver Detalhes →</span>
                </div>
              </RouterLink>
            </div>
            
            <div v-else class="flex-1 flex flex-col items-center justify-center text-center mt-6">
              <div class="w-12 h-12 bg-white/10 rounded-full flex items-center justify-center mb-3">🎉</div>
              <p class="text-white/80 text-sm">Tudo sob controle! Nenhuma pendência urgente no momento.</p>
            </div>
          </div>
        </div>

        <div class="lg:col-span-2 bg-white p-6 rounded-2xl shadow-sm border border-gray-200/80">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg font-bold text-[#19341a]">Calendário de Prazos</h3>
            <div class="flex items-center gap-4">
              <button @click="prevMonth" class="p-2 rounded-lg hover:bg-[#eaf3ea] transition-colors text-[#2a2a2a]/60 hover:text-[#19341a]">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
              </button>
              <span class="text-md font-bold text-[#19341a] capitalize w-40 text-center">{{ currentMonth }} {{ currentYear }}</span>
              <button @click="nextMonth" class="p-2 rounded-lg hover:bg-[#eaf3ea] transition-colors text-[#2a2a2a]/60 hover:text-[#19341a]">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
              </button>
            </div>
          </div>

          <div class="grid grid-cols-7 gap-1 mb-1">
            <div class="text-center text-xs font-semibold text-[#2a2a2a]/40 py-2">Dom</div>
            <div class="text-center text-xs font-semibold text-[#2a2a2a]/40 py-2">Seg</div>
            <div class="text-center text-xs font-semibold text-[#2a2a2a]/40 py-2">Ter</div>
            <div class="text-center text-xs font-semibold text-[#2a2a2a]/40 py-2">Qua</div>
            <div class="text-center text-xs font-semibold text-[#2a2a2a]/40 py-2">Qui</div>
            <div class="text-center text-xs font-semibold text-[#2a2a2a]/40 py-2">Sex</div>
            <div class="text-center text-xs font-semibold text-[#2a2a2a]/40 py-2">Sáb</div>
          </div>

          <div class="grid grid-cols-7 gap-1">
            <div
              v-for="(day, index) in calendarDays"
              :key="index"
              class="min-h-[80px] md:min-h-[100px] border border-gray-100 rounded-lg p-1 md:p-2 transition-colors flex flex-col"
              :class="day.date ? 'bg-white hover:bg-gray-50/50' : 'bg-gray-50/30'"
            >
              <template v-if="day.date">
                <div class="text-right mb-1">
                  <span
                    class="text-xs md:text-sm font-medium"
                    :class="isToday(day.date) ? 'bg-[#ff8a65] text-white w-6 h-6 md:w-7 md:h-7 rounded-full inline-flex items-center justify-center shadow-sm' : 'text-[#2a2a2a]/70'"
                  >{{ day.date }}</span>
                </div>

                <!-- Limite de tarefas no calendário para não quebrar a tela -->
                <div class="space-y-1 mt-1 flex-1 overflow-hidden">
                  <template v-for="(task, tIndex) in day.tasks" :key="task.id">
                    <!-- Mostra no máximo 2 tarefas por dia -->
                    <div v-if="tIndex < 2"
                      class="flex items-center gap-1 group cursor-pointer rounded px-1 -mx-1 transition-colors"
                      :class="task.type === 'receita_federal' ? 'bg-[#fff3e0] hover:bg-[#ffe0b2]' : 'hover:bg-gray-100'"
                      :title="task.description || task.title"
                    >
                      <template v-if="task.type === 'receita_federal'">
                        <span class="text-[10px] flex-shrink-0">🏛️</span>
                        <span class="text-[10px] md:text-xs text-[#e65100] truncate group-hover:text-[#bf360c] font-bold">{{ task.title }}</span>
                      </template>
                      <template v-else>
                        <div class="w-1.5 h-1.5 rounded-full flex-shrink-0" :class="getStatusColor(task.status)"></div>
                        <span class="text-[10px] md:text-xs text-[#2a2a2a]/60 truncate group-hover:text-[#19341a] transition-colors font-medium">{{ task.title }}</span>
                      </template>
                    </div>
                  </template>
                  
                  <!-- Etiqueta resumida se houver mais de 2 tarefas -->
                  <div v-if="day.tasks.length > 2" class="mt-1 text-[10px] font-bold text-center text-gray-500 bg-gray-100 rounded border border-gray-200 py-0.5">
                    + {{ day.tasks.length - 2 }} tarefas
                  </div>
                </div>
              </template>
            </div>
          </div>

          <div class="mt-4 flex items-center gap-6 border-t border-gray-100 pt-4">
            <div class="flex items-center gap-2"><span class="text-xs">🏛️</span><span class="text-xs text-[#2a2a2a]/50 font-medium">Federal</span></div>
            <div class="flex items-center gap-2"><div class="w-2 h-2 rounded-full bg-[#19341a]"></div><span class="text-xs text-[#2a2a2a]/50 font-medium">Concluída</span></div>
            <div class="flex items-center gap-2"><div class="w-2 h-2 rounded-full bg-[#ff8a65]"></div><span class="text-xs text-[#2a2a2a]/50 font-medium">Em Andamento</span></div>
            <div class="flex items-center gap-2"><div class="w-2 h-2 rounded-full bg-red-500"></div><span class="text-xs text-[#2a2a2a]/50 font-medium">Atrasada</span></div>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>