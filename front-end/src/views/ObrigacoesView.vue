<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import api from '../services/api'
import Layout from '../components/Layout.vue'
import { toast } from 'vue3-toastify'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import EmptyState from '../components/EmptyState.vue'
import { getApiErrorMessage } from '../utils/apiError'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import CommentsPanel from '../components/CommentsPanel.vue'
import PaginationControls from '../components/PaginationControls.vue'
import { fetchAllPages, fetchPage } from '../services/pagination'
import ObrigacoesKanban from '../components/ObrigacoesKanban.vue'
import type { Obrigacao, TaskStatus } from '../types/obrigacao'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const canManageTasks = computed(() => ['admin', 'gerente'].includes(authStore.role))

interface Cliente {
  id: string | number
  razao_social?: string
  nome?: string
}

interface Membro {
  id: string | number
  name: string
}

const taskToDelete = ref<string | number | null>(null)

interface TemplateContabil {
  nome: string
  title: string
  description: string
  grau_importancia: string
  status?: string
}

const obrigacoes = ref<Obrigacao[]>([])
const clientes = ref<Cliente[]>([])
const membros = ref<Membro[]>([])
const isLoading = ref(true)
const currentPage = ref(1)
const totalPages = ref(0)
const totalResults = ref(0)
const pageSize = 20

const filtroClienteId = ref(typeof route.query.cliente === 'string' ? route.query.cliente : '')
const filtroStatus = ref('')
const statusFilters = [
  { value: '', label: 'Todas' },
  { value: 'atrasadas', label: 'Em atraso' },
  { value: 'pendente', label: 'Pendentes' },
  { value: 'em_andamento', label: 'Em andamento' },
  { value: 'aguardando_cliente', label: 'Aguardando cliente' },
  { value: 'concluida', label: 'Concluídas' },
  { value: 'arquivadas', label: 'Arquivadas' },
]

const filtroResponsavel = ref(
  typeof route.query.responsavel === 'string' ? route.query.responsavel : '',
)
const searchQuery = ref(typeof route.query.busca === 'string' ? route.query.busca : '')
watch(
  () => route.query.busca,
  (value) => {
    searchQuery.value = typeof value === 'string' ? value : ''
  },
)
watch(
  () => route.query.cliente,
  (value) => {
    filtroClienteId.value = typeof value === 'string' ? value : ''
  },
)
watch(
  () => route.query.responsavel,
  (value) => {
    filtroResponsavel.value = typeof value === 'string' ? value : ''
  },
)
const visualizacao = ref<'lista' | 'kanban'>('lista')
const kanbanRefreshKey = ref(0)
const isUpdatingStatus = ref(false)
const archivingTaskId = ref<string | number | null>(null)
const filtrosAplicados = ref<Record<string, string | number | boolean | undefined>>({
  search: searchQuery.value.trim() || undefined,
  client_id: filtroClienteId.value || undefined,
  assigned_to: filtroResponsavel.value || undefined,
})

const isDetalhesModalOpen = ref(false)
const obrigacaoSelecionada = ref<Obrigacao | null>(null)
const isCadastroModalOpen = ref(false)

const isEditando = ref(false)
const idSendoEditado = ref<string | number | null>(null)
const formularioObrigacao = ref({
  title: '',
  description: '',
  client_id: '' as string | number,
  assigned_to: '' as string | number | '',
  due_date: '',
  status: 'pendente',
  grau_importancia: 'Média',
  is_recurring: false,
  recurrence_day: null as number | null,
})

const templatesContabeis: TemplateContabil[] = [
  {
    nome: 'Apuração DAS (Simples Nacional)',
    title: 'Apuração DAS - Simples Nacional',
    description:
      'Verificar receitas do período, calcular tributos devidos e gerar guia de DAS para pagamento.',
    grau_importancia: 'Alta',
  },
  {
    nome: 'Folha de Pagamento Mensal',
    title: 'Folha de Pagamento',
    description: 'Conferir ponto, calcular salários, encargos sociais e gerar holerites.',
    grau_importancia: 'Alta',
  },
  {
    nome: 'SPED Fiscal',
    title: 'SPED Fiscal',
    description:
      'Validar livros fiscais, conferir notas fiscais de entrada/saída e gerar arquivo do SPED.',
    grau_importancia: 'Urgente',
  },
  {
    nome: 'DCTFWeb',
    title: 'DCTFWeb',
    description: 'Gerar e transmitir a DCTFWeb com as apurações do eSocial e EFD-Contribuições.',
    grau_importancia: 'Alta',
  },
  {
    nome: 'Solicitar documentos (aguardando cliente)',
    title: 'Aguardando Documentos do Cliente',
    description:
      'Solicitar e organizar documentos enviados pelo cliente para fechamento da competência.',
    grau_importancia: 'Média',
    status: 'aguardando_cliente',
  },
  {
    nome: '🏢 ECD (Escrituração Contábil)',
    title: 'ECD - Escrituração Contábil Digital',
    description: 'Conferir lançamentos contábeis e gerar arquivo da ECD para envio ao SPED.',
    grau_importancia: 'Urgente',
  },
]

const aplicarTemplate = (event: Event) => {
  const target = event.target as HTMLSelectElement
  const selectedIndex = parseInt(target.value)
  if (!isNaN(selectedIndex)) {
    const template = templatesContabeis[selectedIndex]
    if (template) {
      formularioObrigacao.value.title = template.title
      formularioObrigacao.value.description = template.description
      formularioObrigacao.value.grau_importancia = template.grau_importancia
      if (template.status) formularioObrigacao.value.status = template.status
    }
  }
}

const obrigacoesFiltradas = computed(() => obrigacoes.value)

const abrirDetalhes = (obrigacao: Obrigacao) => {
  obrigacaoSelecionada.value = obrigacao
  isDetalhesModalOpen.value = true
}

const fecharDetalhes = () => {
  isDetalhesModalOpen.value = false
  obrigacaoSelecionada.value = null
  if (route.query.tarefa) {
    const query = { ...route.query }
    delete query.tarefa
    void router.replace({ query })
  }
}

const abrirCadastro = () => {
  isEditando.value = false
  idSendoEditado.value = null
  formularioObrigacao.value = {
    title: '',
    description: '',
    client_id: '',
    assigned_to: canManageTasks.value ? '' : authStore.userId,
    due_date: '',
    status: 'pendente',
    grau_importancia: 'Média',
    is_recurring: false,
    recurrence_day: null,
  }
  isCadastroModalOpen.value = true
}

const abrirEdicao = (obrigacao: Obrigacao) => {
  if (obrigacao.type === 'receita_federal') {
    toast.info('Não é possível editar prazos federais fixos.')
    return
  }

  isEditando.value = true
  idSendoEditado.value = obrigacao.id
  formularioObrigacao.value = {
    title: obrigacao.title,
    description: obrigacao.description || '',
    client_id: obrigacao.client_id,
    assigned_to: obrigacao.assigned_to || '',
    due_date: obrigacao.due_date,
    status: obrigacao.status,
    grau_importancia: obrigacao.grau_importancia || 'Média',
    is_recurring: obrigacao.is_recurring || false,
    recurrence_day: obrigacao.recurrence_day || null,
  }
  fecharDetalhes()
  isCadastroModalOpen.value = true
}

const fecharCadastro = () => {
  isCadastroModalOpen.value = false
}

const salvarObrigacao = async () => {
  if (
    !formularioObrigacao.value.title ||
    !formularioObrigacao.value.client_id ||
    !formularioObrigacao.value.due_date
  ) {
    toast.warn('Por favor, preencha os campos obrigatórios (Título, Cliente e Prazo).')
    return
  }

  if (formularioObrigacao.value.is_recurring && !formularioObrigacao.value.recurrence_day) {
    toast.warn('Você marcou como tarefa recorrente. Escolha o dia do vencimento mensal.')
    return
  }

  try {
    const payload = {
      ...formularioObrigacao.value,
      assigned_to: formularioObrigacao.value.assigned_to || null,
    }

    if (isEditando.value && idSendoEditado.value) {
      const response = await api.put(`/api/v1/obrigacoes/${idSendoEditado.value}`, payload)
      const index = obrigacoes.value.findIndex((o) => o.id === idSendoEditado.value)
      if (index !== -1) obrigacoes.value[index] = response.data
      toast.success('Tarefa atualizada com sucesso!')
    } else {
      const response = await api.post('/api/v1/obrigacoes', payload)
      obrigacoes.value.push(response.data)
      toast.success('Nova obrigação criada com sucesso!')
    }

    fecharCadastro()
    await fetchData()
    kanbanRefreshKey.value += 1
  } catch (error) {
    toast.error(getApiErrorMessage(error, 'Erro ao salvar a obrigação.'))
    console.error(error)
  }
}

const concluirTarefa = async (obrigacao: Obrigacao) => {
  await alterarStatus(obrigacao, 'concluida')
}

const alterarStatus = async (obrigacao: Obrigacao, status: TaskStatus) => {
  if (
    isUpdatingStatus.value ||
    archivingTaskId.value !== null ||
    obrigacao.archived_at ||
    obrigacao.status === status
  )
    return
  isUpdatingStatus.value = true
  try {
    const response = await api.patch(`/api/v1/obrigacoes/${obrigacao.id}/status`, { status })
    const index = obrigacoes.value.findIndex((o) => o.id === obrigacao.id)

    if (index !== -1) obrigacoes.value[index] = response.data
    if (obrigacaoSelecionada.value?.id === obrigacao.id) obrigacaoSelecionada.value = response.data

    if (status === 'concluida' && obrigacao.is_recurring) {
      toast.success('Obrigação concluída! A próxima competência já está disponível.')
    } else if (status === 'concluida') {
      toast.success('Obrigação concluída!')
    } else {
      toast.success('Status atualizado!')
    }
    kanbanRefreshKey.value += 1
    await fetchData()
  } catch (error) {
    toast.error(getApiErrorMessage(error, 'Erro ao atualizar o status da tarefa.'))
  } finally {
    isUpdatingStatus.value = false
  }
}

const arquivarOuRestaurar = async (obrigacao: Obrigacao) => {
  if (archivingTaskId.value !== null || isUpdatingStatus.value || authStore.trialReadOnly) return
  archivingTaskId.value = obrigacao.id
  const restoring = Boolean(obrigacao.archived_at)
  try {
    await api.patch(`/api/v1/obrigacoes/${obrigacao.id}/${restoring ? 'restaurar' : 'arquivar'}`)
    if (obrigacaoSelecionada.value?.id === obrigacao.id) fecharDetalhes()
    kanbanRefreshKey.value += 1
    await fetchData()
    toast.success(
      restoring
        ? 'Tarefa restaurada para a lista de concluídas.'
        : 'Tarefa arquivada. Consulte na aba Arquivadas.',
    )
  } catch (error) {
    toast.error(
      getApiErrorMessage(
        error,
        restoring ? 'Não foi possível restaurar a tarefa.' : 'Não foi possível arquivar a tarefa.',
      ),
    )
  } finally {
    archivingTaskId.value = null
  }
}

const excluirTarefa = async () => {
  const id = taskToDelete.value
  if (id === null) return
  try {
    await api.delete(`/api/v1/obrigacoes/${id}`)
    if (obrigacoes.value.length === 1 && currentPage.value > 1) currentPage.value -= 1
    await fetchData()
    kanbanRefreshKey.value += 1
    fecharDetalhes()
    toast.success('Tarefa excluída.')
    taskToDelete.value = null
  } catch (error) {
    toast.error(getApiErrorMessage(error, 'Erro ao excluir tarefa.'))
  }
}

let fetchVersion = 0
const fetchData = async () => {
  const version = ++fetchVersion
  isLoading.value = true
  try {
    const taskPage = await fetchPage<Obrigacao>(
      '/api/v1/obrigacoes',
      currentPage.value,
      pageSize,
      filtrosAplicados.value,
    )
    if (version !== fetchVersion) return
    if (currentPage.value > Math.max(1, taskPage.pages)) {
      currentPage.value = Math.max(1, taskPage.pages)
      await fetchData()
      return
    }

    obrigacoes.value = taskPage.items
    totalPages.value = taskPage.pages
    totalResults.value = taskPage.total
  } catch (error) {
    if (version !== fetchVersion) return
    toast.error(getApiErrorMessage(error, 'Erro ao carregar os dados.'))
    console.error(error)
  } finally {
    if (version === fetchVersion) isLoading.value = false
  }
}

const fetchLookups = async () => {
  try {
    const [clientItems, memberItems] = await Promise.all([
      fetchAllPages<Cliente>('/api/v1/clientes'),
      fetchAllPages<Membro>('/api/v1/membros'),
    ])
    clientes.value = clientItems
    membros.value = memberItems
  } catch {
    toast.error('Erro ao carregar clientes e responsáveis.')
  }
}

const changePage = (page: number) => {
  currentPage.value = page
  fetchData()
}

let filterTimer: ReturnType<typeof setTimeout> | undefined
watch([searchQuery, filtroClienteId, filtroStatus, filtroResponsavel], () => {
  if (filterTimer) clearTimeout(filterTimer)
  filterTimer = setTimeout(() => {
    filtrosAplicados.value = {
      search: searchQuery.value.trim() || undefined,
      client_id: filtroClienteId.value || undefined,
      assigned_to: filtroResponsavel.value || undefined,
      task_status:
        filtroStatus.value && !['atrasadas', 'arquivadas'].includes(filtroStatus.value)
          ? filtroStatus.value
          : undefined,
      overdue: filtroStatus.value === 'atrasadas' || undefined,
      archived: filtroStatus.value === 'arquivadas',
    }
    currentPage.value = 1
    fetchData()
  }, 300)
})

onUnmounted(() => {
  if (filterTimer) clearTimeout(filterTimer)
  fetchVersion += 1
})

const getNomeCliente = (clientId: string | number) => {
  const cliente = clientes.value.find((c) => String(c.id) === String(clientId))
  return cliente ? cliente.nome || cliente.razao_social || 'Nome indisponível' : 'Não vinculado'
}

const getNomeMembro = (membroId?: string | number | null) => {
  if (!membroId) return 'Não atribuído'
  const membro = membros.value.find((m) => String(m.id) === String(membroId))
  return membro ? membro.name : 'Desconhecido'
}

const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  const [year, month, day] = dateString.split('-')
  return `${day}/${month}/${year}`
}

const isAtrasada = (dateString: string, status: string) => {
  if (status === 'concluida' || !dateString) return false
  return (
    dateString <
    new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Sao_Paulo' }).format(new Date())
  )
}

const getStatusBadge = (status: string) => {
  const styles: Record<string, string> = {
    concluida: 'bg-emerald-100 text-emerald-700 border-emerald-200',
    em_andamento: 'bg-[var(--ct-primary-soft)] text-[var(--ct-primary)] border-[var(--ct-border)]',
    aguardando_cliente: 'bg-amber-100 text-amber-700 border-amber-200',
    pendente: 'bg-amber-50 text-amber-600 border-amber-100',
  }

  const labels: Record<string, string> = {
    concluida: 'Concluída',
    em_andamento: 'Em andamento',
    aguardando_cliente: 'Aguard. cliente',
    pendente: 'Pendente',
  }

  return {
    class: `inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium ${styles[status] || styles['pendente']}`,
    label: labels[status] || 'Pendente',
  }
}

const getTaskBadge = (task: Obrigacao) =>
  task.archived_at
    ? {
        label: 'Arquivada',
        class:
          'inline-flex items-center rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-500',
      }
    : isAtrasada(task.due_date, task.status)
      ? {
          label: 'Em atraso',
          class:
            'inline-flex items-center rounded-full bg-rose-50 px-2.5 py-1 text-xs font-medium text-rose-500',
        }
      : getStatusBadge(task.status)

const dateToday = () =>
  new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Sao_Paulo' }).format(new Date())
const getListDate = (date: string) => (date === dateToday() ? 'Hoje' : formatDate(date))
const toggleCompleted = (task: Obrigacao, event: Event) => {
  const checkbox = event.target as HTMLInputElement
  const nextStatus = checkbox.checked ? 'concluida' : 'pendente'
  checkbox.checked = task.status === 'concluida'
  void alterarStatus(task, nextStatus)
}

const getImportanciaBadge = (grau?: string) => {
  const nivel = grau || 'Média'
  const styles: Record<string, string> = {
    Urgente: 'bg-red-50 text-red-700 border-red-200',
    Alta: 'bg-orange-50 text-orange-700 border-orange-200',
    Média: 'bg-[var(--ct-primary-soft)] text-[var(--ct-primary)] border-[var(--ct-border)]',
    Baixa: 'bg-slate-50 text-slate-700 border-slate-200',
  }

  return {
    class: `inline-flex items-center rounded-md border px-2 py-1 text-[11px] font-semibold uppercase tracking-[0.08em] ${styles[nivel] || styles['Média']}`,
    label: nivel,
  }
}

let detailVersion = 0
const openLinkedTask = async () => {
  const version = ++detailVersion
  const id = route.query.tarefa
  isDetalhesModalOpen.value = false
  obrigacaoSelecionada.value = null
  if (typeof id !== 'string' || !id) return
  try {
    const { data } = await api.get<Obrigacao>(`/api/v1/obrigacoes/${encodeURIComponent(id)}`)
    if (version === detailVersion) abrirDetalhes(data)
  } catch {
    if (version === detailVersion) toast.error('Obrigação indisponível ou sem permissão de acesso.')
  }
}
watch(() => route.query.tarefa, openLinkedTask)
onUnmounted(() => {
  detailVersion += 1
})
onMounted(async () => {
  await Promise.all([fetchData(), fetchLookups(), openLinkedTask()])
  if (route.query.novo === '1' && !route.query.tarefa) abrirCadastro()
})
</script>

<template>
  <Layout title="Controle de Obrigações">
    <div class="ct-obligations-workspace ct-workspace space-y-5">
      <!-- topo -->
      <header
        class="ct-page-header flex flex-col gap-4 border-b border-[var(--ct-border)] pb-5 xl:flex-row xl:items-end xl:justify-between"
      >
        <div>
          <h1 class="ct-page-title text-2xl font-semibold tracking-tight text-[var(--ct-ink)]">
            Obrigações e tarefas
          </h1>
          <p class="ct-page-description mt-1 text-sm text-[var(--ct-text-muted)]">
            Organize as entregas e acompanhe cada etapa.
          </p>
        </div>

        <button
          @click="abrirCadastro"
          class="ct-primary-action inline-flex w-full items-center justify-center gap-2 rounded-lg bg-[var(--ct-primary)] px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[var(--ct-primary-hover)] sm:w-auto"
        >
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 4v16m8-8H4"
            />
          </svg>
          <span>Nova obrigação</span>
        </button>
      </header>

      <section class="ct-obligations-panel rounded-xl border border-[#e7edf5] bg-white p-4">
        <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div role="group" aria-label="Filtrar obrigações por status" class="flex flex-wrap gap-2">
            <button
              v-for="filter in statusFilters"
              :key="filter.value"
              type="button"
              :aria-pressed="filtroStatus === filter.value"
              class="ct-obligations-tab rounded-md border px-3 py-2 text-xs transition-colors"
              :class="
                filtroStatus === filter.value
                  ? 'border-blue-200 bg-blue-50 text-blue-600'
                  : 'border-[#e1e9f5] bg-white text-slate-500 hover:bg-slate-50'
              "
              @click="filtroStatus = filter.value"
            >
              {{ filter.label }}
            </button>
          </div>
          <div
            role="group"
            aria-label="Visualização das obrigações"
            class="inline-flex rounded-lg border border-[var(--ct-border)] bg-slate-50 p-1"
          >
            <button
              type="button"
              :aria-pressed="visualizacao === 'lista'"
              class="rounded-md px-3 py-1.5 text-xs font-semibold"
              :class="
                visualizacao === 'lista'
                  ? 'bg-white text-[var(--ct-primary)] shadow-sm'
                  : 'text-slate-500'
              "
              @click="visualizacao = 'lista'"
            >
              Lista
            </button>
            <button
              type="button"
              :aria-pressed="visualizacao === 'kanban'"
              class="rounded-md px-3 py-1.5 text-xs font-semibold"
              :class="
                visualizacao === 'kanban'
                  ? 'bg-white text-[var(--ct-primary)] shadow-sm'
                  : 'text-slate-500'
              "
              @click="visualizacao = 'kanban'"
            >
              Kanban
            </button>
          </div>
        </div>
        <div class="mb-4 flex flex-wrap items-center gap-3">
          <div class="grid min-w-0 flex-1 gap-3 md:grid-cols-3">
            <div class="relative min-w-0">
              <svg
                class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M21 21l-4.35-4.35M10.5 18a7.5 7.5 0 100-15 7.5 7.5 0 000 15z"
                />
              </svg>
              <input
                v-model="searchQuery"
                aria-label="Buscar obrigações"
                type="text"
                placeholder="Buscar tarefa..."
                class="w-full rounded-lg border border-[var(--ct-border)] bg-white py-2 pl-10 pr-4 text-xs text-[var(--ct-ink)] outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
              />
            </div>

            <select
              v-model="filtroClienteId"
              aria-label="Filtrar obrigações por cliente"
              class="w-full rounded-lg border border-[var(--ct-border)] bg-white px-3 py-2 text-xs text-[var(--ct-ink)] outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
            >
              <option value="">Todos os clientes</option>
              <option v-for="c in clientes" :key="c.id" :value="c.id">
                {{ c.nome || c.razao_social }}
              </option>
            </select>

            <select
              v-model="filtroResponsavel"
              aria-label="Filtrar obrigações por responsável"
              class="w-full rounded-lg border border-[var(--ct-border)] bg-white px-3 py-2 text-xs text-[var(--ct-ink)] outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
            >
              <option value="">Todos os responsáveis</option>
              <option v-for="m in membros" :key="m.id" :value="m.id">{{ m.name }}</option>
            </select>
          </div>
          <p class="shrink-0 text-xs text-slate-500" role="status">
            {{ totalResults }} resultado(s)
          </p>
        </div>
        <ObrigacoesKanban
          v-if="visualizacao === 'kanban'"
          :filters="filtrosAplicados"
          :refresh-key="kanbanRefreshKey"
          :updating="isUpdatingStatus || archivingTaskId !== null"
          :read-only="authStore.trialReadOnly"
          :client-name="getNomeCliente"
          :member-name="getNomeMembro"
          :overdue="isAtrasada"
          :format-date="formatDate"
          @details="abrirDetalhes"
          @move="alterarStatus"
          @archive="arquivarOuRestaurar"
        />

        <!-- tabela -->
        <section v-else class="ct-obligations-list min-w-0">
          <div v-if="isLoading" class="space-y-3 p-6">
            <div class="h-12 animate-pulse rounded-xl bg-slate-100"></div>
            <div class="h-12 animate-pulse rounded-xl bg-slate-100"></div>
            <div class="h-12 animate-pulse rounded-xl bg-slate-100"></div>
            <div class="h-12 animate-pulse rounded-xl bg-slate-100"></div>
          </div>

          <EmptyState
            v-else-if="obrigacoesFiltradas.length === 0"
            title="Nenhuma obrigação encontrada"
            description="Ajuste os filtros ou crie uma nova obrigação para começar."
            action-label="Criar obrigação"
            @action="abrirCadastro"
          />

          <div v-else class="overflow-x-auto">
            <div class="divide-y divide-[var(--ct-border)] md:hidden">
              <article
                v-for="obrigacao in obrigacoesFiltradas"
                :key="`mobile-${obrigacao.id}`"
                class="p-4"
              >
                <button class="w-full text-left" @click="abrirDetalhes(obrigacao)">
                  <div class="flex items-start justify-between gap-3">
                    <div class="min-w-0">
                      <p class="truncate text-sm font-semibold text-[var(--ct-ink)]">
                        {{ obrigacao.title }}
                      </p>
                      <p class="mt-1 truncate text-xs text-[var(--ct-text-muted)]">
                        {{ getNomeCliente(obrigacao.client_id) }}
                      </p>
                    </div>
                    <span :class="getTaskBadge(obrigacao).class">{{
                      getTaskBadge(obrigacao).label
                    }}</span>
                  </div>
                  <div class="mt-3 flex items-center justify-between">
                    <span :class="getImportanciaBadge(obrigacao.grau_importancia).class">{{
                      getImportanciaBadge(obrigacao.grau_importancia).label
                    }}</span
                    ><span
                      class="text-xs"
                      :class="
                        isAtrasada(obrigacao.due_date, obrigacao.status)
                          ? 'font-semibold text-red-600'
                          : 'text-slate-500'
                      "
                      >{{ formatDate(obrigacao.due_date) }}</span
                    >
                  </div>
                </button>
                <button
                  v-if="
                    obrigacao.status !== 'concluida' &&
                    !authStore.trialReadOnly &&
                    obrigacao.type !== 'receita_federal'
                  "
                  :disabled="isUpdatingStatus"
                  class="mt-3 text-xs font-semibold text-emerald-700"
                  @click="concluirTarefa(obrigacao)"
                >
                  Marcar como concluída
                </button>
                <button
                  v-if="obrigacao.status === 'concluida' && !authStore.trialReadOnly"
                  type="button"
                  :disabled="isUpdatingStatus || archivingTaskId !== null"
                  class="mt-3 text-xs font-medium text-blue-600 disabled:opacity-50"
                  @click="arquivarOuRestaurar(obrigacao)"
                >
                  {{ obrigacao.archived_at ? 'Restaurar' : 'Arquivar' }}
                </button>
              </article>
            </div>
            <table class="ct-obligations-table hidden w-full min-w-[760px] text-left md:table">
              <thead class="bg-[#f5f7fa] text-slate-500">
                <tr>
                  <th class="w-8 rounded-l-md"><span class="sr-only">Concluir obrigação</span></th>
                  <th>Tarefa</th>
                  <th>Cliente</th>
                  <th>Responsável</th>
                  <th>Prazo</th>
                  <th>Status</th>
                  <th class="w-36 rounded-r-md"><span class="sr-only">Ações</span></th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="obrigacao in obrigacoesFiltradas"
                  :key="obrigacao.id"
                  class="border-b border-[#edf1f7] transition-colors hover:bg-slate-50/60"
                >
                  <td>
                    <input
                      type="checkbox"
                      :checked="obrigacao.status === 'concluida'"
                      :disabled="
                        isUpdatingStatus ||
                        archivingTaskId !== null ||
                        Boolean(obrigacao.archived_at) ||
                        authStore.trialReadOnly ||
                        obrigacao.type === 'receita_federal'
                      "
                      :aria-label="`${obrigacao.status === 'concluida' ? 'Reabrir' : 'Concluir'} ${obrigacao.title}`"
                      class="ct-obligation-checkbox"
                      @change="toggleCompleted(obrigacao, $event)"
                    />
                  </td>
                  <td>
                    <button
                      type="button"
                      @click="abrirDetalhes(obrigacao)"
                      class="flex items-center gap-2 text-left font-medium text-slate-800 hover:text-blue-600"
                      :title="obrigacao.description"
                    >
                      <span
                        :class="
                          obrigacao.status === 'concluida' ? 'text-slate-400 line-through' : ''
                        "
                        >{{ obrigacao.title }}</span
                      >
                      <span
                        v-if="obrigacao.is_recurring"
                        class="text-blue-500"
                        title="Obrigação recorrente"
                        aria-label="Obrigação recorrente"
                        >↻</span
                      >
                    </button>
                  </td>
                  <td class="text-slate-500">{{ getNomeCliente(obrigacao.client_id) }}</td>
                  <td class="text-slate-500">{{ getNomeMembro(obrigacao.assigned_to) }}</td>
                  <td
                    class="whitespace-nowrap"
                    :class="
                      isAtrasada(obrigacao.due_date, obrigacao.status) ||
                      (obrigacao.due_date === dateToday() && obrigacao.status !== 'concluida')
                        ? 'text-rose-500'
                        : 'text-slate-500'
                    "
                  >
                    {{ getListDate(obrigacao.due_date) }}
                  </td>
                  <td>
                    <span :class="getTaskBadge(obrigacao).class">{{
                      getTaskBadge(obrigacao).label
                    }}</span>
                  </td>
                  <td class="whitespace-nowrap">
                    <button
                      v-if="obrigacao.status === 'concluida' && !authStore.trialReadOnly"
                      type="button"
                      :aria-label="`${obrigacao.archived_at ? 'Restaurar' : 'Arquivar'} ${obrigacao.title}`"
                      :disabled="isUpdatingStatus || archivingTaskId !== null"
                      class="mr-2 rounded px-2 py-1 text-xs font-medium text-blue-600 hover:bg-blue-50 disabled:opacity-50"
                      @click="arquivarOuRestaurar(obrigacao)"
                    >
                      {{ obrigacao.archived_at ? 'Restaurar' : 'Arquivar' }}
                    </button>
                    <button
                      type="button"
                      @click="abrirDetalhes(obrigacao)"
                      :aria-label="`Ver detalhes e ações de ${obrigacao.title}`"
                      class="rounded px-2 py-1 text-lg leading-none text-slate-500 hover:bg-blue-50 hover:text-blue-600"
                    >
                      ⋮
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <PaginationControls
            :page="currentPage"
            :pages="totalPages"
            :total="totalResults"
            @change="changePage"
          />
        </section>
      </section>

      <!-- modal cadastro/edição -->
      <div
        v-if="isCadastroModalOpen"
        v-focus-trap
        role="dialog"
        aria-modal="true"
        aria-labelledby="task-modal-title"
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4 backdrop-blur-[2px]"
      >
        <div
          class="w-full max-w-2xl overflow-hidden rounded-xl border border-[var(--ct-border)] bg-white shadow-2xl"
        >
          <div
            class="flex items-center justify-between border-b border-[var(--ct-border)] bg-slate-50 px-6 py-5"
          >
            <h3
              id="task-modal-title"
              class="text-xl font-semibold tracking-tight text-[var(--ct-ink)]"
            >
              {{ isEditando ? 'Editar obrigação' : 'Nova obrigação' }}
            </h3>
            <button
              @click="fecharCadastro"
              aria-label="Fechar formulário de obrigação"
              class="rounded-lg p-1 text-slate-400 transition-colors hover:bg-white hover:text-slate-700"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          <div class="max-h-[80vh] space-y-5 overflow-y-auto p-6">
            <div v-if="!isEditando">
              <label
                class="mb-1.5 block text-xs font-semibold uppercase tracking-[0.08em] text-slate-500"
              >
                Modelo rápido
              </label>
              <select
                @change="aplicarTemplate($event)"
                class="w-full rounded-xl border border-[var(--ct-border)] bg-white px-4 py-3 text-sm outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
              >
                <option value="">Escolha um modelo...</option>
                <option v-for="(t, i) in templatesContabeis" :key="i" :value="i">
                  {{ t.nome }}
                </option>
              </select>
            </div>

            <div>
              <label
                class="mb-1.5 block text-xs font-semibold uppercase tracking-[0.08em] text-slate-500"
              >
                Título *
              </label>
              <input
                v-model="formularioObrigacao.title"
                type="text"
                class="w-full rounded-xl border border-[var(--ct-border)] px-4 py-3 text-sm outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
              />
            </div>

            <div>
              <label
                class="mb-1.5 block text-xs font-semibold uppercase tracking-[0.08em] text-slate-500"
              >
                Descrição
              </label>
              <textarea
                v-model="formularioObrigacao.description"
                rows="3"
                class="w-full rounded-xl border border-[var(--ct-border)] px-4 py-3 text-sm outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
              ></textarea>
            </div>

            <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div>
                <label
                  class="mb-1.5 block text-xs font-semibold uppercase tracking-[0.08em] text-slate-500"
                >
                  Cliente *
                </label>
                <select
                  v-model="formularioObrigacao.client_id"
                  class="w-full rounded-xl border border-[var(--ct-border)] bg-white px-4 py-3 text-sm outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
                >
                  <option value="">Selecione...</option>
                  <option v-for="c in clientes" :key="c.id" :value="c.id">
                    {{ c.nome || c.razao_social }}
                  </option>
                </select>
              </div>

              <div>
                <label
                  class="mb-1.5 block text-xs font-semibold uppercase tracking-[0.08em] text-slate-500"
                >
                  Atribuir para
                </label>
                <select
                  v-if="canManageTasks"
                  v-model="formularioObrigacao.assigned_to"
                  class="w-full rounded-xl border border-[var(--ct-border)] bg-white px-4 py-3 text-sm outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
                >
                  <option value="">Não atribuído</option>
                  <option v-for="m in membros" :key="m.id" :value="m.id">{{ m.name }}</option>
                </select>
                <div
                  v-else
                  class="w-full rounded-xl border border-[var(--ct-border)] bg-slate-50 px-4 py-3 text-sm font-medium text-[var(--ct-ink)]"
                >
                  {{ authStore.userName || 'Você' }}
                </div>
              </div>
            </div>

            <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
              <div>
                <label
                  class="mb-1.5 block text-xs font-semibold uppercase tracking-[0.08em] text-slate-500"
                >
                  Prazo *
                </label>
                <input
                  v-model="formularioObrigacao.due_date"
                  type="date"
                  class="w-full rounded-xl border border-[var(--ct-border)] px-4 py-3 text-sm outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
                />
              </div>

              <div>
                <label
                  class="mb-1.5 block text-xs font-semibold uppercase tracking-[0.08em] text-slate-500"
                >
                  Prioridade
                </label>
                <select
                  v-model="formularioObrigacao.grau_importancia"
                  class="w-full rounded-xl border border-[var(--ct-border)] bg-white px-4 py-3 text-sm outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
                >
                  <option value="Urgente">Urgente</option>
                  <option value="Alta">Alta</option>
                  <option value="Média">Média</option>
                  <option value="Baixa">Baixa</option>
                </select>
              </div>

              <div>
                <label
                  class="mb-1.5 block text-xs font-semibold uppercase tracking-[0.08em] text-slate-500"
                >
                  Status
                </label>
                <select
                  v-model="formularioObrigacao.status"
                  class="w-full rounded-xl border border-[var(--ct-border)] bg-white px-4 py-3 text-sm outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
                >
                  <option value="pendente">Pendente</option>
                  <option value="em_andamento">Em andamento</option>
                  <option value="aguardando_cliente">Aguardando cliente</option>
                  <option value="concluida">Concluída</option>
                </select>
              </div>
            </div>

            <div class="rounded-xl border border-[var(--ct-border)] bg-slate-50 p-4">
              <label class="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  v-model="formularioObrigacao.is_recurring"
                  class="h-4 w-4 rounded border-gray-300 text-[var(--ct-primary)] focus:ring-[var(--ct-primary)]"
                />
                <div>
                  <span class="block text-sm font-semibold text-[var(--ct-ink)]">
                    Tarefa recorrente mensal
                  </span>
                  <span class="block text-xs text-[var(--ct-text-muted)]">
                    Ao concluir, o sistema garante automaticamente a próxima competência, sem
                    duplicar.
                  </span>
                </div>
              </label>

              <div v-if="formularioObrigacao.is_recurring" class="mt-4">
                <label
                  class="mb-1.5 block text-xs font-semibold uppercase tracking-[0.08em] text-slate-500"
                >
                  Vence todo dia
                </label>
                <select
                  v-model="formularioObrigacao.recurrence_day"
                  class="w-full rounded-xl border border-[var(--ct-border)] bg-white px-4 py-3 text-sm outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
                >
                  <option :value="null" disabled>Selecione o dia</option>
                  <option v-for="n in 31" :key="n" :value="n">Dia {{ n }}</option>
                </select>
              </div>
            </div>
          </div>

          <div
            class="flex items-center justify-between border-t border-[var(--ct-border)] bg-slate-50 px-6 py-4"
          >
            <button
              v-if="isEditando && canManageTasks"
              @click="taskToDelete = idSendoEditado"
              class="text-sm font-semibold text-red-600 transition-colors hover:text-red-700"
            >
              Excluir
            </button>

            <div class="ml-auto flex gap-3">
              <button
                @click="fecharCadastro"
                class="rounded-xl px-4 py-2.5 text-sm font-medium text-slate-500 transition-colors hover:bg-white"
              >
                Cancelar
              </button>

              <button
                @click="salvarObrigacao"
                class="rounded-xl bg-[var(--ct-primary)] px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[var(--ct-primary-hover)]"
              >
                {{ isEditando ? 'Salvar alterações' : 'Criar obrigação' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- drawer detalhes -->
      <div
        v-if="isDetalhesModalOpen && obrigacaoSelecionada"
        v-focus-trap
        class="fixed inset-0 z-50 overflow-hidden"
        role="dialog"
        aria-modal="true"
      >
        <div class="absolute inset-0 bg-slate-950/50" @click="fecharDetalhes"></div>

        <div class="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-10">
          <div class="pointer-events-auto w-screen max-w-xl">
            <div class="flex h-full flex-col overflow-y-auto bg-white shadow-2xl">
              <div class="border-b border-[var(--ct-border)] bg-white px-6 py-5">
                <div class="flex items-start justify-between gap-4">
                  <div>
                    <div class="mb-2 flex flex-wrap items-center gap-2">
                      <span :class="getStatusBadge(obrigacaoSelecionada.status).class">
                        {{ getStatusBadge(obrigacaoSelecionada.status).label }}
                      </span>

                      <span
                        :class="getImportanciaBadge(obrigacaoSelecionada.grau_importancia).class"
                      >
                        {{ getImportanciaBadge(obrigacaoSelecionada.grau_importancia).label }}
                      </span>

                      <span
                        v-if="obrigacaoSelecionada.is_recurring"
                        class="inline-flex rounded-full bg-blue-50 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.08em] text-blue-700"
                      >
                        Recorrente
                      </span>
                    </div>

                    <h3 class="text-xl font-semibold tracking-tight text-[#101a38]">
                      {{ obrigacaoSelecionada.title }}
                    </h3>

                    <p v-if="obrigacaoSelecionada.archived_at" class="mt-2 text-xs text-slate-500">
                      Arquivada em
                      {{ new Date(obrigacaoSelecionada.archived_at).toLocaleDateString('pt-BR') }}.
                      Restaure para editar.
                    </p>
                    <p class="mt-1 text-sm text-[var(--ct-text-muted)]">
                      {{ obrigacaoSelecionada.description || 'Sem descrição adicional.' }}
                    </p>
                  </div>

                  <button
                    @click="fecharDetalhes"
                    aria-label="Fechar detalhes da obrigação"
                    class="rounded-lg p-1 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-700"
                  >
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  </button>
                </div>
              </div>

              <div class="flex-1 space-y-6 p-6">
                <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                  <div class="rounded-xl border border-[var(--ct-border)] bg-slate-50 p-4">
                    <span class="block text-xs text-[var(--ct-text-muted)]">Cliente</span>
                    <span class="mt-1 block text-sm font-semibold text-[var(--ct-ink)]">
                      {{ getNomeCliente(obrigacaoSelecionada.client_id) }}
                    </span>
                  </div>

                  <div class="rounded-xl border border-[var(--ct-border)] bg-slate-50 p-4">
                    <span class="block text-xs text-[var(--ct-text-muted)]">Responsável</span>
                    <span class="mt-1 block text-sm font-semibold text-[var(--ct-ink)]">
                      {{ getNomeMembro(obrigacaoSelecionada.assigned_to) }}
                    </span>
                  </div>

                  <div class="rounded-xl border border-[var(--ct-border)] bg-slate-50 p-4">
                    <span class="block text-xs text-[var(--ct-text-muted)]">Prazo</span>
                    <span
                      class="mt-1 block text-sm font-semibold"
                      :class="
                        isAtrasada(obrigacaoSelecionada.due_date, obrigacaoSelecionada.status)
                          ? 'text-red-600'
                          : 'text-[var(--ct-ink)]'
                      "
                    >
                      {{ formatDate(obrigacaoSelecionada.due_date) }}
                    </span>
                  </div>

                  <div
                    v-if="obrigacaoSelecionada.is_recurring"
                    class="rounded-xl border border-[var(--ct-border)] bg-slate-50 p-4"
                  >
                    <span class="block text-xs text-[var(--ct-text-muted)]">Recorrência</span>
                    <span class="mt-1 block text-sm font-semibold text-[var(--ct-ink)]">
                      Todo dia {{ obrigacaoSelecionada.recurrence_day || '-' }}
                    </span>
                  </div>
                </div>

                <div class="rounded-xl border border-[var(--ct-border)] bg-white p-4">
                  <h4 class="text-sm font-semibold text-[var(--ct-ink)]">Resumo</h4>
                  <p class="mt-2 text-sm leading-6 text-[var(--ct-text-muted)]">
                    {{
                      obrigacaoSelecionada.description ||
                      'Esta obrigação não possui descrição cadastrada.'
                    }}
                  </p>
                </div>

                <div>
                  <div class="mb-3">
                    <h4 class="text-sm font-semibold text-[var(--ct-ink)]">
                      Comentários da equipe
                    </h4>
                    <p class="mt-1 text-xs text-[var(--ct-text-muted)]">
                      Registre decisões e observações relacionadas a esta tarefa.
                    </p>
                  </div>
                  <CommentsPanel
                    :client-id="obrigacaoSelecionada.client_id"
                    :task-id="obrigacaoSelecionada.id"
                  />
                </div>
              </div>

              <div class="border-t border-[var(--ct-border)] bg-slate-50 px-6 py-4">
                <div class="flex flex-wrap justify-end gap-3">
                  <button
                    v-if="obrigacaoSelecionada.status !== 'concluida'"
                    @click="concluirTarefa(obrigacaoSelecionada)"
                    class="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-2.5 text-sm font-semibold text-emerald-700 transition-colors hover:bg-emerald-100"
                  >
                    Concluir
                  </button>

                  <button
                    v-if="obrigacaoSelecionada.status === 'concluida' && !authStore.trialReadOnly"
                    type="button"
                    :disabled="isUpdatingStatus || archivingTaskId !== null"
                    class="rounded-xl border border-blue-200 bg-blue-50 px-4 py-2.5 text-sm font-semibold text-blue-600 disabled:opacity-50"
                    @click="arquivarOuRestaurar(obrigacaoSelecionada)"
                  >
                    {{ obrigacaoSelecionada.archived_at ? 'Restaurar' : 'Arquivar' }}
                  </button>
                  <button
                    v-if="!obrigacaoSelecionada.archived_at"
                    @click="abrirEdicao(obrigacaoSelecionada)"
                    class="rounded-xl bg-[var(--ct-navy)] px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[var(--ct-primary-hover)]"
                  >
                    Editar
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <ConfirmDialog
        :open="taskToDelete !== null"
        title="Excluir obrigação"
        message="Deseja excluir esta obrigação permanentemente?"
        confirm-label="Excluir obrigação"
        @close="taskToDelete = null"
        @confirm="excluirTarefa"
      />
    </div>
  </Layout>
</template>
