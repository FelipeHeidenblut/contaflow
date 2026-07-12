<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import api from '../services/api'
import Layout from '../components/Layout.vue'
import { toast } from 'vue3-toastify'

// ==========================================
// 1. TIPAGENS
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
}

interface CalendarDay {
  date: number | null
  tasks: TaskData[]
}

// ==========================================
// 2. ESTADOS
// ==========================================
const isLoading = ref(true)
const tasks = ref<TaskData[]>([])
const currentDate = ref(new Date())

// Controle do Modal do Dia
const isDayModalOpen = ref(false)
const selectedDayTasks = ref<TaskData[]>([])
const selectedDayTitle = ref('')

// ==========================================
// 3. SINCRONIZAÇÃO ICS (.ics)
// ==========================================
// Pega a URL base do backend do arquivo .env (ou usa localhost se não tiver)
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://api.contablytask.com.br'

const icsUrl = ref('')
const copied = ref(false)

const carregarIcsUrl = async () => {
  try {
    // Busca o tenant_id do usuário logado no backend
    const res = await api.get('/api/v1/auth/me')
    if (res.data.tenant_id) {
      icsUrl.value = `${API_BASE_URL}/api/v1/calendario/feed/${res.data.tenant_id}.ics`
    } else {
      console.warn("Backend não retornou tenant_id na rota /me")
    }
  } catch (error) {
    console.error("Erro ao buscar tenant_id para o link ICS:", error)
  }
}

const copyLink = async () => {
  try {
    await navigator.clipboard.writeText(icsUrl.value)
    copied.value = true
    toast.success('Link copiado! Cole no Google Agenda ou Outlook.')
    setTimeout(() => copied.value = false, 3000)
  } catch (error) {
    toast.error('Não foi possível copiar o link.')
  }
}

// ==========================================
// 4. LÓGICA DO CALENDÁRIO
// ==========================================
const currentMonth = computed(() => currentDate.value.toLocaleDateString('pt-BR', { month: 'long' }))
const currentYear = computed(() => currentDate.value.getFullYear())

const calendarDays = computed<CalendarDay[]>(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  const firstDayOfMonth = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  let days: CalendarDay[] = []

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

const prevMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1, 1)
}
const nextMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 1)
}

// ==========================================
// 5. MODAL DO DIA (NOVO)
// ==========================================
const openDayModal = (day: CalendarDay) => {
  // Só abre se o dia tiver tarefas
  if (day.date && day.tasks.length > 0) {
    const dateObj = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth(), day.date)
    selectedDayTitle.value = dateObj.toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric', month: 'long' })
    selectedDayTasks.value = day.tasks
    isDayModalOpen.value = true
  }
}

// ==========================================
// 6. CHAMADAS À API
// ==========================================
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

// ==========================================
// 7. HELPERS VISUAIS
// ==========================================
const getStatusColor = (status: string) => {
  if (status === 'concluida') return 'bg-[#19341a]'
  if (status === 'em_andamento') return 'bg-[#ff8a65]'
  if (status === 'aguardando_cliente') return 'bg-yellow-400'
  return 'bg-gray-400'
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    'concluida': 'Concluída',
    'em_andamento': 'Em Andamento',
    'aguardando_cliente': 'Aguardando Cliente',
    'pendente': 'Pendente'
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
    <div class="bg-white rounded-2xl shadow-sm border border-gray-200/80 p-6 md:p-8">

      <!-- Cabeçalho do Calendário -->
      <div class="flex items-center justify-between mb-8">
        <h2 class="text-2xl font-extrabold text-[#19341a] capitalize tracking-tight">
          {{ currentMonth }} <span class="text-gray-300 font-light">{{ currentYear }}</span>
        </h2>
        <div class="flex items-center gap-2">
          <button @click="prevMonth" class="p-2.5 rounded-lg hover:bg-[#eaf3ea] transition-colors text-[#2a2a2a]/60 hover:text-[#19341a] border border-gray-100">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
          </button>
          <button @click="nextMonth" class="p-2.5 rounded-lg hover:bg-[#eaf3ea] transition-colors text-[#2a2a2a]/60 hover:text-[#19341a] border border-gray-100">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
          </button>
        </div>
      </div>

      <!-- CARTÃO DE SINCRONIZAÇÃO (.ICS) -->
      <div v-if="icsUrl" class="mb-8 p-5 bg-[#eaf3ea] border border-[#19341a]/10 rounded-2xl flex flex-col md:flex-row items-center justify-between gap-4">
        <div class="flex items-center gap-3 text-center md:text-left">
          <div class="h-10 w-10 rounded-xl bg-white flex items-center justify-center text-[#19341a] flex-shrink-0">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
          </div>
          <div>
            <p class="font-bold text-[#19341a]">Sincronizar com minha agenda</p>
            <p class="text-sm text-gray-500">Adicione este link no Google Agenda ou Outlook para ver seus prazos no celular.</p>
          </div>
        </div>
        <div class="flex gap-2 items-center w-full md:w-auto">
          <input type="text" readonly :value="icsUrl" class="flex-1 md:w-64 px-3 py-2 border border-gray-200 rounded-lg text-xs bg-white text-gray-500 outline-none" />
          <button @click="copyLink" class="bg-[#19341a] text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-[#0f2010] transition-colors whitespace-nowrap">
            {{ copied ? 'Copiado!' : 'Copiar Link' }}
          </button>
        </div>
      </div>

      <div v-if="isLoading" class="text-center text-gray-400 py-20">Carregando calendário...</div>

      <div v-else>
        <!-- Dias da Semana -->
        <div class="grid grid-cols-7 gap-2 mb-2">
          <div class="text-center text-xs font-bold text-gray-400 uppercase py-2">Dom</div>
          <div class="text-center text-xs font-bold text-gray-400 uppercase py-2">Seg</div>
          <div class="text-center text-xs font-bold text-gray-400 uppercase py-2">Ter</div>
          <div class="text-center text-xs font-bold text-gray-400 uppercase py-2">Qua</div>
          <div class="text-center text-xs font-bold text-gray-400 uppercase py-2">Qui</div>
          <div class="text-center text-xs font-bold text-gray-400 uppercase py-2">Sex</div>
          <div class="text-center text-xs font-bold text-gray-400 uppercase py-2">Sáb</div>
        </div>

        <!-- Grid do Calendário -->
        <div class="grid grid-cols-7 gap-2">
          <div
            v-for="(day, index) in calendarDays"
            :key="index"
            @click="openDayModal(day)"
            class="min-h-[110px] border rounded-xl p-2 transition-all flex flex-col"
            :class="[
              day.date ? 'bg-white border-gray-100 hover:border-[#ff8a65]/40 hover:shadow-sm' : 'bg-gray-50/30 border-transparent',
              day.tasks.length > 0 ? 'cursor-pointer hover:bg-[#f8f8f8]' : ''
            ]"
          >
            <template v-if="day.date">
              <div class="text-right mb-1">
                <span
                  class="text-xs font-bold inline-flex items-center justify-center"
                  :class="isToday(day.date) ? 'bg-[#ff8a65] text-white w-6 h-6 rounded-full shadow-sm' : 'text-gray-400'"
                >{{ day.date }}</span>
              </div>

              <div class="space-y-1 mt-1 flex-1 overflow-hidden">
                <template v-for="(task, tIndex) in day.tasks" :key="task.id">
                  <div v-if="tIndex < 3"
                    class="flex items-center gap-1.5 group cursor-pointer rounded-md px-1.5 py-1 transition-colors"
                    :class="task.type === 'receita_federal' ? 'bg-[#fff3e0]' : 'bg-gray-50'"
                    :title="task.description || task.title"
                  >
                    <template v-if="task.type === 'receita_federal'">
                      <span class="text-[10px]">🏛️</span>
                      <span class="text-[11px] text-[#e65100] truncate font-bold">{{ task.title }}</span>
                    </template>
                    <template v-else>
                      <div class="w-2 h-2 rounded-full flex-shrink-0" :class="getStatusColor(task.status)"></div>
                      <span class="text-[11px] text-[#2a2a2a]/70 truncate font-medium">{{ task.title }}</span>
                    </template>
                  </div>
                </template>

                <div v-if="day.tasks.length > 3" class="mt-1 text-[10px] font-bold text-center text-[#ff8a65] bg-[#fff3e0] rounded-md py-0.5 border border-[#ffe0b2]">
                  + {{ day.tasks.length - 3 }} tarefas (Clique para ver)
                </div>
              </div>
            </template>
          </div>
        </div>

        <!-- Legenda -->
        <div class="mt-8 flex flex-wrap items-center gap-x-6 gap-y-2 border-t border-gray-100 pt-6">
          <div class="flex items-center gap-2"><span class="text-sm">🏛️</span><span class="text-xs text-gray-500 font-medium">Prazo Federal</span></div>
          <div class="flex items-center gap-2"><div class="w-2.5 h-2.5 rounded-full bg-[#19341a]"></div><span class="text-xs text-gray-500 font-medium">Concluída</span></div>
          <div class="flex items-center gap-2"><div class="w-2.5 h-2.5 rounded-full bg-[#ff8a65]"></div><span class="text-xs text-gray-500 font-medium">Em Andamento</span></div>
          <div class="flex items-center gap-2"><div class="w-2.5 h-2.5 rounded-full bg-yellow-400"></div><span class="text-xs text-gray-500 font-medium">Aguardando Cliente</span></div>
        </div>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- MODAL DE DETALHES DO DIA (NOVO)            -->
    <!-- ========================================== -->
    <div v-if="isDayModalOpen" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50" @click="isDayModalOpen = false">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden" @click.stop>

        <!-- Cabeçalho do Modal -->
        <div class="bg-[#19341a] px-6 py-5 flex justify-between items-center">
          <div>
            <p class="text-white/50 text-xs font-bold uppercase tracking-wider">Prazos do Dia</p>
            <h3 class="text-xl font-bold text-white capitalize tracking-tight">{{ selectedDayTitle }}</h3>
          </div>
          <button @click="isDayModalOpen = false" class="text-white/50 hover:text-white text-2xl font-bold">&times;</button>
        </div>

        <!-- Lista de Tarefas do Dia -->
        <div class="p-6 space-y-3 max-h-[60vh] overflow-y-auto">
          <div v-for="task in selectedDayTasks" :key="task.id"
               class="flex items-start gap-3 p-4 rounded-xl border transition-colors"
               :class="task.type === 'receita_federal' ? 'bg-[#fff3e0] border-[#ffe0b2]' : 'bg-[#f8f8f8] border-gray-100'">

            <div class="flex-shrink-0 mt-1">
              <span v-if="task.type === 'receita_federal'" class="text-xl">🏛️</span>
              <div v-else class="w-3 h-3 rounded-full" :class="getStatusColor(task.status)"></div>
            </div>

            <div class="flex-1 min-w-0">
              <p class="text-sm font-bold text-[#19341a]">{{ task.title }}</p>
              <p v-if="task.description" class="text-xs text-gray-500 mt-1 truncate">{{ task.description }}</p>

              <div class="flex items-center gap-3 mt-2">
                <span v-if="task.type !== 'receita_federal'"
                      class="text-[10px] font-bold px-2 py-0.5 rounded-md"
                      :class="getStatusColor(task.status) + ' text-white'">
                  {{ getStatusLabel(task.status) }}
                </span>
                <span v-if="task.grau_importancia" class="text-[10px] font-bold text-gray-400 uppercase">
                  ⚡ {{ task.grau_importancia }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Rodapé do Modal -->
        <div class="px-6 py-4 bg-[#f8f8f8] border-t border-gray-100 flex justify-end">
          <RouterLink to="/obrigacoes" class="px-5 py-2.5 bg-[#ff8a65] text-white text-sm font-bold rounded-xl hover:bg-[#f07047] transition-colors">
            Gerenciar Tarefas →
          </RouterLink>
        </div>
      </div>
    </div>

  </Layout>
</template>
