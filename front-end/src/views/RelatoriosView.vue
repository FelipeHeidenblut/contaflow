<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { toast } from 'vue3-toastify'
import Layout from '../components/Layout.vue'
import api from '../services/api'
import { getApiErrorMessage } from '../utils/apiError'

interface Summary {
  total: number
  completed: number
  open: number
  overdue: number
  completion_rate: number
  clients_with_overdue: number
}

interface StatusItem {
  status: string
  label: string
  value: number
  percentage: number
}

interface TimelineItem {
  month: string
  label: string
  total: number
  completed: number
  overdue: number
}

interface RankingItem {
  id: string | null
  name: string
  total: number
  completed: number
  open: number
  overdue: number
  completion_rate: number
  share?: number
}

interface FilterOption {
  id: string
  name: string
}

interface ReportData {
  period: { start: string; end: string }
  summary: Summary
  status_distribution: StatusItem[]
  timeline: TimelineItem[]
  clients: RankingItem[]
  team: RankingItem[]
  filters: { clients: FilterOption[]; members: FilterOption[] }
  access: {
    plan: string
    paid: boolean
    advanced: boolean
    can_export: boolean
    max_report_days: number
  }
}

const paidPlans = new Set(['basico', 'profissional', 'business'])
const now = new Date()
const startDefault = new Date(now.getFullYear(), now.getMonth() - 5, 1)
const endDefault = new Date(now.getFullYear(), now.getMonth() + 1, 0)
const toIsoDate = (value: Date) =>
  `${value.getFullYear()}-${String(value.getMonth() + 1).padStart(2, '0')}-${String(value.getDate()).padStart(2, '0')}`

const startDate = ref(toIsoDate(startDefault))
const endDate = ref(toIsoDate(endDefault))
const clientId = ref('')
const memberId = ref('')
const taskStatus = ref('')
const currentPlan = ref('free')
const isCheckingAccess = ref(true)
const isLoading = ref(false)
const hasPaidAccess = ref(false)
const accessMessage = ref('Relatórios estão disponíveis nos planos pagos.')
const report = ref<ReportData | null>(null)
const hasAdvancedReports = computed(
  () => report.value?.access.advanced ?? ['profissional', 'business'].includes(currentPlan.value),
)
const canExportReports = computed(
  () => report.value?.access.can_export ?? ['profissional', 'business'].includes(currentPlan.value),
)

const applyDefaultPeriod = (plan: string) => {
  if (plan === 'basico') {
    const end = new Date()
    const start = new Date(end)
    start.setDate(start.getDate() - 91)
    startDate.value = toIsoDate(start)
    endDate.value = toIsoDate(end)
    return
  }
  startDate.value = toIsoDate(startDefault)
  endDate.value = toIsoDate(endDefault)
}

const summaryCards = computed(() => {
  const summary = report.value?.summary
  return [
    {
      label: 'Entregas no período',
      value: summary?.total ?? 0,
      helper: 'Com vencimento no intervalo',
      tone: 'blue',
    },
    {
      label: 'Concluídas',
      value: summary?.completed ?? 0,
      helper: `${summary?.completion_rate ?? 0}% de conclusão`,
      tone: 'green',
    },
    {
      label: 'Em aberto',
      value: summary?.open ?? 0,
      helper: 'Pendentes e em andamento',
      tone: 'cyan',
    },
    {
      label: 'Atrasadas',
      value: summary?.overdue ?? 0,
      helper: 'Em aberto após o prazo',
      tone: 'red',
    },
    {
      label: 'Clientes com atraso',
      value: summary?.clients_with_overdue ?? 0,
      helper: 'Exigem acompanhamento',
      tone: 'amber',
    },
  ]
})

const maxTimeline = computed(() =>
  Math.max(1, ...(report.value?.timeline.map((item) => item.total) || [1])),
)

const statusTone = (status: string) => {
  if (status === 'concluida') return 'bg-emerald-500'
  if (status === 'em_andamento') return 'bg-blue-500'
  if (status === 'aguardando_cliente') return 'bg-amber-500'
  return 'bg-slate-400'
}

const fetchReport = async () => {
  if (!hasPaidAccess.value) return
  if (!startDate.value || !endDate.value || startDate.value > endDate.value) {
    toast.warning('Informe um período válido.')
    return
  }

  isLoading.value = true
  try {
    const { data } = await api.get<ReportData>('/api/v1/relatorios', {
      params: {
        start_date: startDate.value,
        end_date: endDate.value,
        client_id: clientId.value || undefined,
        member_id: memberId.value || undefined,
        status: taskStatus.value || undefined,
      },
    })
    report.value = data
  } catch (error: unknown) {
    const responseStatus = (error as { response?: { status?: number } }).response?.status
    if (responseStatus === 402 || responseStatus === 403) {
      hasPaidAccess.value = false
      accessMessage.value = getApiErrorMessage(error, accessMessage.value)
    } else {
      toast.error(getApiErrorMessage(error, 'Não foi possível carregar o relatório.'))
    }
  } finally {
    isLoading.value = false
  }
}

const checkAccess = async () => {
  isCheckingAccess.value = true
  try {
    const { data } = await api.get('/api/v1/dashboard/')
    currentPlan.value = data.plano || 'free'
    applyDefaultPeriod(currentPlan.value)
    hasPaidAccess.value = paidPlans.has(data.plano) && data.status_pagamento === 'ativo'
    if (paidPlans.has(data.plano) && data.status_pagamento !== 'ativo') {
      accessMessage.value = 'Regularize a assinatura para acessar os relatórios.'
    }
    if (hasPaidAccess.value) await fetchReport()
  } catch (error: unknown) {
    toast.error(getApiErrorMessage(error, 'Não foi possível verificar o plano da conta.'))
  } finally {
    isCheckingAccess.value = false
  }
}

const resetFilters = () => {
  applyDefaultPeriod(currentPlan.value)
  clientId.value = ''
  memberId.value = ''
  taskStatus.value = ''
  fetchReport()
}

const csvCell = (value: string | number | null | undefined) => {
  let text = String(value ?? '')
  if (/^[=+\-@]/.test(text)) text = `'${text}`
  return `"${text.replaceAll('"', '""')}"`
}

const exportCsv = () => {
  if (!report.value || !canExportReports.value) {
    toast.info('A exportação CSV está disponível a partir do plano Profissional.')
    return
  }
  const rows: Array<Array<string | number | null | undefined>> = [
    ['Relatório operacional'],
    ['Período', `${report.value.period.start} a ${report.value.period.end}`],
    [],
    ['Resumo', 'Valor'],
    ['Entregas no período', report.value.summary.total],
    ['Concluídas', report.value.summary.completed],
    ['Em aberto', report.value.summary.open],
    ['Atrasadas', report.value.summary.overdue],
    ['Taxa de conclusão', `${report.value.summary.completion_rate}%`],
    [],
    ['Cliente', 'Total', 'Concluídas', 'Em aberto', 'Atrasadas', 'Conclusão'],
    ...report.value.clients.map((item) => [
      item.name,
      item.total,
      item.completed,
      item.open,
      item.overdue,
      `${item.completion_rate}%`,
    ]),
    [],
    ['Responsável', 'Total', 'Concluídas', 'Em aberto', 'Atrasadas', 'Conclusão'],
    ...report.value.team.map((item) => [
      item.name,
      item.total,
      item.completed,
      item.open,
      item.overdue,
      `${item.completion_rate}%`,
    ]),
  ]
  const csv = `\uFEFF${rows.map((row) => row.map(csvCell).join(';')).join('\n')}`
  const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }))
  const link = document.createElement('a')
  link.href = url
  link.download = `relatorio-${startDate.value}-${endDate.value}.csv`
  link.click()
  URL.revokeObjectURL(url)
}

onMounted(checkAccess)
</script>

<template>
  <Layout title="Relatórios">
    <div class="ct-workspace space-y-4">
      <header
        class="ct-page-header flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between"
      >
        <div>
          <div class="flex flex-wrap items-center gap-2">
            <h1 class="ct-page-title">Relatórios operacionais</h1>
            <span
              class="rounded-full bg-blue-50 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide text-blue-700"
              >{{
                isCheckingAccess
                  ? 'Relatórios'
                  : !hasPaidAccess
                    ? 'Recurso pago'
                    : hasAdvancedReports
                      ? 'Relatório avançado'
                      : 'Resumo Essencial'
              }}</span
            >
          </div>
          <p class="ct-page-description mt-1 text-sm">
            {{
              !hasPaidAccess
                ? 'Transforme entregas e pendências em uma visão clara da operação.'
                : hasAdvancedReports
                  ? 'Analise entregas, pendências, clientes e distribuição da equipe.'
                  : 'Acompanhe os principais indicadores das entregas dos últimos 3 meses.'
            }}
          </p>
        </div>
        <button
          v-if="hasPaidAccess && canExportReports"
          type="button"
          class="ct-secondary-action inline-flex items-center justify-center gap-2 border border-[var(--ct-border)] bg-white text-sm font-semibold text-[#26344f] hover:bg-slate-50 disabled:opacity-50"
          :disabled="!report || isLoading"
          @click="exportCsv"
        >
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-width="1.8" d="M12 3v12m0 0 4-4m-4 4-4-4M5 19h14" />
          </svg>
          Exportar CSV
        </button>
      </header>

      <div v-if="isCheckingAccess" class="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
        <div
          v-for="item in 5"
          :key="item"
          class="h-28 animate-pulse rounded-xl border border-[#e0e5ed] bg-white"
        ></div>
      </div>

      <section
        v-else-if="!hasPaidAccess"
        class="overflow-hidden rounded-xl border border-[#e0e5ed] bg-white shadow-sm"
      >
        <div class="grid items-center gap-8 p-6 lg:grid-cols-[0.8fr_1.2fr] lg:p-10">
          <div>
            <span
              class="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-blue-600"
            >
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.8"
                  d="M7 11V8a5 5 0 0 1 10 0v3m-11 0h12v10H6V11Z"
                />
              </svg>
            </span>
            <h2 class="mt-5 text-2xl font-semibold tracking-[-0.03em] text-[#101a38]">
              Transforme a operação em decisões claras
            </h2>
            <p class="mt-3 max-w-lg text-sm leading-6 text-[#6b7890]">{{ accessMessage }}</p>
            <ul class="mt-5 space-y-2 text-sm text-[#52617a]">
              <li>✓ Evolução das entregas por período</li>
              <li>✓ Clientes com mais pendências</li>
              <li>✓ Distribuição e desempenho da equipe</li>
              <li>✓ Exportação consolidada em CSV</li>
            </ul>
            <RouterLink to="/faturamento" class="ct-button-primary mt-6"
              >Conhecer planos</RouterLink
            >
          </div>
          <div class="grid gap-3 sm:grid-cols-2" aria-hidden="true">
            <div
              v-for="label in ['Entregas', 'Conclusão', 'Pendências', 'Equipe']"
              :key="label"
              class="rounded-xl border border-[#e0e5ed] bg-[#fbfcfe] p-4"
            >
              <p class="text-xs font-medium text-[#6b7890]">{{ label }}</p>
              <div class="mt-5 h-7 w-20 rounded bg-slate-200/70"></div>
              <div class="mt-4 h-2 rounded-full bg-slate-100">
                <div class="h-full w-2/3 rounded-full bg-blue-200"></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <template v-else>
        <section
          v-if="!hasAdvancedReports"
          class="flex flex-col justify-between gap-4 rounded-xl border border-blue-200 bg-blue-50/70 px-5 py-4 sm:flex-row sm:items-center"
        >
          <div>
            <p class="text-sm font-semibold text-[#17213d]">
              Seu plano inclui o resumo operacional de até 3 meses
            </p>
            <p class="mt-1 text-xs leading-5 text-[#52617a]">
              No Profissional, analise até 12 meses, filtre por cliente ou responsável, acompanhe a
              equipe e exporte tudo em CSV.
            </p>
          </div>
          <RouterLink
            :to="{ path: '/faturamento', query: { plano: 'profissional' } }"
            class="ct-button-primary shrink-0"
          >
            Conhecer Profissional
          </RouterLink>
        </section>

        <section class="ct-filter-panel">
          <form
            class="grid gap-3 md:grid-cols-2"
            :class="
              hasAdvancedReports
                ? 'xl:grid-cols-[1fr_1fr_1.3fr_1.3fr_1.2fr_auto]'
                : 'xl:grid-cols-[1fr_1fr_1.2fr_auto]'
            "
            @submit.prevent="fetchReport"
          >
            <label class="text-[11px] font-semibold text-[#52617a]"
              >Data inicial<input
                v-model="startDate"
                type="date"
                class="mt-1 w-full px-3 text-sm"
                required
            /></label>
            <label class="text-[11px] font-semibold text-[#52617a]"
              >Data final<input
                v-model="endDate"
                type="date"
                class="mt-1 w-full px-3 text-sm"
                required
            /></label>
            <label v-if="hasAdvancedReports" class="text-[11px] font-semibold text-[#52617a]"
              >Cliente<select v-model="clientId" class="mt-1 w-full px-3 text-sm">
                <option value="">Todos os clientes</option>
                <option
                  v-for="item in report?.filters.clients || []"
                  :key="item.id"
                  :value="item.id"
                >
                  {{ item.name }}
                </option>
              </select></label
            >
            <label v-if="hasAdvancedReports" class="text-[11px] font-semibold text-[#52617a]"
              >Responsável<select v-model="memberId" class="mt-1 w-full px-3 text-sm">
                <option value="">Toda a equipe</option>
                <option
                  v-for="item in report?.filters.members || []"
                  :key="item.id"
                  :value="item.id"
                >
                  {{ item.name }}
                </option>
              </select></label
            >
            <label class="text-[11px] font-semibold text-[#52617a]"
              >Status<select v-model="taskStatus" class="mt-1 w-full px-3 text-sm">
                <option value="">Todos os status</option>
                <option value="pendente">Pendentes</option>
                <option value="em_andamento">Em andamento</option>
                <option value="aguardando_cliente">Aguardando cliente</option>
                <option value="concluida">Concluídas</option>
              </select></label
            >
            <div class="flex items-end gap-2">
              <button class="ct-button-primary flex-1" type="submit" :disabled="isLoading">
                {{ isLoading ? 'Gerando...' : 'Aplicar' }}</button
              ><button
                class="rounded-lg px-3 py-3 text-xs font-semibold text-slate-500 hover:bg-slate-100"
                type="button"
                @click="resetFilters"
              >
                Limpar
              </button>
            </div>
          </form>
        </section>

        <section class="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
          <article
            v-for="card in summaryCards"
            :key="card.label"
            class="relative min-h-[108px] rounded-xl border border-[#e0e5ed] bg-white p-4 shadow-[0_2px_8px_rgba(15,23,42,0.035)]"
          >
            <span
              class="absolute right-4 top-4 h-2 w-2 rounded-full ring-[6px]"
              :class="{
                'bg-blue-500 ring-blue-50': card.tone === 'blue',
                'bg-emerald-500 ring-emerald-50': card.tone === 'green',
                'bg-cyan-500 ring-cyan-50': card.tone === 'cyan',
                'bg-red-500 ring-red-50': card.tone === 'red',
                'bg-amber-500 ring-amber-50': card.tone === 'amber',
              }"
            ></span>
            <p class="text-xs font-medium text-[#52617a]">{{ card.label }}</p>
            <p
              class="mt-3 text-[26px] font-semibold leading-none tracking-[-0.03em] text-[#101a38]"
            >
              {{ isLoading ? '—' : card.value }}
            </p>
            <p class="mt-3 text-[10px] text-[#8190a8]">{{ card.helper }}</p>
          </article>
        </section>

        <div class="grid gap-4 xl:grid-cols-12">
          <section
            class="ct-data-panel rounded-xl border border-[#e0e5ed] bg-white p-4 xl:col-span-8"
          >
            <div>
              <h2 class="text-sm font-semibold text-[#17213d]">Evolução das entregas</h2>
              <p class="mt-1 text-[11px] text-[#8190a8]">
                Obrigações agrupadas pelo mês de vencimento.
              </p>
            </div>
            <div
              v-if="report?.timeline.length"
              class="mt-6 flex h-52 items-end gap-3 overflow-x-auto border-b border-[#edf0f5] px-2 pb-6"
            >
              <div
                v-for="item in report.timeline"
                :key="item.month"
                class="flex h-full min-w-[76px] flex-1 flex-col justify-end text-center"
              >
                <div class="mb-2 text-[10px] font-semibold text-[#52617a]">
                  {{ item.completed }}/{{ item.total }}
                </div>
                <div
                  class="mx-auto flex w-10 flex-col justify-end overflow-hidden rounded-t-md bg-blue-100"
                  :style="{ height: `${Math.max(8, (item.total / maxTimeline) * 130)}px` }"
                >
                  <div
                    class="w-full bg-emerald-500"
                    :style="{ height: `${item.total ? (item.completed / item.total) * 100 : 0}%` }"
                  ></div>
                </div>
                <p class="mt-2 text-[10px] text-[#8190a8]">{{ item.label }}</p>
              </div>
            </div>
            <p v-else class="py-20 text-center text-sm text-[#8190a8]">Sem dados no período.</p>
          </section>

          <section
            class="ct-data-panel rounded-xl border border-[#e0e5ed] bg-white p-4 xl:col-span-4"
          >
            <h2 class="text-sm font-semibold text-[#17213d]">Distribuição por status</h2>
            <div class="mt-5 space-y-5">
              <div v-for="item in report?.status_distribution || []" :key="item.status">
                <div class="mb-1.5 flex items-center justify-between text-[11px]">
                  <span class="font-medium text-[#52617a]">{{ item.label }}</span
                  ><span class="font-semibold text-[#26344f]"
                    >{{ item.value }} · {{ item.percentage }}%</span
                  >
                </div>
                <div class="h-2 overflow-hidden rounded-full bg-slate-100">
                  <div
                    class="h-full rounded-full"
                    :class="statusTone(item.status)"
                    :style="{ width: `${item.percentage}%` }"
                  ></div>
                </div>
              </div>
            </div>
          </section>

          <section
            v-if="hasAdvancedReports"
            class="ct-data-panel overflow-hidden rounded-xl border border-[#e0e5ed] bg-white xl:col-span-7"
          >
            <div class="border-b border-[#edf0f5] px-4 py-3.5">
              <h2 class="text-sm font-semibold text-[#17213d]">Desempenho por cliente</h2>
            </div>
            <div class="overflow-x-auto">
              <table class="min-w-[620px] w-full">
                <thead>
                  <tr>
                    <th class="px-4 py-3 text-left">Cliente</th>
                    <th class="px-4 py-3 text-center">Total</th>
                    <th class="px-4 py-3 text-center">Concluídas</th>
                    <th class="px-4 py-3 text-center">Em aberto</th>
                    <th class="px-4 py-3 text-center">Atrasadas</th>
                    <th class="px-4 py-3 text-right">Conclusão</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-[#edf0f5]">
                  <tr
                    v-for="item in report?.clients.slice(0, 10) || []"
                    :key="item.id ?? item.name"
                  >
                    <td class="px-4 py-3 text-xs font-semibold text-[#26344f]">{{ item.name }}</td>
                    <td class="px-4 py-3 text-center text-xs text-[#52617a]">{{ item.total }}</td>
                    <td class="px-4 py-3 text-center text-xs text-emerald-600">
                      {{ item.completed }}
                    </td>
                    <td class="px-4 py-3 text-center text-xs text-[#52617a]">{{ item.open }}</td>
                    <td
                      class="px-4 py-3 text-center text-xs"
                      :class="item.overdue ? 'font-semibold text-red-600' : 'text-[#8190a8]'"
                    >
                      {{ item.overdue }}
                    </td>
                    <td class="px-4 py-3 text-right text-xs font-semibold text-[#26344f]">
                      {{ item.completion_rate }}%
                    </td>
                  </tr>
                </tbody>
              </table>
              <p v-if="!report?.clients.length" class="py-12 text-center text-xs text-[#8190a8]">
                Nenhum cliente com entregas no período.
              </p>
            </div>
          </section>

          <section
            v-if="hasAdvancedReports"
            class="ct-data-panel overflow-hidden rounded-xl border border-[#e0e5ed] bg-white xl:col-span-5"
          >
            <div class="border-b border-[#edf0f5] px-4 py-3.5">
              <h2 class="text-sm font-semibold text-[#17213d]">Distribuição da equipe</h2>
            </div>
            <div class="divide-y divide-[#edf0f5] px-4">
              <div v-for="item in report?.team || []" :key="item.id || 'unassigned'" class="py-3">
                <div class="flex items-center justify-between gap-3">
                  <div class="min-w-0">
                    <p class="truncate text-xs font-semibold text-[#26344f]">{{ item.name }}</p>
                    <p class="mt-0.5 text-[10px] text-[#8190a8]">
                      {{ item.completed }} concluídas · {{ item.overdue }} atrasadas
                    </p>
                  </div>
                  <span class="text-xs font-semibold text-[#52617a]">{{ item.total }}</span>
                </div>
                <div class="mt-2 h-1.5 overflow-hidden rounded-full bg-slate-100">
                  <div
                    class="h-full rounded-full bg-blue-500"
                    :style="{ width: `${Math.max(3, item.share || 0)}%` }"
                  ></div>
                </div>
              </div>
              <p v-if="!report?.team.length" class="py-12 text-center text-xs text-[#8190a8]">
                Nenhuma tarefa distribuída no período.
              </p>
            </div>
          </section>
        </div>
      </template>
    </div>
  </Layout>
</template>
