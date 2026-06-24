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
  assigned_to?: string | number | null // Adicionado
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
})

const tasks = ref<TaskData[]>([])
const membros = ref<Membro[]>([]) // NOVO: Para a distribuição de equipe

// ==========================================
// 3. MÁGICA DOS DADOS (COMPUTED PROPERTIES)
// ==========================================
const officeTasks = computed(() => tasks.value.filter(t => t.type === 'task'))

const countUrgentes = computed(() => 
  officeTasks.value.filter(t => t.grau_importancia === 'Urgente' && t.status !== 'concluida').length
)
const countConcluidas = computed(() => 
  officeTasks.value.filter(t => t.status === 'concluida').length
)
const countAguardandoCliente = computed(() => 
  officeTasks.value.filter(t => t.status === 'aguardando_cliente').length
)

const totalStatus = computed(() => dashData.value.tarefas_abertas + countConcluidas.value)

const percConcluidas = computed(() => totalStatus.value > 0 ? (countConcluidas.value / totalStatus.value) * 100 : 0)
const percAtrasadas = computed(() => totalStatus.value > 0 ? (dashData.value.tarefas_atrasadas / totalStatus.value) * 100 : 0)
const percNoPrazo = computed(() => totalStatus.value > 0 ? ((dashData.value.tarefas_abertas - dashData.value.tarefas_atrasadas) / totalStatus.value) * 100 : 0)

const tarefasNoPrazo = computed(() => dashData.value.tarefas_abertas - dashData.value.tarefas_atrasadas)

// ==========================================
// 4. DISTRIBUIÇÃO DA EQUIPE (NOVO)
// ==========================================
const cargaEquipe = computed(() => {
  const tarefasAtribuidas = officeTasks.value.filter(t => t.status !== 'concluida' && t.assigned_to)
  
  // Inicializa todos os membros com 0 tarefas
  const carga: Record<string, { nome: string, count: number }> = {}
  membros.value.forEach(m => {
    carga[String(m.id)] = { nome: m.name, count: 0 }
  })
  
  // Conta as tarefas de cada um
  tarefasAtribuidas.forEach(t => {
    const id = String(t.assigned_to)
    if (carga[id]) {
      carga[id].count++
    }
  })
  
  // Retorna como array ordenado por quem tem mais tarefas
  return Object.values(carga).sort((a, b) => b.count - a.count)
})

// ==========================================
// 5. FOCO DO DIA E PRÓXIMOS PRAZOS
// ==========================================
const focoDoDiaTasks = computed(() => {
  const today = new Date();
  const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
  
  const abertas = officeTasks.value.filter(t => 
    t.status !== 'concluida' && t.due_date && t.due_date <= todayStr
  );
  
  const prioridadePeso: Record<string, number> = { 'Urgente': 4, 'Alta': 3, 'Média': 2, 'Baixa': 1 }
  
  return abertas.sort((a, b) => {
    const pesoA = prioridadePeso[a.grau_importancia || 'Média'] || 0
    const pesoB = prioridadePeso[b.grau_importancia || 'Média'] || 0
    if (pesoB !== pesoA) return pesoB - pesoA
    const dataA = a.due_date ? new Date(a.due_date).getTime() : 0
    const dataB = b.due_date ? new Date(b.due_date).getTime() : 0
    return dataA - dataB
  }).slice(0, 3)
})

const proximosPrazos = computed(() => {
  const today = new Date();
  const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
  
  const nextWeek = new Date(today);
  nextWeek.setDate(today.getDate() + 7);
  const nextWeekStr = `${nextWeek.getFullYear()}-${String(nextWeek.getMonth() + 1).padStart(2, '0')}-${String(nextWeek.getDate()).padStart(2, '0')}`;

  return tasks.value
    .filter(t => {
      const date = t.due_date || t.date;
      return date && date > todayStr && date <= nextWeekStr;
    })
    .sort((a, b) => (a.due_date || a.date || '').localeCompare(b.due_date || b.date || ''))
    .slice(0, 6);
});

// ==========================================
// 6. CHAMADAS À API E NAVEGAÇÃO
// ==========================================
const fetchData = async () => {
  isLoading.value = true
  try {
    // Busca membros também
    const [dashRes, tasksRes, membrosRes] = await Promise.all([
      api.get('/api/v1/dashboard'),
      api.get('/api/v1/obrigacoes'),
      api.get('/api/v1/membros')
    ])

    dashData.value = dashRes.data
    membros.value = membrosRes.data
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

const goToClients = () => router.push('/clientes')
const goToTasks = () => router.push('/obrigacoes')

// ==========================================
// 7. HELPERS FORMATAÇÃO
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

// Helper para as iniciais dos membros
const getIniciaisMembro = (nome: string) => {
  if (!nome) return '?'
  const partes = nome.trim().split(' ').filter(p => p)
  if (partes.length === 0) return '?'
  if (partes.length === 1) return (partes[0]?.charAt(0) || '?').toUpperCase()
  const primeiraLetra = partes[0]?.charAt(0) || ''
  const ultimaLetra = partes[partes.length - 1]?.charAt(0) || ''
  return (primeiraLetra + ultimaLetra).toUpperCase() || '?'
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
      <!-- Linha de Cards Clicáveis -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        <div @click="goToClients" class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200/80 flex items-center gap-5 transition-all hover:shadow-md hover:-translate-y-1 cursor-pointer">
          <div class="h-14 w-14 rounded-xl bg-[#eaf3ea] flex items-center justify-center flex-shrink-0">
            <svg class="w-7 h-7 text-[#19341a]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
          </div>
          <div>
            <p class="text-sm font-medium text-[#2a2a2a]/60">Total de Clientes</p>
            <p class="text-3xl font-extrabold text-[#19341a]">{{ dashData.total_clientes }}</p>
          </div>
        </div>

        <div @click="goToTasks" class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200/80 flex items-center gap-5 transition-all hover:shadow-md hover:-translate-y-1 cursor-pointer">
          <div class="h-14 w-14 rounded-xl bg-[#fff3e0] flex items-center justify-center flex-shrink-0">
            <svg class="w-7 h-7 text-[#ff8a65]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          </div>
          <div>
            <p class="text-sm font-medium text-[#2a2a2a]/60">Tarefas Abertas</p>
            <p class="text-3xl font-extrabold text-[#19341a]">{{ dashData.tarefas_abertas }}</p>
          </div>
        </div>

        <div @click="goToTasks" class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200/80 flex items-center gap-5 transition-all hover:shadow-md hover:-translate-y-1 cursor-pointer">
          <div class="h-14 w-14 rounded-xl bg-yellow-50 flex items-center justify-center flex-shrink-0">
            <svg class="w-7 h-7 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
          </div>
          <div>
            <p class="text-sm font-medium text-[#2a2a2a]/60">Urgentes</p>
            <p class="text-3xl font-extrabold text-yellow-600">{{ countUrgentes }}</p>
          </div>
        </div>

        <div @click="goToTasks" class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200/80 flex items-center gap-5 transition-all hover:shadow-md hover:-translate-y-1 cursor-pointer">
          <div class="h-14 w-14 rounded-xl bg-red-50 flex items-center justify-center flex-shrink-0">
             <svg class="w-7 h-7 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          </div>
          <div>
            <p class="text-sm font-medium text-[#2a2a2a]/60">Atrasadas</p>
            <p class="text-3xl font-extrabold text-red-500">{{ dashData.tarefas_atrasadas }}</p>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div class="lg:col-span-1 space-y-6">
          
          <!-- Saúde dos Prazos -->
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
                <div class="w-full bg-gray-100 rounded-full h-4 flex overflow-hidden">
                  <div :style="{ width: percConcluidas + '%' }" class="bg-[#19341a] h-4 transition-all duration-500" title="Concluídas"></div>
                  <div :style="{ width: percNoPrazo + '%' }" class="bg-[#8ecba0] h-4 transition-all duration-500" title="No Prazo"></div>
                  <div :style="{ width: percAtrasadas + '%' }" class="bg-red-500 h-4 transition-all duration-500" title="Atrasadas"></div>
                </div>
              </div>
              <div class="grid grid-cols-2 gap-2">
                <div class="flex flex-col items-center bg-[#eaf3ea] p-2 rounded-lg">
                  <p class="text-[10px] uppercase font-bold text-[#19341a]/60">Concluídas</p>
                  <p class="text-lg font-extrabold text-[#19341a]">{{ countConcluidas }}</p>
                </div>
                <div class="flex flex-col items-center bg-gray-50 p-2 rounded-lg">
                  <p class="text-[10px] uppercase font-bold text-gray-500">Pendentes</p>
                  <p class="text-lg font-extrabold text-gray-700">{{ tarefasNoPrazo }}</p>
                </div>
                <div class="flex flex-col items-center bg-yellow-50 p-2 rounded-lg border border-yellow-100">
                  <p class="text-[10px] uppercase font-bold text-yellow-600">Aguard. Cliente</p>
                  <p class="text-lg font-extrabold text-yellow-700">{{ countAguardandoCliente }}</p>
                </div>
                <div class="flex flex-col items-center bg-red-50 p-2 rounded-lg">
                  <p class="text-[10px] uppercase font-bold text-red-500">Atrasadas</p>
                  <p class="text-lg font-extrabold text-red-600">{{ dashData.tarefas_atrasadas }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Foco do Dia -->
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
                  <div class="flex flex-col items-end gap-1">
                    <span v-if="task.status === 'aguardando_cliente'" class="text-[9px] bg-yellow-500 text-black px-1.5 py-0.5 rounded uppercase font-bold tracking-wider">Aguardando</span>
                    <span v-else-if="task.grau_importancia === 'Urgente'" class="text-[9px] bg-red-500 text-white px-1.5 py-0.5 rounded uppercase font-bold tracking-wider">Urgente</span>
                    <span v-else-if="task.grau_importancia === 'Alta'" class="text-[9px] bg-orange-500 text-white px-1.5 py-0.5 rounded uppercase font-bold tracking-wider">Alta</span>
                  </div>
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

        <!-- Próximos 7 Dias -->
        <div class="lg:col-span-2 bg-white p-6 rounded-2xl shadow-sm border border-gray-200/80">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg font-bold text-[#19341a]">Próximos 7 Dias</h3>
            <RouterLink to="/calendario" class="text-sm font-bold text-[#ff8a65] hover:text-[#f07047] transition-colors">
              Ver Calendário Completo →
            </RouterLink>
          </div>

          <div class="space-y-3">
            <div v-for="task in proximosPrazos" :key="task.id" class="flex items-center justify-between p-3 rounded-xl hover:bg-gray-50 border border-gray-100 transition-colors">
              <div class="flex items-center gap-3">
                <div class="w-2.5 h-2.5 rounded-full flex-shrink-0" :class="getStatusColor(task.status)"></div>
                <div>
                  <p class="text-sm font-semibold text-[#19341a]">{{ task.title }}</p>
                  <p class="text-xs text-gray-400">{{ task.type === 'receita_federal' ? 'Prazo Federal' : 'Tarefa Interna' }}</p>
                </div>
              </div>
              <div class="text-right">
                <p class="text-sm font-bold text-[#2a2a2a]/80">{{ formatDate(task.due_date || task.date) }}</p>
                <p class="text-[10px] uppercase font-bold text-gray-400">{{ getDayName(task.due_date || task.date) }}</p>
              </div>
            </div>
            <div v-if="proximosPrazos.length === 0" class="text-center py-8 text-gray-400 text-sm">
              Nenhum prazo para os próximos 7 dias. Você está em dia! 🎉
            </div>
          </div>
        </div>
      </div>

      <!-- NOVA LINHA: DISTRIBUIÇÃO DA EQUIPE -->
      <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200/80">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-bold text-[#19341a]">Distribuição da Equipe</h3>
          <span class="text-xs text-gray-400 font-medium">Tarefas em aberto por membro</span>
        </div>

        <div v-if="cargaEquipe.length === 0" class="text-center py-8 text-gray-400 text-sm">
          Nenhum membro cadastrado ou sem tarefas atribuídas.
        </div>

        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div v-for="membro in cargaEquipe" :key="membro.nome" class="border border-gray-100 rounded-xl p-4 flex items-center gap-3 hover:border-[#ff8a65]/40 transition-colors">
            <div class="w-10 h-10 rounded-full bg-[#19341a]/10 text-[#19341a] flex items-center justify-center font-bold flex-shrink-0">
              {{ getIniciaisMembro(membro.nome) }}
            </div>
            <div class="min-w-0">
              <p class="text-sm font-bold text-[#19341a] truncate">{{ membro.nome }}</p>
              <p class="text-xs font-medium" :class="membro.count > 5 ? 'text-orange-500' : 'text-gray-500'">
                {{ membro.count }} {{ membro.count === 1 ? 'tarefa em aberto' : 'tarefas em aberto' }}
              </p>
            </div>
          </div>
        </div>
      </div>

    </div>
  </Layout>
</template>