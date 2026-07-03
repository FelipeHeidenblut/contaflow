<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '../services/api'
import AdminLayout from '../components/AdminLayout.vue'
import { toast } from 'vue3-toastify'

// ==========================================
// 1. KPIs (Métricas do Dashboard)
// ==========================================
interface SaasStats {
  mrr_estimado: number
  total_escritorios: number
  escritorios_ativos: number
  escritorios_inadimplentes: number
  total_usuarios: number
  total_clientes_finais: number
}

const stats = ref<SaasStats | null>(null)
const isLoadingStats = ref(true)

// ==========================================
// 2. GESTÃO DE ESCRITÓRIOS
// ==========================================
interface Tenant {
  id: string
  razao_social: string
  plano: string
  status_pagamento: string
  admin_email: string
}

const tenants = ref<Tenant[]>([])
const isLoadingTenants = ref(true)
const searchQuery = ref('')

const tenantsFiltrados = computed(() => {
  if (!searchQuery.value) return tenants.value
  const termo = searchQuery.value.toLowerCase()
  return tenants.value.filter(
    (t) =>
      t.razao_social.toLowerCase().includes(termo) || t.admin_email.toLowerCase().includes(termo),
  )
})

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)
}

const getPlanoBadge = (plano: string) => {
  const styles: Record<string, string> = {
    free: 'bg-gray-100 text-gray-600',
    basico: 'bg-blue-100 text-blue-700',
    profissional: 'bg-[#eaf3ea] text-[#19341a]',
    business: 'bg-purple-100 text-purple-700',
  }
  return `px-2 py-0.5 rounded-full text-[11px] font-bold border ${styles[plano] || styles['free']}`
}

const getStatusBadge = (status: string) => {
  if (status === 'ativo') return 'bg-emerald-100 text-emerald-700'
  if (status === 'aguardando_pagamento') return 'bg-yellow-100 text-yellow-700'
  if (status === 'inadimplente') return 'bg-red-100 text-red-700'
  return 'bg-gray-100 text-gray-600'
}

const getStatusLabel = (status: string) => {
  if (status === 'ativo') return 'Ativo'
  if (status === 'aguardando_pagamento') return 'Pendente'
  if (status === 'inadimplente') return 'Bloqueado'
  return status
}

// Funções de Ação
const toggleBloqueio = async (tenant: Tenant) => {
  const novoStatus = tenant.status_pagamento === 'ativo' ? 'inadimplente' : 'ativo'
  const acao = novoStatus === 'ativo' ? 'ativado' : 'bloqueado'

  if (!confirm(`Tem certeza que deseja ${acao} o escritório ${tenant.razao_social}?`)) return

  try {
    await api.patch(`/api/v1/admin/tenants/${tenant.id}/status?novo_status=${novo_status}`)
    tenant.status_pagamento = novoStatus // Atualiza a tela na hora
    toast.success(`Escritório ${acao} com sucesso.`)
  } catch (error) {
    toast.error('Erro ao alterar status do escritório.')
  }
}

// Fetchs
const fetchStats = async () => {
  try {
    const response = await api.get<SaasStats>('/api/v1/admin/dashboard-stats')
    stats.value = response.data
  } catch (error: any) {
    toast.error('Erro ao carregar as métricas do SaaS.')
  } finally {
    isLoadingStats.value = false
  }
}

const fetchTenants = async () => {
  try {
    const response = await api.get<Tenant[]>('/api/v1/admin/tenants')
    tenants.value = response.data
  } catch (error: any) {
    toast.error('Erro ao carregar a lista de escritórios.')
  } finally {
    isLoadingTenants.value = false
  }
}

onMounted(() => {
  fetchStats()
  fetchTenants()
})
</script>

<template>
  <AdminLayout title="Backoffice SaaS">
    <div class="mb-8">
      <h1 class="text-3xl font-extrabold text-[#19341a] tracking-tight">Visão Global do Negócio</h1>
      <p class="text-gray-500 mt-1">Métricas de faturamento e adoção em tempo real.</p>
    </div>

    <!-- Skeleton Loading KPIs -->
    <div v-if="isLoadingStats" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
      <div
        v-for="i in 4"
        :key="i"
        class="bg-white border border-gray-100 rounded-2xl p-6 h-32 animate-pulse"
      >
        <div class="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
        <div class="h-8 bg-gray-300 rounded w-3/4"></div>
      </div>
    </div>

    <!-- Cards de KPIs -->
    <div v-else-if="stats" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
      <!-- Card MRR -->
      <div
        class="bg-white border-l-4 border-[#ff8a65] rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow"
      >
        <h3 class="text-sm font-bold uppercase tracking-wider text-gray-400 mb-2">MRR Estimado</h3>
        <p class="text-3xl font-extrabold text-[#19341a]">
          {{ formatCurrency(stats.mrr_estimado) }}
        </p>
        <p class="text-xs text-gray-400 mt-2">Receita recorrente ativa</p>
      </div>

      <!-- Card Escritórios -->
      <div
        class="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow"
      >
        <h3 class="text-sm font-bold uppercase tracking-wider text-gray-400 mb-2">
          Escritórios Ativos
        </h3>
        <div class="flex items-end gap-2">
          <p class="text-3xl font-extrabold text-[#19341a]">{{ stats.escritorios_ativos }}</p>
          <p class="text-sm font-medium text-gray-400 mb-1">
            / {{ stats.total_escritorios }} total
          </p>
        </div>
        <p class="text-xs text-red-500 mt-2 font-medium" v-if="stats.escritorios_inadimplentes > 0">
          {{ stats.escritorios_inadimplentes }} inadimplentes
        </p>
        <p class="text-xs text-green-500 mt-2 font-medium" v-else>Inadimplência zero 🎉</p>
      </div>

      <!-- Card Usuários -->
      <div
        class="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow"
      >
        <h3 class="text-sm font-bold uppercase tracking-wider text-gray-400 mb-2">Usuários</h3>
        <p class="text-3xl font-extrabold text-[#19341a]">{{ stats.total_usuarios }}</p>
        <p class="text-xs text-gray-400 mt-2">Pessoas acessando</p>
      </div>

      <!-- Card Volume de Dados -->
      <div
        class="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow"
      >
        <h3 class="text-sm font-bold uppercase tracking-wider text-gray-400 mb-2">
          Clientes Finais
        </h3>
        <p class="text-3xl font-extrabold text-[#19341a]">{{ stats.total_clientes_finais }}</p>
        <p class="text-xs text-gray-400 mt-2">Empresas gerenciadas</p>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- GESTÃO DE ESCRITÓRIOS E FATURAMENTO        -->
    <!-- ========================================== -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div
        class="p-6 border-b border-gray-100 flex flex-col sm:flex-row items-center justify-between gap-4"
      >
        <div>
          <h2 class="text-xl font-bold text-[#19341a]">Gestão de Escritórios</h2>
          <p class="text-sm text-gray-500 mt-1">Ative, bloqueie ou visualize as contas e planos.</p>
        </div>
        <div class="relative w-full sm:w-64">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar por nome ou e-mail..."
            class="w-full pl-4 pr-4 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#ff8a65] text-sm"
          />
        </div>
      </div>

      <div v-if="isLoadingTenants" class="p-10 text-center text-gray-400">
        Carregando escritórios...
      </div>

      <div v-else-if="tenantsFiltrados.length === 0" class="p-10 text-center text-gray-400">
        Nenhum escritório encontrado.
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-100">
          <thead class="bg-[#f8f8f8]">
            <tr>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-400 uppercase">
                Escritório
              </th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-400 uppercase">Plano</th>
              <th class="px-6 py-4 text-center text-xs font-bold text-gray-400 uppercase">
                Status
              </th>
              <th class="px-6 py-4 text-right text-xs font-bold text-gray-400 uppercase">Ações</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-100">
            <tr
              v-for="tenant in tenantsFiltrados"
              :key="tenant.id"
              class="hover:bg-gray-50 transition-colors"
            >
              <td class="px-6 py-4">
                <div class="text-sm font-bold text-[#19341a]">{{ tenant.razao_social }}</div>
                <div class="text-xs text-gray-400 mt-0.5">{{ tenant.admin_email }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getPlanoBadge(tenant.plano)" class="capitalize">{{
                  tenant.plano
                }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <span
                  class="px-2.5 py-0.5 rounded-full text-xs font-semibold"
                  :class="getStatusBadge(tenant.status_pagamento)"
                >
                  {{ getStatusLabel(tenant.status_pagamento) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right">
                <button
                  v-if="tenant.status_pagamento === 'ativo'"
                  @click="toggleBloqueio(tenant)"
                  class="text-xs font-bold text-red-500 hover:text-red-700 border border-red-200 hover:bg-red-50 px-3 py-1.5 rounded-lg transition-colors"
                >
                  Bloquear Acesso
                </button>
                <button
                  v-else
                  @click="toggleBloqueio(tenant)"
                  class="text-xs font-bold text-emerald-600 hover:text-emerald-700 border border-emerald-200 hover:bg-emerald-50 px-3 py-1.5 rounded-lg transition-colors"
                >
                  Ativar Acesso
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </AdminLayout>
</template>
