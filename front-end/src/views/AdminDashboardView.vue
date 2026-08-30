<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import {
  CategoryScale,
  Chart as ChartJS,
  ArcElement,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
} from 'chart.js'
import { Doughnut, Line } from 'vue-chartjs'
import { toast } from 'vue3-toastify'
import api from '../services/api'
import AdminLayout from '../components/AdminLayout.vue'
import { getPlan } from '@/constants/plans'
import { getApiErrorMessage } from '../utils/apiError'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Filler,
  Tooltip,
  Legend,
)

interface Overview {
  generated_at: string
  stats: {
    mrr: number
    mrr_actual_coverage: number
    paying_offices: number
    new_offices_month: number
    new_offices_change_pct: number | null
    delinquency_rate: number
    total_users: number
    total_clients: number
    average_ticket: number
    revenue_month: number
    revenue_change_pct: number | null
  }
  plans: Array<{ id: string; name: string; count: number }>
  trend: Array<{ month: string; label: string; signups: number; revenue: number }>
  attention: {
    total: number
    items: Array<{
      type: string
      severity: 'critical' | 'warning' | 'info'
      title: string
      description: string
      count: number
      filter_status: string | null
    }>
  }
}

interface Tenant {
  id: string
  razao_social: string
  plano: string
  billing_cycle: string
  status_pagamento: string
  admin_email: string
  created_at: string
  user_count: number
  client_count: number
  task_count: number
  last_activity_at: string | null
}

interface TenantPage {
  items: Tenant[]
  page: number
  page_size: number
  total: number
  pages: number
}

interface TenantDetail {
  id: string
  razao_social: string
  cnpj: string | null
  plano: string
  billing_cycle: string
  status_pagamento: string
  created_at: string
  last_activity_at: string | null
  usage: {
    users: number
    user_limit: number | null
    clients: number
    client_limit: number | null
    tasks: number
  }
  provider: { customer_id: string | null; subscription_id: string | null }
  members: Array<{ id: string; name: string; email: string; role: string }>
  payments: Array<{
    id: string
    value: number
    status: string
    due_date: string | null
    paid_at: string | null
    invoice_url: string | null
  }>
  audit: Array<{
    id: string
    action: string
    reason: string
    old_value: string | null
    new_value: string | null
    actor_name: string
    created_at: string
  }>
}

const overview = ref<Overview | null>(null)
const tenantsPage = ref<TenantPage>({ items: [], page: 1, page_size: 20, total: 0, pages: 1 })
const isLoadingOverview = ref(true)
const isLoadingTenants = ref(true)
const isRefreshing = ref(false)
const selectedTenant = ref<TenantDetail | null>(null)
const isLoadingDetail = ref(false)
const isExporting = ref(false)
const periodMonths = ref(6)
const search = ref('')
const planFilter = ref('')
const statusFilter = ref('')
const sortBy = ref('created_at')
const page = ref(1)
const tenantForAction = ref<Tenant | TenantDetail | null>(null)
const actionReason = ref('')
const isChangingStatus = ref(false)
let searchTimer: ReturnType<typeof setTimeout> | null = null

const formatCurrency = (value: number) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)

const formatDate = (value: string | null, withTime = false) => {
  if (!value) return 'Sem atividade'
  return new Intl.DateTimeFormat(
    'pt-BR',
    withTime ? { dateStyle: 'short', timeStyle: 'short' } : { dateStyle: 'short' },
  ).format(new Date(value))
}

const formatChange = (value: number | null) => {
  if (value === null) return 'Sem base anterior'
  return `${value >= 0 ? '+' : ''}${value.toLocaleString('pt-BR')}% vs. mês anterior`
}

const getPlanLabel = (plan: string) => getPlan(plan)?.name || plan

const getPlanBadge = (plan: string) => {
  const styles: Record<string, string> = {
    free: 'border-slate-200 bg-slate-50 text-slate-600',
    basico: 'border-blue-200 bg-blue-50 text-blue-700',
    profissional: 'border-indigo-200 bg-indigo-50 text-indigo-700',
    escritorio: 'border-cyan-200 bg-cyan-50 text-cyan-700',
    business: 'border-violet-200 bg-violet-50 text-violet-700',
  }
  return `inline-flex rounded-full border px-2.5 py-1 text-[11px] font-semibold ${styles[plan] || styles.free}`
}

const getStatus = (status: string) => {
  const values: Record<string, { label: string; class: string }> = {
    ativo: { label: 'Ativo', class: 'border-emerald-200 bg-emerald-50 text-emerald-700' },
    aguardando_pagamento: {
      label: 'Pendente',
      class: 'border-amber-200 bg-amber-50 text-amber-700',
    },
    inadimplente: { label: 'Bloqueado', class: 'border-red-200 bg-red-50 text-red-700' },
    estornado: { label: 'Estornado', class: 'border-orange-200 bg-orange-50 text-orange-700' },
    cancelado: { label: 'Cancelado', class: 'border-slate-300 bg-slate-100 text-slate-700' },
    chargeback: { label: 'Chargeback', class: 'border-rose-300 bg-rose-50 text-rose-800' },
  }
  return values[status] || { label: status, class: 'border-slate-200 bg-slate-50 text-slate-600' }
}

const getPaymentStatus = (status: string) => {
  const labels: Record<string, string> = {
    pending: 'Pendente',
    confirmed: 'Confirmado',
    received: 'Recebido',
    overdue: 'Vencido',
    refund_pending: 'Estorno em andamento',
    partially_refunded: 'Estorno parcial',
    refunded: 'Estornado',
    canceled: 'Cancelado',
    chargeback: 'Chargeback',
  }
  return labels[status] || status
}

const getRoleLabel = (role: string) => {
  if (role === 'admin') return 'Administrador'
  if (role === 'gerente') return 'Gerente'
  return 'Colaborador'
}

const lineData = computed(() => ({
  labels: overview.value?.trend.map((item) => item.label) || [],
  datasets: [
    {
      label: 'Receita confirmada',
      data: overview.value?.trend.map((item) => item.revenue) || [],
      borderColor: '#2563eb',
      backgroundColor: 'rgba(37, 99, 235, 0.10)',
      pointBackgroundColor: '#2563eb',
      tension: 0.35,
      fill: true,
      yAxisID: 'y',
    },
    {
      label: 'Novos escritórios',
      data: overview.value?.trend.map((item) => item.signups) || [],
      borderColor: '#0f9f6e',
      backgroundColor: '#0f9f6e',
      pointBackgroundColor: '#0f9f6e',
      tension: 0.35,
      yAxisID: 'y1',
    },
  ],
}))

const lineOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index' as const, intersect: false },
  plugins: { legend: { position: 'bottom' as const, labels: { usePointStyle: true } } },
  scales: {
    y: {
      beginAtZero: true,
      grid: { color: '#edf0f5' },
      ticks: { callback: (value: string | number) => `R$ ${value}` },
    },
    y1: {
      beginAtZero: true,
      position: 'right' as const,
      grid: { drawOnChartArea: false },
      ticks: { precision: 0 },
    },
  },
}

const planData = computed(() => ({
  labels: overview.value?.plans.map((plan) => plan.name) || [],
  datasets: [
    {
      data: overview.value?.plans.map((plan) => plan.count) || [],
      backgroundColor: ['#cbd5e1', '#60a5fa', '#2563eb', '#0891b2', '#7c3aed'],
      borderWidth: 0,
      hoverOffset: 4,
    },
  ],
}))

const planOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '68%',
  plugins: {
    legend: { position: 'bottom' as const, labels: { usePointStyle: true, boxWidth: 8 } },
  },
}

const tenantParams = computed(() => ({
  search: search.value || undefined,
  plan: planFilter.value || undefined,
  payment_status: statusFilter.value || undefined,
  sort_by: sortBy.value,
  page: page.value,
  page_size: 20,
}))

const fetchOverview = async () => {
  try {
    const { data } = await api.get<Overview>('/api/v1/admin/overview', {
      params: { months: periodMonths.value },
    })
    overview.value = data
  } catch (error: unknown) {
    toast.error(getApiErrorMessage(error, 'Não foi possível carregar os indicadores.'))
  } finally {
    isLoadingOverview.value = false
  }
}

const fetchTenants = async () => {
  isLoadingTenants.value = true
  try {
    const { data } = await api.get<TenantPage>('/api/v1/admin/tenants', {
      params: tenantParams.value,
    })
    tenantsPage.value = data
  } catch (error: unknown) {
    toast.error(getApiErrorMessage(error, 'Não foi possível carregar os escritórios.'))
  } finally {
    isLoadingTenants.value = false
  }
}

const refreshAll = async () => {
  isRefreshing.value = true
  await Promise.all([fetchOverview(), fetchTenants()])
  isRefreshing.value = false
}

const openTenant = async (tenant: { id: string }) => {
  isLoadingDetail.value = true
  selectedTenant.value = null
  try {
    const { data } = await api.get<TenantDetail>(`/api/v1/admin/tenants/${tenant.id}`)
    selectedTenant.value = data
  } catch (error: unknown) {
    toast.error(getApiErrorMessage(error, 'Não foi possível abrir o escritório.'))
  } finally {
    isLoadingDetail.value = false
  }
}

const requestStatusChange = (tenant: Tenant | TenantDetail) => {
  tenantForAction.value = tenant
  actionReason.value = ''
}

const changeStatus = async () => {
  if (!tenantForAction.value || actionReason.value.trim().length < 3) {
    toast.warning('Informe o motivo da alteração.')
    return
  }
  const nextStatus = tenantForAction.value.status_pagamento === 'ativo' ? 'inadimplente' : 'ativo'
  isChangingStatus.value = true
  try {
    const selectedTenantId = selectedTenant.value?.id
    await api.patch(`/api/v1/admin/tenants/${tenantForAction.value.id}/status`, {
      status: nextStatus,
      reason: actionReason.value.trim(),
    })
    toast.success(nextStatus === 'ativo' ? 'Escritório reativado.' : 'Escritório bloqueado.')
    tenantForAction.value = null
    await refreshAll()
    if (selectedTenantId) await openTenant({ id: selectedTenantId })
  } catch (error: unknown) {
    toast.error(getApiErrorMessage(error, 'Não foi possível alterar o status.'))
  } finally {
    isChangingStatus.value = false
  }
}

const applyAttentionFilter = (item: Overview['attention']['items'][number]) => {
  if (item.filter_status) {
    statusFilter.value = item.filter_status
    page.value = 1
    document.getElementById('tenants-table')?.scrollIntoView({ behavior: 'smooth' })
  } else {
    toast.info(item.description)
  }
}

const exportCsv = async () => {
  isExporting.value = true
  try {
    const response = await api.get('/api/v1/admin/tenants/export', {
      params: {
        search: search.value || undefined,
        plan: planFilter.value || undefined,
        payment_status: statusFilter.value || undefined,
      },
      responseType: 'blob',
    })
    const url = URL.createObjectURL(new Blob([response.data], { type: 'text/csv;charset=utf-8' }))
    const link = document.createElement('a')
    link.href = url
    link.download = 'escritorios-contablytask.csv'
    link.click()
    URL.revokeObjectURL(url)
  } catch (error: unknown) {
    toast.error(getApiErrorMessage(error, 'Não foi possível exportar os escritórios.'))
  } finally {
    isExporting.value = false
  }
}

const usagePercentage = (current: number, limit: number | null) =>
  limit ? Math.min(100, Math.round((current / limit) * 100)) : 0

watch(periodMonths, fetchOverview)
watch([planFilter, statusFilter, sortBy], () => {
  if (page.value === 1) fetchTenants()
  else page.value = 1
})
watch(page, fetchTenants)
watch(search, () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    if (page.value === 1) fetchTenants()
    else page.value = 1
  }, 350)
})

onMounted(refreshAll)
onBeforeUnmount(() => {
  if (searchTimer) clearTimeout(searchTimer)
})
</script>

<template>
  <AdminLayout title="Backoffice SaaS">
    <div class="space-y-5">
      <header
        class="flex flex-col gap-4 border-b border-[var(--ct-border)] pb-5 lg:flex-row lg:items-end lg:justify-between"
      >
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--ct-primary)]">
            Operação SaaS
          </p>
          <h1 class="mt-2 text-2xl font-semibold tracking-tight text-[var(--ct-ink)] sm:text-3xl">
            Visão global do negócio
          </h1>
          <p class="mt-1 text-sm text-[var(--ct-text-muted)]">
            Receita, crescimento, adoção e contas que precisam de atenção.
          </p>
        </div>
        <div class="flex flex-col gap-2 sm:flex-row">
          <select
            v-model="periodMonths"
            class="rounded-lg border border-[var(--ct-border)] bg-white px-3 py-2.5 text-sm text-[var(--ct-ink)] outline-none focus:border-[var(--ct-primary)]"
          >
            <option :value="6">Últimos 6 meses</option>
            <option :value="12">Últimos 12 meses</option>
          </select>
          <button class="ct-button-primary min-h-10" :disabled="isRefreshing" @click="refreshAll">
            {{ isRefreshing ? 'Atualizando...' : 'Atualizar dados' }}
          </button>
        </div>
      </header>

      <section v-if="isLoadingOverview" class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        <div
          v-for="index in 6"
          :key="index"
          class="h-28 animate-pulse rounded-xl border border-[var(--ct-border)] bg-white"
        ></div>
      </section>

      <template v-else-if="overview">
        <section class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          <article class="rounded-xl border border-[var(--ct-border)] bg-white p-5">
            <div class="flex items-start justify-between gap-3">
              <p class="text-xs font-semibold uppercase tracking-[0.1em] text-slate-500">
                MRR atual
              </p>
              <span
                class="rounded-full bg-blue-50 px-2 py-1 text-[10px] font-semibold text-blue-700"
                >{{ overview.stats.mrr_actual_coverage }}% real</span
              >
            </div>
            <p class="mt-3 text-2xl font-semibold text-[var(--ct-ink)]">
              {{ formatCurrency(overview.stats.mrr) }}
            </p>
            <p class="mt-1 text-xs text-[var(--ct-text-muted)]">
              Pagamentos reais com fallback para contratos antigos.
            </p>
          </article>
          <article class="rounded-xl border border-[var(--ct-border)] bg-white p-5">
            <p class="text-xs font-semibold uppercase tracking-[0.1em] text-slate-500">
              Escritórios pagantes
            </p>
            <p class="mt-3 text-2xl font-semibold text-[var(--ct-ink)]">
              {{ overview.stats.paying_offices }}
            </p>
            <p class="mt-1 text-xs text-[var(--ct-text-muted)]">
              Ticket médio de {{ formatCurrency(overview.stats.average_ticket) }}.
            </p>
          </article>
          <article class="rounded-xl border border-[var(--ct-border)] bg-white p-5">
            <p class="text-xs font-semibold uppercase tracking-[0.1em] text-slate-500">
              Receita no mês
            </p>
            <p class="mt-3 text-2xl font-semibold text-[var(--ct-ink)]">
              {{ formatCurrency(overview.stats.revenue_month) }}
            </p>
            <p
              class="mt-1 text-xs"
              :class="
                (overview.stats.revenue_change_pct || 0) >= 0 ? 'text-emerald-600' : 'text-red-600'
              "
            >
              {{ formatChange(overview.stats.revenue_change_pct) }}
            </p>
          </article>
          <article class="rounded-xl border border-[var(--ct-border)] bg-white p-5">
            <p class="text-xs font-semibold uppercase tracking-[0.1em] text-slate-500">
              Novos no mês
            </p>
            <p class="mt-3 text-2xl font-semibold text-[var(--ct-ink)]">
              {{ overview.stats.new_offices_month }}
            </p>
            <p
              class="mt-1 text-xs"
              :class="
                (overview.stats.new_offices_change_pct || 0) >= 0
                  ? 'text-emerald-600'
                  : 'text-red-600'
              "
            >
              {{ formatChange(overview.stats.new_offices_change_pct) }}
            </p>
          </article>
          <article class="rounded-xl border border-[var(--ct-border)] bg-white p-5">
            <p class="text-xs font-semibold uppercase tracking-[0.1em] text-slate-500">
              Inadimplência
            </p>
            <p
              class="mt-3 text-2xl font-semibold"
              :class="overview.stats.delinquency_rate > 0 ? 'text-red-600' : 'text-emerald-600'"
            >
              {{ overview.stats.delinquency_rate.toLocaleString('pt-BR') }}%
            </p>
            <p class="mt-1 text-xs text-[var(--ct-text-muted)]">
              Percentual sobre todos os escritórios.
            </p>
          </article>
          <article class="rounded-xl border border-[var(--ct-border)] bg-white p-5">
            <p class="text-xs font-semibold uppercase tracking-[0.1em] text-slate-500">
              Adoção total
            </p>
            <p class="mt-3 text-2xl font-semibold text-[var(--ct-ink)]">
              {{ overview.stats.total_users }} usuários
            </p>
            <p class="mt-1 text-xs text-[var(--ct-text-muted)]">
              {{ overview.stats.total_clients }} clientes finais gerenciados.
            </p>
          </article>
        </section>

        <section class="grid gap-4 xl:grid-cols-[minmax(0,1.65fr)_minmax(300px,0.75fr)]">
          <article class="rounded-xl border border-[var(--ct-border)] bg-white p-5">
            <div>
              <h2 class="text-base font-semibold text-[var(--ct-ink)]">Crescimento e receita</h2>
              <p class="mt-1 text-xs text-[var(--ct-text-muted)]">
                Pagamentos confirmados e novos escritórios por mês.
              </p>
            </div>
            <div class="mt-5 h-72"><Line :data="lineData" :options="lineOptions" /></div>
          </article>
          <article class="rounded-xl border border-[var(--ct-border)] bg-white p-5">
            <h2 class="text-base font-semibold text-[var(--ct-ink)]">Distribuição por plano</h2>
            <p class="mt-1 text-xs text-[var(--ct-text-muted)]">Composição atual da base.</p>
            <div class="mt-5 h-72"><Doughnut :data="planData" :options="planOptions" /></div>
          </article>
        </section>

        <section class="rounded-xl border border-[var(--ct-border)] bg-white">
          <div class="border-b border-[var(--ct-border)] px-5 py-4">
            <h2 class="text-base font-semibold text-[var(--ct-ink)]">Requer atenção</h2>
            <p class="mt-1 text-xs text-[var(--ct-text-muted)]">
              Sinais que podem exigir uma ação administrativa.
            </p>
          </div>
          <div
            class="grid divide-y divide-[var(--ct-border)] md:grid-cols-5 md:divide-x md:divide-y-0"
          >
            <button
              v-for="item in overview.attention.items"
              :key="item.type"
              class="p-4 text-left transition-colors hover:bg-slate-50"
              @click="applyAttentionFilter(item)"
            >
              <div class="flex items-center justify-between gap-2">
                <span
                  class="h-2 w-2 rounded-full"
                  :class="
                    item.severity === 'critical'
                      ? 'bg-red-500'
                      : item.severity === 'warning'
                        ? 'bg-amber-500'
                        : 'bg-blue-500'
                  "
                ></span
                ><strong class="text-lg text-[var(--ct-ink)]">{{ item.count }}</strong>
              </div>
              <p class="mt-3 text-xs font-semibold text-[var(--ct-ink)]">{{ item.title }}</p>
              <p class="mt-1 text-[11px] leading-4 text-[var(--ct-text-muted)]">
                {{ item.description }}
              </p>
            </button>
          </div>
        </section>
      </template>

      <section
        id="tenants-table"
        class="overflow-hidden rounded-xl border border-[var(--ct-border)] bg-white"
      >
        <div class="border-b border-[var(--ct-border)] p-5">
          <div class="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
            <div>
              <h2 class="text-lg font-semibold text-[var(--ct-ink)]">Escritórios</h2>
              <p class="mt-1 text-xs text-[var(--ct-text-muted)]">
                {{ tenantsPage.total }} conta(s) encontrada(s).
              </p>
            </div>
            <div class="grid gap-2 sm:grid-cols-2 xl:flex">
              <input
                v-model="search"
                type="search"
                placeholder="Nome ou e-mail..."
                class="rounded-lg border border-[var(--ct-border)] px-3 py-2.5 text-sm outline-none focus:border-[var(--ct-primary)] xl:w-56"
              />
              <select
                v-model="planFilter"
                class="rounded-lg border border-[var(--ct-border)] bg-white px-3 py-2.5 text-sm"
              >
                <option value="">Todos os planos</option>
                <option value="free">Gratuito</option>
                <option value="basico">Essencial</option>
                <option value="profissional">Profissional</option>
                <option value="escritorio">Escritório</option>
                <option value="business">Empresarial</option>
              </select>
              <select
                v-model="statusFilter"
                class="rounded-lg border border-[var(--ct-border)] bg-white px-3 py-2.5 text-sm"
              >
                <option value="">Todos os status</option>
                <option value="ativo">Ativos</option>
                <option value="aguardando_pagamento">Pendentes</option>
                <option value="inadimplente">Bloqueados</option>
                <option value="estornado">Estornados</option>
                <option value="cancelado">Cancelados</option>
                <option value="chargeback">Chargebacks</option>
              </select>
              <select
                v-model="sortBy"
                class="rounded-lg border border-[var(--ct-border)] bg-white px-3 py-2.5 text-sm"
              >
                <option value="created_at">Mais recentes</option>
                <option value="last_activity">Última atividade</option>
                <option value="clients">Mais clientes</option>
                <option value="users">Mais usuários</option>
                <option value="name">Nome</option>
              </select>
              <button
                class="rounded-lg border border-[var(--ct-border)] bg-white px-3 py-2.5 text-sm font-semibold text-[#52617a] hover:bg-slate-50"
                :disabled="isExporting"
                @click="exportCsv"
              >
                {{ isExporting ? 'Exportando...' : 'Exportar CSV' }}
              </button>
            </div>
          </div>
        </div>

        <div v-if="isLoadingTenants" class="space-y-3 p-6">
          <div
            v-for="index in 4"
            :key="index"
            class="h-14 animate-pulse rounded-lg bg-slate-100"
          ></div>
        </div>
        <div v-else-if="tenantsPage.items.length === 0" class="p-12 text-center">
          <p class="text-sm font-semibold text-[var(--ct-ink)]">Nenhum escritório encontrado</p>
          <p class="mt-1 text-xs text-[var(--ct-text-muted)]">
            Ajuste os filtros para ampliar a busca.
          </p>
        </div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-[980px] w-full">
            <thead class="border-b border-[var(--ct-border)] bg-slate-50/80">
              <tr>
                <th
                  class="px-5 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-slate-500"
                >
                  Escritório
                </th>
                <th
                  class="px-4 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-slate-500"
                >
                  Plano e status
                </th>
                <th
                  class="px-4 py-3 text-center text-[10px] font-semibold uppercase tracking-wider text-slate-500"
                >
                  Uso
                </th>
                <th
                  class="px-4 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-slate-500"
                >
                  Última atividade
                </th>
                <th
                  class="px-5 py-3 text-right text-[10px] font-semibold uppercase tracking-wider text-slate-500"
                >
                  Ações
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[var(--ct-border)]">
              <tr v-for="tenant in tenantsPage.items" :key="tenant.id" class="hover:bg-slate-50/70">
                <td class="px-5 py-4">
                  <button class="text-left" @click="openTenant(tenant)">
                    <p
                      class="text-sm font-semibold text-[var(--ct-ink)] hover:text-[var(--ct-primary)]"
                    >
                      {{ tenant.razao_social }}
                    </p>
                    <p class="mt-0.5 text-xs text-[var(--ct-text-muted)]">
                      {{ tenant.admin_email }}
                    </p>
                    <p class="mt-1 text-[10px] text-slate-400">
                      Desde {{ formatDate(tenant.created_at) }}
                    </p>
                  </button>
                </td>
                <td class="px-4 py-4">
                  <div class="flex flex-wrap gap-2">
                    <span :class="getPlanBadge(tenant.plano)">{{ getPlanLabel(tenant.plano) }}</span
                    ><span
                      v-if="tenant.plano !== 'free'"
                      class="inline-flex rounded-full border border-slate-200 bg-white px-2.5 py-1 text-[11px] font-semibold text-slate-500"
                      >{{ tenant.billing_cycle === 'annual' ? 'Anual' : 'Mensal' }}</span
                    ><span
                      class="inline-flex rounded-full border px-2.5 py-1 text-[11px] font-semibold"
                      :class="getStatus(tenant.status_pagamento).class"
                      >{{ getStatus(tenant.status_pagamento).label }}</span
                    >
                  </div>
                </td>
                <td class="px-4 py-4 text-center">
                  <p class="text-xs font-semibold text-[var(--ct-ink)]">
                    {{ tenant.client_count }} clientes
                  </p>
                  <p class="mt-1 text-[11px] text-[var(--ct-text-muted)]">
                    {{ tenant.user_count }} usuários · {{ tenant.task_count }} tarefas
                  </p>
                </td>
                <td class="px-4 py-4 text-xs text-[#52617a]">
                  {{ formatDate(tenant.last_activity_at, true) }}
                </td>
                <td class="px-5 py-4">
                  <div class="flex justify-end gap-2">
                    <button
                      class="rounded-lg border border-[var(--ct-border)] px-3 py-2 text-xs font-semibold text-[#52617a] hover:bg-slate-50"
                      @click="openTenant(tenant)"
                    >
                      Detalhes</button
                    ><button
                      class="rounded-lg border px-3 py-2 text-xs font-semibold"
                      :class="
                        tenant.status_pagamento === 'ativo'
                          ? 'border-red-200 text-red-600 hover:bg-red-50'
                          : 'border-emerald-200 text-emerald-700 hover:bg-emerald-50'
                      "
                      @click="requestStatusChange(tenant)"
                    >
                      {{ tenant.status_pagamento === 'ativo' ? 'Bloquear' : 'Reativar' }}
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div
          v-if="tenantsPage.total > 0"
          class="flex items-center justify-between border-t border-[var(--ct-border)] px-5 py-4"
        >
          <p class="text-xs text-[var(--ct-text-muted)]">
            Página {{ tenantsPage.page }} de {{ tenantsPage.pages }}
          </p>
          <div class="flex gap-2">
            <button
              class="rounded-lg border border-[var(--ct-border)] px-3 py-2 text-xs font-semibold disabled:opacity-40"
              :disabled="page <= 1"
              @click="page--"
            >
              Anterior</button
            ><button
              class="rounded-lg border border-[var(--ct-border)] px-3 py-2 text-xs font-semibold disabled:opacity-40"
              :disabled="page >= tenantsPage.pages"
              @click="page++"
            >
              Próxima
            </button>
          </div>
        </div>
      </section>
    </div>

    <div v-if="isLoadingDetail || selectedTenant" class="fixed inset-0 z-50 overflow-hidden">
      <div class="absolute inset-0 bg-slate-950/45" @click="selectedTenant = null"></div>
      <aside
        class="absolute inset-y-0 right-0 w-full max-w-2xl overflow-y-auto bg-white shadow-2xl"
      >
        <div v-if="isLoadingDetail" class="space-y-4 p-6">
          <div class="h-16 animate-pulse rounded-xl bg-slate-100"></div>
          <div class="h-40 animate-pulse rounded-xl bg-slate-100"></div>
          <div class="h-64 animate-pulse rounded-xl bg-slate-100"></div>
        </div>
        <template v-else-if="selectedTenant">
          <header
            class="sticky top-0 z-10 border-b border-[var(--ct-border)] bg-white/95 px-6 py-5 backdrop-blur"
          >
            <div class="flex items-start justify-between gap-4">
              <div>
                <div class="flex flex-wrap gap-2">
                  <span :class="getPlanBadge(selectedTenant.plano)">{{
                    getPlanLabel(selectedTenant.plano)
                  }}</span
                  ><span
                    v-if="selectedTenant.plano !== 'free'"
                    class="inline-flex rounded-full border border-slate-200 bg-white px-2.5 py-1 text-[11px] font-semibold text-slate-500"
                    >{{ selectedTenant.billing_cycle === 'annual' ? 'Anual' : 'Mensal' }}</span
                  ><span
                    class="inline-flex rounded-full border px-2.5 py-1 text-[11px] font-semibold"
                    :class="getStatus(selectedTenant.status_pagamento).class"
                    >{{ getStatus(selectedTenant.status_pagamento).label }}</span
                  >
                </div>
                <h2 class="mt-3 text-xl font-semibold text-[var(--ct-ink)]">
                  {{ selectedTenant.razao_social }}
                </h2>
                <p class="mt-1 text-xs text-[var(--ct-text-muted)]">
                  {{ selectedTenant.cnpj || 'Documento não informado' }} · cadastro em
                  {{ formatDate(selectedTenant.created_at) }}
                </p>
              </div>
              <button
                class="rounded-lg p-2 text-slate-400 hover:bg-slate-100"
                aria-label="Fechar detalhes"
                @click="selectedTenant = null"
              >
                ✕
              </button>
            </div>
          </header>
          <div class="space-y-6 p-6">
            <section class="grid gap-3 sm:grid-cols-3">
              <div class="rounded-xl border border-[var(--ct-border)] bg-slate-50 p-4">
                <p class="text-xs text-[var(--ct-text-muted)]">Usuários</p>
                <p class="mt-1 text-lg font-semibold">
                  {{ selectedTenant.usage.users }} / {{ selectedTenant.usage.user_limit || '∞' }}
                </p>
                <div
                  v-if="selectedTenant.usage.user_limit"
                  class="mt-3 h-1.5 rounded-full bg-slate-200"
                >
                  <div
                    class="h-full rounded-full bg-blue-500"
                    :style="{
                      width: `${usagePercentage(selectedTenant.usage.users, selectedTenant.usage.user_limit)}%`,
                    }"
                  ></div>
                </div>
              </div>
              <div class="rounded-xl border border-[var(--ct-border)] bg-slate-50 p-4">
                <p class="text-xs text-[var(--ct-text-muted)]">Clientes</p>
                <p class="mt-1 text-lg font-semibold">
                  {{ selectedTenant.usage.clients }} /
                  {{ selectedTenant.usage.client_limit || '∞' }}
                </p>
                <div
                  v-if="selectedTenant.usage.client_limit"
                  class="mt-3 h-1.5 rounded-full bg-slate-200"
                >
                  <div
                    class="h-full rounded-full bg-indigo-500"
                    :style="{
                      width: `${usagePercentage(selectedTenant.usage.clients, selectedTenant.usage.client_limit)}%`,
                    }"
                  ></div>
                </div>
              </div>
              <div class="rounded-xl border border-[var(--ct-border)] bg-slate-50 p-4">
                <p class="text-xs text-[var(--ct-text-muted)]">Tarefas</p>
                <p class="mt-1 text-lg font-semibold">{{ selectedTenant.usage.tasks }}</p>
                <p class="mt-3 text-[10px] text-slate-400">
                  Última atividade: {{ formatDate(selectedTenant.last_activity_at, true) }}
                </p>
              </div>
            </section>
            <section>
              <h3 class="text-sm font-semibold text-[var(--ct-ink)]">Assinatura</h3>
              <div class="mt-3 grid gap-3 sm:grid-cols-2">
                <div class="rounded-xl border border-[var(--ct-border)] p-4">
                  <p class="text-xs text-[var(--ct-text-muted)]">Cliente Asaas</p>
                  <p class="mt-1 font-mono text-sm">
                    {{ selectedTenant.provider.customer_id || 'Não vinculado' }}
                  </p>
                </div>
                <div class="rounded-xl border border-[var(--ct-border)] p-4">
                  <p class="text-xs text-[var(--ct-text-muted)]">Assinatura Asaas</p>
                  <p class="mt-1 font-mono text-sm">
                    {{ selectedTenant.provider.subscription_id || 'Não vinculada' }}
                  </p>
                </div>
              </div>
            </section>
            <section>
              <h3 class="text-sm font-semibold text-[var(--ct-ink)]">Equipe</h3>
              <div
                class="mt-3 divide-y divide-[var(--ct-border)] rounded-xl border border-[var(--ct-border)]"
              >
                <div
                  v-for="member in selectedTenant.members"
                  :key="member.id"
                  class="flex items-center justify-between gap-3 p-3"
                >
                  <div class="min-w-0">
                    <p class="truncate text-sm font-medium text-[var(--ct-ink)]">
                      {{ member.name }}
                    </p>
                    <p class="truncate text-xs text-[var(--ct-text-muted)]">{{ member.email }}</p>
                  </div>
                  <span class="text-[11px] font-semibold text-[#52617a]">{{
                    getRoleLabel(member.role)
                  }}</span>
                </div>
              </div>
            </section>
            <section>
              <h3 class="text-sm font-semibold text-[var(--ct-ink)]">Pagamentos recentes</h3>
              <div
                v-if="selectedTenant.payments.length"
                class="mt-3 divide-y divide-[var(--ct-border)] rounded-xl border border-[var(--ct-border)]"
              >
                <div
                  v-for="payment in selectedTenant.payments"
                  :key="payment.id"
                  class="flex items-center justify-between gap-3 p-3"
                >
                  <div>
                    <p class="text-sm font-semibold">{{ formatCurrency(payment.value) }}</p>
                    <p class="text-[11px] text-[var(--ct-text-muted)]">
                      {{
                        payment.paid_at
                          ? `Pago em ${formatDate(payment.paid_at)}`
                          : `Vence em ${formatDate(payment.due_date)}`
                      }}
                    </p>
                  </div>
                  <span
                    class="rounded-full bg-slate-100 px-2 py-1 text-[10px] font-semibold uppercase text-slate-600"
                    >{{ getPaymentStatus(payment.status) }}</span
                  >
                </div>
              </div>
              <p
                v-else
                class="mt-3 rounded-xl border border-dashed border-[var(--ct-border)] p-5 text-center text-xs text-[var(--ct-text-muted)]"
              >
                O histórico será preenchido pelos próximos webhooks do Asaas.
              </p>
            </section>
            <section>
              <h3 class="text-sm font-semibold text-[var(--ct-ink)]">Histórico administrativo</h3>
              <ol v-if="selectedTenant.audit.length" class="mt-3 space-y-3">
                <li
                  v-for="log in selectedTenant.audit"
                  :key="log.id"
                  class="rounded-xl border border-[var(--ct-border)] p-3"
                >
                  <div class="flex justify-between gap-3">
                    <p class="text-xs font-semibold text-[var(--ct-ink)]">{{ log.actor_name }}</p>
                    <time class="text-[10px] text-slate-400">{{
                      formatDate(log.created_at, true)
                    }}</time>
                  </div>
                  <p class="mt-2 text-sm text-[#52617a]">{{ log.reason }}</p>
                  <p v-if="log.old_value || log.new_value" class="mt-2 text-[11px] text-slate-400">
                    {{ log.old_value || '—' }} → {{ log.new_value || '—' }}
                  </p>
                </li>
              </ol>
              <p v-else class="mt-3 text-xs text-[var(--ct-text-muted)]">
                Nenhuma ação administrativa registrada.
              </p>
            </section>
            <button
              class="w-full rounded-xl border px-4 py-3 text-sm font-semibold"
              :class="
                selectedTenant.status_pagamento === 'ativo'
                  ? 'border-red-200 text-red-600 hover:bg-red-50'
                  : 'border-emerald-200 text-emerald-700 hover:bg-emerald-50'
              "
              @click="requestStatusChange(selectedTenant)"
            >
              {{
                selectedTenant.status_pagamento === 'ativo'
                  ? 'Bloquear acesso do escritório'
                  : 'Reativar escritório'
              }}
            </button>
          </div>
        </template>
      </aside>
    </div>

    <div
      v-if="tenantForAction"
      class="fixed inset-0 z-[60] flex items-center justify-center bg-slate-950/55 p-4"
    >
      <form
        class="w-full max-w-md rounded-xl border border-[var(--ct-border)] bg-white p-6 shadow-2xl"
        @submit.prevent="changeStatus"
      >
        <p
          class="text-xs font-semibold uppercase tracking-wider"
          :class="
            tenantForAction.status_pagamento === 'ativo' ? 'text-red-600' : 'text-emerald-700'
          "
        >
          Alteração administrativa
        </p>
        <h2 class="mt-2 text-lg font-semibold text-[var(--ct-ink)]">
          {{ tenantForAction.status_pagamento === 'ativo' ? 'Bloquear' : 'Reativar' }}
          {{ tenantForAction.razao_social }}
        </h2>
        <p class="mt-2 text-sm leading-6 text-[var(--ct-text-muted)]">
          A ação ficará registrada no histórico do escritório.
        </p>
        <label class="mt-5 block text-xs font-semibold text-[#52617a]"
          >Motivo da alteração<textarea
            v-model="actionReason"
            required
            maxlength="500"
            rows="4"
            class="mt-2 w-full resize-none rounded-xl border border-[var(--ct-border)] p-3 text-sm outline-none focus:border-[var(--ct-primary)]"
            placeholder="Descreva o motivo..."
          ></textarea>
        </label>
        <div class="mt-5 flex justify-end gap-3">
          <button
            type="button"
            class="rounded-lg px-4 py-2.5 text-sm font-semibold text-slate-500 hover:bg-slate-100"
            @click="tenantForAction = null"
          >
            Cancelar</button
          ><button
            type="submit"
            class="rounded-lg px-4 py-2.5 text-sm font-semibold text-white"
            :class="
              tenantForAction.status_pagamento === 'ativo'
                ? 'bg-red-600 hover:bg-red-700'
                : 'bg-emerald-600 hover:bg-emerald-700'
            "
            :disabled="isChangingStatus"
          >
            {{ isChangingStatus ? 'Salvando...' : 'Confirmar alteração' }}
          </button>
        </div>
      </form>
    </div>
  </AdminLayout>
</template>
