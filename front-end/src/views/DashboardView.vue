<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { toast } from 'vue3-toastify'
import Layout from '../components/Layout.vue'
import OperationalDashboard from '../components/OperationalDashboard.vue'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'
import { fetchAllPages } from '../services/pagination'

interface TaskData {
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

interface Member {
  id: string | number
  name: string
}

interface Client {
  id: string | number
  razao_social?: string
  nome?: string
}

const authStore = useAuthStore()
const isLoading = ref(true)
const loadError = ref(false)
const lookupsReady = ref(false)
const tasks = ref<TaskData[]>([])
const members = ref<Member[]>([])
const clients = ref<Client[]>([])
const dashboard = ref({
  total_clientes: 0,
  tarefas_abertas: 0,
  tarefas_atrasadas: 0,
  plano: '',
  status_pagamento: '',
})

const planLabel = computed(() => {
  if (dashboard.value.status_pagamento === 'aguardando_pagamento') return 'Pagamento pendente'
  if (dashboard.value.status_pagamento === 'inadimplente') return 'Conta bloqueada'
  if (dashboard.value.status_pagamento === 'estornado') return 'Pagamento estornado'
  if (dashboard.value.status_pagamento === 'cancelado') return 'Assinatura cancelada'
  if (dashboard.value.status_pagamento === 'chargeback') return 'Pagamento em contestação'
  const labels: Record<string, string> = {
    free: 'Gratuito',
    basico: 'Essencial',
    profissional: 'Profissional',
    escritorio: 'Escritório',
    business: 'Empresarial',
  }
  return labels[dashboard.value.plano] || 'Gratuito'
})

const fetchData = async () => {
  isLoading.value = true
  loadError.value = false
  try {
    const [dashboardResult, tasksResult, membersResult, clientsResult] = await Promise.allSettled([
      api.get('/api/v1/dashboard/'),
      fetchAllPages<TaskData>('/api/v1/obrigacoes'),
      fetchAllPages<Member>('/api/v1/membros'),
      fetchAllPages<Client>('/api/v1/clientes'),
    ])

    if (dashboardResult.status === 'rejected') throw dashboardResult.reason
    if (tasksResult.status === 'rejected') throw tasksResult.reason

    lookupsReady.value =
      membersResult.status === 'fulfilled' && clientsResult.status === 'fulfilled'
    dashboard.value = dashboardResult.value.data
    tasks.value = tasksResult.value
    members.value = membersResult.status === 'fulfilled' ? membersResult.value : []
    clients.value = clientsResult.status === 'fulfilled' ? clientsResult.value : []
  } catch {
    loadError.value = true
    toast.error('Erro ao carregar os dados do dashboard.')
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchData)
</script>

<template>
  <Layout title="Dashboard">
    <div v-if="loadError" role="alert" class="rounded-xl border border-red-200 bg-red-50 p-5">
      <p>Não foi possível carregar o dashboard. Seus indicadores não estão disponíveis.</p>
      <button type="button" class="mt-3 underline" @click="fetchData">Tentar novamente</button>
    </div>
    <OperationalDashboard
      v-else
      :loading="isLoading"
      :dashboard="dashboard"
      :plan-label="planLabel"
      :user-name="authStore.userName || 'Usuário'"
      :tasks="tasks"
      :clients="clients"
      :members="members"
      :lookups-ready="lookupsReady"
      :user-id="authStore.userId"
      :role="authStore.role"
      :read-only="authStore.trialReadOnly"
    />
  </Layout>
</template>
