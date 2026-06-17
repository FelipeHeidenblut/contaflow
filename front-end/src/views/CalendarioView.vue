<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'
import Layout from '../components/Layout.vue'
import { toast } from 'vue3-toastify'

// Tipagens (Copiadas do Dashboard)
interface TaskData {
  id: string | number
  title: string
  description?: string
  status: string
  due_date?: string
  date?: string
  type: 'task' | 'receita_federal'
}

interface CalendarDay {
  date: number | null
  tasks: TaskData[]
}

const isLoading = ref(true)
const tasks = ref<TaskData[]>([])
const currentDate = ref(new Date())

// Próximos meses
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
  if (status === 'concluida') return 'bg-[#19341a]' 
  if (status === 'em_andamento') return 'bg-[#ff8a65]' 
  if (status === 'aguardando_cliente') return 'bg-yellow-400'
  return 'bg-gray-400'
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

        <!-- Grid do Calendário (Mais espaçado e bonito) -->
        <div class="grid grid-cols-7 gap-2">
          <div
            v-for="(day, index) in calendarDays"
            :key="index"
            class="min-h-[110px] border rounded-xl p-2 transition-colors flex flex-col"
            :class="day.date ? 'bg-white border-gray-100 hover:border-[#ff8a65]/40 hover:shadow-sm' : 'bg-gray-50/30 border-transparent'"
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
                    :class="task.type === 'receita_federal' ? 'bg-[#fff3e0] hover:bg-[#ffe0b2]' : 'bg-gray-50 hover:bg-gray-100'"
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
                
                <div v-if="day.tasks.length > 3" class="mt-1 text-[10px] font-bold text-center text-gray-500 bg-gray-100 rounded-md py-0.5">
                  + {{ day.tasks.length - 3 }} tarefas
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
  </Layout>
</template>