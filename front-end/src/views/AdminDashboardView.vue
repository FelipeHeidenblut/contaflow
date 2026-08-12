<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '../services/api'
import AdminLayout from '../components/AdminLayout.vue'
import { toast } from 'vue3-toastify'
import ConfirmDialog from '../components/ConfirmDialog.vue'

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
const tenantToToggle = ref<Tenant | null>(null)

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
    basico: 'bg-[var(--ct-primary-soft)] text-[var(--ct-primary)]',
    profissional: 'bg-[var(--ct-primary-soft)] text-[var(--ct-primary)]',
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
const toggleBloqueio = async () => {
  const tenant = tenantToToggle.value
  if (!tenant) return
  const novoStatus = tenant.status_pagamento === 'ativo' ? 'inadimplente' : 'ativo'
  const acao = novoStatus === 'ativo' ? 'ativado' : 'bloqueado'

  try {
    await api.patch(`/api/v1/admin/tenants/${tenant.id}/status?novo_status=${novoStatus}`)
    tenant.status_pagamento = novoStatus // Atualiza a tela na hora
    toast.success(`Escritório ${acao} com sucesso.`)
    tenantToToggle.value = null
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
    <div class="mb-6 border-b border-[var(--ct-border)] pb-5">
      <h1 class="text-3xl font-semibold tracking-tight text-[var(--ct-ink)]">
        Visão global do negócio
      </h1>
      <p class="text-gray-500 mt-1">Métricas de faturamento e adoção em tempo real.</p>
    </div>

    <!-- Skeleton Loading KPIs -->
    <div v-if="isLoadingStats" class="mb-8 grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-4">
      <div
        v-for="i in 4"
        :key="i"
        class="h-28 animate-pulse rounded-xl border border-gray-100 bg-white p-5"
      >
        <div class="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
        <div class="h-8 bg-gray-300 rounded w-3/4"></div>
      </div>
    </div>

    <!-- Cards de KPIs -->
    <div
      v-else-if="stats"
      class="mb-8 grid grid-cols-1 overflow-hidden rounded-xl border border-[var(--ct-border)] bg-white md:grid-cols-2 lg:grid-cols-4 lg:divide-x lg:divide-[var(--ct-border)]"
    >
      <!-- Card MRR -->
      <div
        class="border-b border-[var(--ct-border)] border-l-4 border-l-[var(--ct-primary)] p-5 md:border-r lg:border-b-0 lg:border-r-0"
      >
        <h3 class="text-sm font-bold uppercase tracking-wider text-gray-400 mb-2">MRR Estimado</h3>
        <p class="text-3xl font-extrabold text-[var(--ct-ink)]">
          {{ formatCurrency(stats.mrr_estimado) }}
        </p>
        <p class="text-xs text-gray-400 mt-2">Receita recorrente ativa</p>
      </div>

      <!-- Card Escritórios -->
      <div class="border-b border-[var(--ct-border)] p-5 lg:border-b-0">
        <h3 class="text-sm font-bold uppercase tracking-wider text-gray-400 mb-2">
          Escritórios Ativos
        </h3>
        <div class="flex items-end gap-2">
          <p class="text-3xl font-extrabold text-[var(--ct-ink)]">{{ stats.escritorios_ativos }}</p>
          <p class="text-sm font-medium text-gray-400 mb-1">
            / {{ stats.total_escritorios }} total
          </p>
        </div>
        <p class="text-xs text-red-500 mt-2 font-medium" v-if="stats.escritorios_inadimplentes > 0">
          {{ stats.escritorios_inadimplentes }} inadimplentes
        </p>
        <p class="mt-2 text-xs font-medium text-green-600" v-else>Inadimplência zero</p>
      </div>

      <!-- Card Usuários -->
      <div class="border-b border-[var(--ct-border)] p-5 md:border-b-0 md:border-r lg:border-r-0">
        <h3 class="text-sm font-bold uppercase tracking-wider text-gray-400 mb-2">Usuários</h3>
        <p class="text-3xl font-extrabold text-[var(--ct-ink)]">{{ stats.total_usuarios }}</p>
        <p class="text-xs text-gray-400 mt-2">Pessoas acessando</p>
      </div>

      <!-- Card Volume de Dados -->
      <div class="p-5">
        <h3 class="text-sm font-bold uppercase tracking-wider text-gray-400 mb-2">
          Clientes Finais
        </h3>
        <p class="text-3xl font-extrabold text-[var(--ct-ink)]">
          {{ stats.total_clientes_finais }}
        </p>
        <p class="text-xs text-gray-400 mt-2">Empresas gerenciadas</p>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- GESTÃO DE ESCRITÓRIOS E FATURAMENTO        -->
    <!-- ========================================== -->
    <div class="overflow-hidden rounded-xl border border-gray-100 bg-white">
      <div
        class="p-6 border-b border-gray-100 flex flex-col sm:flex-row items-center justify-between gap-4"
      >
        <div>
          <h2 class="text-xl font-bold text-[var(--ct-ink)]">Gestão de escritórios</h2>
          <p class="text-sm text-gray-500 mt-1">Ative, bloqueie ou visualize as contas e planos.</p>
        </div>
        <div class="relative w-full sm:w-64">
          <input
            v-model="searchQuery"
            type="search"
            aria-label="Buscar escritório"
            placeholder="Buscar por nome ou e-mail..."
            class="w-full rounded-xl border border-[var(--ct-border)] px-4 py-2.5 text-sm outline-none focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
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
        <div class="divide-y divide-[var(--ct-border)] md:hidden">
          <article v-for="tenant in tenantsFiltrados" :key="`mobile-${tenant.id}`" class="p-4">
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <p class="truncate text-sm font-semibold text-[var(--ct-ink)]">
                  {{ tenant.razao_social }}
                </p>
                <p class="truncate text-xs text-[var(--ct-text-muted)]">{{ tenant.admin_email }}</p>
              </div>
              <span
                class="rounded-full px-2.5 py-1 text-[11px] font-semibold"
                :class="getStatusBadge(tenant.status_pagamento)"
                >{{ getStatusLabel(tenant.status_pagamento) }}</span
              >
            </div>
            <div class="mt-3 flex items-center justify-between">
              <span :class="getPlanoBadge(tenant.plano)" class="capitalize">{{ tenant.plano }}</span
              ><button
                class="text-xs font-semibold"
                :class="tenant.status_pagamento === 'ativo' ? 'text-red-600' : 'text-emerald-700'"
                @click="tenantToToggle = tenant"
              >
                {{ tenant.status_pagamento === 'ativo' ? 'Bloquear' : 'Ativar' }}
              </button>
            </div>
          </article>
        </div>
        <table class="hidden min-w-full divide-y divide-gray-100 md:table">
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
                <div class="text-sm font-bold text-[var(--ct-ink)]">{{ tenant.razao_social }}</div>
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
                  @click="tenantToToggle = tenant"
                  class="text-xs font-bold text-red-500 hover:text-red-700 border border-red-200 hover:bg-red-50 px-3 py-1.5 rounded-lg transition-colors"
                >
                  Bloquear Acesso
                </button>
                <button
                  v-else
                  @click="tenantToToggle = tenant"
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
  <ConfirmDialog
    :open="!!tenantToToggle"
    title="Alterar acesso do escritório"
    :message="`Deseja ${tenantToToggle?.status_pagamento === 'ativo' ? 'bloquear' : 'ativar'} ${tenantToToggle?.razao_social || 'este escritório'}?`"
    :confirm-label="
      tenantToToggle?.status_pagamento === 'ativo' ? 'Bloquear escritório' : 'Ativar escritório'
    "
    @close="tenantToToggle = null"
    @confirm="toggleBloqueio"
  />
</template>
