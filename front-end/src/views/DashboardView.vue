<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { toast } from 'vue3-toastify'
import Layout from '../components/Layout.vue'
import OperationalDashboard from '../components/OperationalDashboard.vue'
import api from '../services/api'
import { useAuthStore } from '../stores/auth'

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

const teamLoad = computed(() => {
  const openAssigned = tasks.value.filter((task) => task.status !== 'concluida' && task.assigned_to)
  const capacity = 8
  const load = new Map<string, { nome: string; count: number; percentual: number }>()

  members.value.forEach((member) => {
    load.set(String(member.id), { nome: member.name, count: 0, percentual: 0 })
  })
  openAssigned.forEach((task) => {
    const member = load.get(String(task.assigned_to))
    if (member) member.count += 1
  })
  load.forEach((member) => {
    member.percentual = Math.min(100, Math.round((member.count / capacity) * 100))
  })

  return Array.from(load.values()).sort((a, b) => b.count - a.count)
})

const planLabel = computed(() => {
  if (dashboard.value.status_pagamento === 'aguardando_pagamento') return 'Pagamento pendente'
  if (dashboard.value.status_pagamento === 'inadimplente') return 'Conta bloqueada'
  const labels: Record<string, string> = {
    free: 'Gratuito',
    basico: 'Essencial',
    profissional: 'Profissional',
    business: 'Empresarial',
  }
  return labels[dashboard.value.plano] || 'Gratuito'
})

const fetchData = async () => {
  isLoading.value = true
  try {
    const [dashboardResult, tasksResult, membersResult, clientsResult] = await Promise.allSettled([
      api.get('/api/v1/dashboard/'),
      api.get('/api/v1/obrigacoes'),
      api.get('/api/v1/membros'),
      api.get('/api/v1/clientes'),
    ])

    if (dashboardResult.status === 'rejected') throw dashboardResult.reason
    if (tasksResult.status === 'rejected') throw tasksResult.reason

    dashboard.value = dashboardResult.value.data
    tasks.value = tasksResult.value.data
    members.value = membersResult.status === 'fulfilled' ? membersResult.value.data : []
    clients.value = clientsResult.status === 'fulfilled' ? clientsResult.value.data : []
  } catch {
    toast.error('Erro ao carregar os dados do dashboard.')
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchData)
</script>

<template>
  <Layout title="Dashboard">
    <OperationalDashboard
      :loading="isLoading"
      :dashboard="dashboard"
      :plan-label="planLabel"
      :user-name="authStore.userName || 'Usuário'"
      :tasks="tasks"
      :clients="clients"
      :team="teamLoad"
    />
  </Layout>
</template>
