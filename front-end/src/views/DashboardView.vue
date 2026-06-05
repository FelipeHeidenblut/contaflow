<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'
import Layout from '../components/Layout.vue'
import { toast } from 'vue3-toastify'

const isLoading = ref(true)

// Estado do Dashboard
const dashData = ref({
  total_clientes: 0,
  tarefas_abertas: 0,
  tarefas_atrasadas: 0,
})

// Estado do Calendário
const tasks = ref<any[]>([])
const currentDate = ref(new Date())

// Dados calculados para o Gráfico
const tarefasNoPrazo = computed(
  () => dashData.value.tarefas_abertas - dashData.value.tarefas_atrasadas,
)
const totalTarefas = computed(() => dashData.value.tarefas_abertas)
const percNoPrazo = computed(() =>
  totalTarefas.value > 0 ? (tarefasNoPrazo.value / totalTarefas.value) * 100 : 0,
)
const percAtrasadas = computed(() =>
  totalTarefas.value > 0 ? (dashData.value.tarefas_atrasadas / totalTarefas.value) * 100 : 0,
)

// Lógica do Calendário
const currentMonth = computed(() =>
  currentDate.value.toLocaleDateString('pt-BR', { month: 'long' }),
)
const currentYear = computed(() => currentDate.value.getFullYear())

const calendarDays = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()

  const firstDayOfMonth = new Date(year, month, 1).getDay() // 0=Domingo, 1=Segunda...
  const daysInMonth = new Date(year, month + 1, 0).getDate()

  let days: any[] = []

  // Preenche os dias vazios antes do dia 1
  for (let i = 0; i < firstDayOfMonth; i++) {
    days.push({ date: null, tasks: [] })
  }

  // Preenche os dias do mês
  for (let day = 1; day <= daysInMonth; day++) {
    // Formata a data para comparar com a que vem do banco (YYYY-MM-DD)
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`

    // Encontra as tarefas para este dia
    const dayTasks = tasks.value.filter((t) => t.due_date === dateStr)

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

// Busca dados do Dashboard e as Tarefas
const fetchData = async () => {
  isLoading.value = true
  try {
    const [dashRes, tasksRes] = await Promise.all([
      api.get('/api/v1/dashboard'),
      api.get('/api/v1/obrigacoes'),
    ])
    dashData.value = dashRes.data
    tasks.value = tasksRes.data
  } catch (error) {
    toast.error('Erro ao carregar os dados do dashboard.')
  } finally {
    isLoading.value = false
  }
}

// Helpers
const getStatusColor = (status: string) => {
  if (status === 'concluida') return 'bg-green-500'
  if (status === 'em_andamento') return 'bg-blue-500'
  if (status === 'aguardando_cliente') return 'bg-orange-500'
  return 'bg-yellow-400' // pendente
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
})
</script>

<template>
  <Layout title="Dashboard">
    <!-- Header de Boas-vindas -->
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900">Visão Geral</h1>
      <p class="text-gray-500 text-sm mt-1">
        Acompanhe as métricas e o calendário do seu escritório.
      </p>
    </div>

    <div v-if="isLoading" class="text-center text-gray-500 py-10">Carregando métricas...</div>

    <div v-else>
      <!-- Linha de Cards de Métricas -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        <div
          class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center gap-5 transition-all hover:shadow-md hover:-translate-y-1"
        >
          <div
            class="h-14 w-14 rounded-full bg-indigo-50 flex items-center justify-center flex-shrink-0"
          >
            <svg
              class="w-7 h-7 text-indigo-600"
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
          <div>
            <p class="text-sm font-medium text-gray-500">Total de Clientes</p>
            <p class="text-3xl font-bold text-gray-900">{{ dashData.total_clientes }}</p>
          </div>
        </div>

        <div
          class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center gap-5 transition-all hover:shadow-md hover:-translate-y-1"
        >
          <div
            class="h-14 w-14 rounded-full bg-yellow-50 flex items-center justify-center flex-shrink-0"
          >
            <svg
              class="w-7 h-7 text-yellow-500"
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
          <div>
            <p class="text-sm font-medium text-gray-500">Tarefas Abertas</p>
            <p class="text-3xl font-bold text-gray-900">{{ dashData.tarefas_abertas }}</p>
          </div>
        </div>

        <div
          class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center gap-5 transition-all hover:shadow-md hover:-translate-y-1"
        >
          <div
            class="h-14 w-14 rounded-full bg-red-50 flex items-center justify-center flex-shrink-0"
          >
            <svg class="w-7 h-7 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              ></path>
            </svg>
          </div>
          <div>
            <p class="text-sm font-medium text-gray-500">Atrasadas</p>
            <p class="text-3xl font-bold text-red-600">{{ dashData.tarefas_atrasadas }}</p>
          </div>
        </div>
      </div>

      <!-- Grid Principal: Gráfico + Calendário -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Coluna Esquerda: Gráfico e Motivacional -->
        <div class="lg:col-span-1 space-y-6">
          <!-- Gráfico de Prazos -->
          <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h3 class="text-lg font-semibold text-gray-800 mb-6">Saúde dos Prazos</h3>
            <div v-if="totalTarefas === 0" class="text-center text-gray-400 py-8">
              Nenhuma tarefa cadastrada ainda.
            </div>
            <div v-else class="space-y-6">
              <div>
                <div class="flex justify-between mb-1">
                  <span class="text-sm font-medium text-gray-700">Distribuição</span>
                  <span class="text-sm font-medium text-gray-500">{{ totalTarefas }} total</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-4 flex overflow-hidden">
                  <div
                    :style="{ width: percNoPrazo + '%' }"
                    class="bg-green-500 h-4 transition-all duration-500"
                  ></div>
                  <div
                    :style="{ width: percAtrasadas + '%' }"
                    class="bg-red-500 h-4 transition-all duration-500"
                  ></div>
                </div>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div class="flex items-center gap-3 bg-green-50 p-3 rounded-lg">
                  <div class="w-4 h-4 bg-green-500 rounded-sm flex-shrink-0"></div>
                  <div>
                    <p class="text-xs text-gray-500">No Prazo</p>
                    <p class="text-lg font-bold text-green-700">{{ tarefasNoPrazo }}</p>
                  </div>
                </div>
                <div class="flex items-center gap-3 bg-red-50 p-3 rounded-lg">
                  <div class="w-4 h-4 bg-red-500 rounded-sm flex-shrink-0"></div>
                  <div>
                    <p class="text-xs text-gray-500">Atrasadas</p>
                    <p class="text-lg font-bold text-red-700">{{ dashData.tarefas_atrasadas }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Card Motivacional -->
          <div
            class="bg-gradient-to-br from-indigo-600 to-indigo-800 p-6 rounded-xl shadow-sm text-white flex flex-col justify-between"
          >
            <div>
              <h3 class="text-lg font-semibold mb-2">Foco do Dia</h3>
              <p
                class="text-indigo-100 text-sm leading-relaxed"
                v-if="dashData.tarefas_atrasadas > 0"
              >
                Você tem
                <span class="font-bold text-white"
                  >{{ dashData.tarefas_atrasadas }} obrigações atrasadas</span
                >. Priorize a regularização para evitar multas.
              </p>
              <p
                class="text-indigo-100 text-sm leading-relaxed"
                v-else-if="dashData.tarefas_abertas > 0"
              >
                Nada atrasado! Você tem
                <span class="font-bold text-white">{{ dashData.tarefas_abertas }} em aberto</span>.
                Continue assim!
              </p>
              <p class="text-indigo-100 text-sm leading-relaxed" v-else>
                Dia limpo! Todos os prazos foram cumpridos.
              </p>
            </div>
            <div class="mt-6">
              <RouterLink
                to="/obrigacoes"
                class="inline-block bg-white text-indigo-700 font-semibold px-4 py-2 rounded-lg hover:bg-indigo-50 transition-colors text-sm"
              >
                Ver Obrigações →
              </RouterLink>
            </div>
          </div>
        </div>

        <!-- Coluna Direita: Calendário -->
        <div class="lg:col-span-2 bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg font-semibold text-gray-800">Calendário de Prazos</h3>
            <div class="flex items-center gap-4">
              <button
                @click="prevMonth"
                class="p-2 rounded-lg hover:bg-gray-100 transition-colors text-gray-600 hover:text-indigo-600"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 19l-7-7 7-7"
                  ></path>
                </svg>
              </button>
              <span class="text-md font-bold text-gray-800 capitalize w-40 text-center">
                {{ currentMonth }} {{ currentYear }}
              </span>
              <button
                @click="nextMonth"
                class="p-2 rounded-lg hover:bg-gray-100 transition-colors text-gray-600 hover:text-indigo-600"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 5l7 7-7 7"
                  ></path>
                </svg>
              </button>
            </div>
          </div>

          <!-- Cabeçalho Dias da Semana -->
          <div class="grid grid-cols-7 gap-1 mb-1">
            <div class="text-center text-xs font-semibold text-gray-500 py-2">Dom</div>
            <div class="text-center text-xs font-semibold text-gray-500 py-2">Seg</div>
            <div class="text-center text-xs font-semibold text-gray-500 py-2">Ter</div>
            <div class="text-center text-xs font-semibold text-gray-500 py-2">Qua</div>
            <div class="text-center text-xs font-semibold text-gray-500 py-2">Qui</div>
            <div class="text-center text-xs font-semibold text-gray-500 py-2">Sex</div>
            <div class="text-center text-xs font-semibold text-gray-500 py-2">Sáb</div>
          </div>

          <!-- Grid do Calendário -->
          <div class="grid grid-cols-7 gap-1">
            <div
              v-for="(day, index) in calendarDays"
              :key="index"
              class="min-h-[80px] md:min-h-[100px] border border-gray-100 rounded-md p-1 md:p-2 transition-colors"
              :class="day.date ? 'bg-white hover:bg-gray-50' : 'bg-gray-50/50'"
            >
              <template v-if="day.date">
                <!-- Número do Dia -->
                <div class="text-right mb-1">
                  <span
                    class="text-xs md:text-sm font-medium"
                    :class="
                      isToday(day.date)
                        ? 'bg-indigo-600 text-white w-6 h-6 md:w-7 md:h-7 rounded-full inline-flex items-center justify-center'
                        : 'text-gray-700'
                    "
                  >
                    {{ day.date }}
                  </span>
                </div>

                <!-- Tarefas do Dia -->
                <div class="space-y-1">
                  <div
                    v-for="task in day.tasks"
                    :key="task.id"
                    class="flex items-center gap-1 group cursor-pointer"
                    :title="task.title"
                  >
                    <div
                      class="w-1.5 h-1.5 rounded-full flex-shrink-0"
                      :class="getStatusColor(task.status)"
                    ></div>
                    <span
                      class="text-[10px] md:text-xs text-gray-600 truncate group-hover:text-indigo-600 transition-colors font-medium"
                    >
                      {{ task.title }}
                    </span>
                  </div>
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>
