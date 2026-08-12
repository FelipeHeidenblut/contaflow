<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '../services/api'
import Layout from '../components/Layout.vue'
import { toast } from 'vue3-toastify'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import EmptyState from '../components/EmptyState.vue'
import { getApiErrorMessage } from '../utils/apiError'
import { useRoute } from 'vue-router'

const route = useRoute()

interface Cliente {
  id: string | number
  razao_social?: string
  nome?: string
}

interface Membro {
  id: string | number
  name: string
}

interface Obrigacao {
  id: string | number
  title: string
  description?: string
  status: string
  due_date: string
  client_id: string | number
  assigned_to?: string | number | null
  type?: 'custom' | 'receita_federal'
  grau_importancia?: string
  is_recurring?: boolean
  recurrence_day?: number | null
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

const filtroClienteId = ref('')
const filtroStatus = ref('')
const filtroResponsavel = ref('')
const searchQuery = ref('')

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

const obrigacoesFiltradas = computed(() => {
  let resultado = obrigacoes.value

  if (filtroClienteId.value) {
    resultado = resultado.filter((o) => String(o.client_id) === String(filtroClienteId.value))
  }

  if (filtroStatus.value) {
    resultado = resultado.filter((o) => o.status === filtroStatus.value)
  }

  if (filtroResponsavel.value) {
    resultado = resultado.filter((o) => String(o.assigned_to) === String(filtroResponsavel.value))
  }

  if (searchQuery.value) {
    const termoBusca = searchQuery.value.toLowerCase()
    resultado = resultado.filter(
      (o) =>
        o.title.toLowerCase().includes(termoBusca) ||
        (o.description && o.description.toLowerCase().includes(termoBusca)),
    )
  }

  const prioridadePeso: Record<string, number> = { Urgente: 4, Alta: 3, Média: 2, Baixa: 1 }

  return [...resultado].sort((a, b) => {
    const pesoA = prioridadePeso[a.grau_importancia || 'Média'] || 0
    const pesoB = prioridadePeso[b.grau_importancia || 'Média'] || 0

    if (pesoB !== pesoA) return pesoB - pesoA
    return a.due_date.localeCompare(b.due_date)
  })
})

const totalConcluidas = computed(
  () => obrigacoes.value.filter((o) => o.status === 'concluida').length,
)
const totalPendentes = computed(
  () => obrigacoes.value.filter((o) => o.status === 'pendente').length,
)
const totalAguardando = computed(
  () => obrigacoes.value.filter((o) => o.status === 'aguardando_cliente').length,
)
const totalAtrasadas = computed(
  () => obrigacoes.value.filter((o) => isAtrasada(o.due_date, o.status)).length,
)

const abrirDetalhes = (obrigacao: Obrigacao) => {
  obrigacaoSelecionada.value = obrigacao
  isDetalhesModalOpen.value = true
}

const fecharDetalhes = () => {
  isDetalhesModalOpen.value = false
  obrigacaoSelecionada.value = null
}

const abrirCadastro = () => {
  isEditando.value = false
  idSendoEditado.value = null
  formularioObrigacao.value = {
    title: '',
    description: '',
    client_id: '',
    assigned_to: '',
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
    const payload = { ...formularioObrigacao.value }
    if (!payload.assigned_to) payload.assigned_to = null as any

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
  } catch (error) {
    toast.error(getApiErrorMessage(error, 'Erro ao salvar a obrigação.'))
    console.error(error)
  }
}

const concluirTarefa = async (obrigacao: Obrigacao) => {
  try {
    const response = await api.patch(`/api/v1/obrigacoes/${obrigacao.id}/concluir`)
    const index = obrigacoes.value.findIndex((o) => o.id === obrigacao.id)

    if (index !== -1) obrigacoes.value[index] = response.data
    if (obrigacaoSelecionada.value?.id === obrigacao.id) obrigacaoSelecionada.value = response.data

    if (obrigacao.is_recurring) {
      toast.success('Obrigação concluída! A tarefa do próximo mês já foi criada automaticamente.')
      fetchData()
    } else {
      toast.success('Obrigação concluída!')
    }
  } catch (error) {
    toast.error(getApiErrorMessage(error, 'Erro ao concluir tarefa.'))
  }
}

const excluirTarefa = async () => {
  const id = taskToDelete.value
  if (id === null) return
  try {
    await api.delete(`/api/v1/obrigacoes/${id}`)
    obrigacoes.value = obrigacoes.value.filter((o) => o.id !== id)
    fecharDetalhes()
    toast.success('Tarefa excluída.')
    taskToDelete.value = null
  } catch (error) {
    toast.error(getApiErrorMessage(error, 'Erro ao excluir tarefa.'))
  }
}

const fetchData = async () => {
  isLoading.value = true
  try {
    const [obrigacoesRes, clientesRes, membrosRes] = await Promise.all([
      api.get('/api/v1/obrigacoes'),
      api.get('/api/v1/clientes'),
      api.get('/api/v1/membros'),
    ])

    obrigacoes.value = obrigacoesRes.data
    clientes.value = clientesRes.data
    membros.value = membrosRes.data
  } catch (error) {
    toast.error(getApiErrorMessage(error, 'Erro ao carregar os dados.'))
    console.error(error)
  } finally {
    isLoading.value = false
  }
}

const getNomeCliente = (clientId: string | number) => {
  const cliente = clientes.value.find((c) => String(c.id) === String(clientId))
  return cliente ? cliente.nome || cliente.razao_social || 'Nome indisponível' : 'Não vinculado'
}

const getNomeMembro = (membroId?: string | number | null) => {
  if (!membroId) return 'Não atribuído'
  const membro = membros.value.find((m) => String(m.id) === String(membroId))
  return membro ? membro.name : 'Desconhecido'
}

const getIniciaisMembro = (nome: string) => {
  if (!nome || nome === 'Não atribuído') return '?'

  const partes = nome
    .trim()
    .split(' ')
    .filter((p) => p)

  if (partes.length === 0) return '?'
  if (partes.length === 1) return (partes[0]?.charAt(0) || '?').toUpperCase()

  const primeiraLetra = partes[0]?.charAt(0) || ''
  const ultimaLetra = partes[partes.length - 1]?.charAt(0) || ''
  return (primeiraLetra + ultimaLetra).toUpperCase() || '?'
}

const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  const [year, month, day] = dateString.split('-')
  return `${day}/${month}/${year}`
}

const isAtrasada = (dateString: string, status: string) => {
  if (status === 'concluida' || !dateString) return false
  const today = new Date()
  const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
  return dateString < todayStr
}

const getStatusBadge = (status: string) => {
  const styles: Record<string, string> = {
    concluida: 'bg-emerald-100 text-emerald-700 border-emerald-200',
    em_andamento: 'bg-[var(--ct-primary-soft)] text-[var(--ct-primary)] border-[var(--ct-border)]',
    aguardando_cliente: 'bg-amber-100 text-amber-700 border-amber-200',
    pendente: 'bg-slate-100 text-slate-700 border-slate-200',
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

onMounted(async () => {
  await fetchData()
  if (route.query.novo === '1') abrirCadastro()
})
</script>

<template>
  <Layout title="Controle de Obrigações">
    <div class="ct-workspace space-y-4">
      <!-- topo -->
      <header
        class="ct-page-header flex flex-col gap-4 border-b border-[var(--ct-border)] pb-5 xl:flex-row xl:items-end xl:justify-between"
      >
        <div>
          <h1 class="ct-page-title text-2xl font-semibold tracking-tight text-[var(--ct-ink)]">
            Obrigações e tarefas
          </h1>
          <p class="ct-page-description mt-1 text-sm text-[var(--ct-text-muted)]">
            Gerencie prazos, responsáveis e pendências operacionais do escritório.
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

      <!-- kpis -->
      <section
        class="ct-summary-grid flex flex-wrap items-center gap-x-10 gap-y-4 border-b border-[var(--ct-border)] pb-5"
      >
        <div class="flex items-baseline gap-2">
          <p class="text-xs font-medium text-[var(--ct-text-muted)]">Pendentes</p>
          <p
            class="text-xl font-semibold tracking-tight text-[var(--ct-ink)] [font-variant-numeric:tabular-nums]"
          >
            {{ totalPendentes }}
          </p>
        </div>

        <div class="flex items-baseline gap-2">
          <p class="text-xs font-medium text-[var(--ct-text-muted)]">Em espera do cliente</p>
          <p
            class="text-xl font-semibold tracking-tight text-[var(--ct-ink)] [font-variant-numeric:tabular-nums]"
          >
            {{ totalAguardando }}
          </p>
        </div>

        <div class="flex items-baseline gap-2">
          <p class="text-xs font-medium text-[var(--ct-text-muted)]">Concluídas</p>
          <p
            class="text-xl font-semibold tracking-tight text-[var(--ct-ink)] [font-variant-numeric:tabular-nums]"
          >
            {{ totalConcluidas }}
          </p>
        </div>

        <div class="flex items-baseline gap-2">
          <p class="text-xs font-medium text-[var(--ct-text-muted)]">Atrasadas</p>
          <p
            class="text-xl font-semibold tracking-tight text-red-600 [font-variant-numeric:tabular-nums]"
          >
            {{ totalAtrasadas }}
          </p>
        </div>
      </section>

      <!-- filtros -->
      <section class="ct-filter-panel border-b border-[var(--ct-border)] pb-5">
        <div class="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
          <div class="grid w-full grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
            <div class="relative">
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
                class="w-full rounded-lg border border-[var(--ct-border)] bg-white py-2.5 pl-10 pr-4 text-sm text-[var(--ct-ink)] outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
              />
            </div>

            <select
              v-model="filtroClienteId"
              aria-label="Filtrar obrigações por cliente"
              class="w-full rounded-lg border border-[var(--ct-border)] bg-white px-4 py-2.5 text-sm text-[var(--ct-ink)] outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
            >
              <option value="">Todos os clientes</option>
              <option v-for="c in clientes" :key="c.id" :value="c.id">
                {{ c.nome || c.razao_social }}
              </option>
            </select>

            <select
              v-model="filtroResponsavel"
              aria-label="Filtrar obrigações por responsável"
              class="w-full rounded-lg border border-[var(--ct-border)] bg-white px-4 py-2.5 text-sm text-[var(--ct-ink)] outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
            >
              <option value="">Todos os responsáveis</option>
              <option v-for="m in membros" :key="m.id" :value="m.id">{{ m.name }}</option>
            </select>

            <select
              v-model="filtroStatus"
              aria-label="Filtrar obrigações por status"
              class="w-full rounded-lg border border-[var(--ct-border)] bg-white px-4 py-2.5 text-sm text-[var(--ct-ink)] outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
            >
              <option value="">Todos os status</option>
              <option value="pendente">Pendentes</option>
              <option value="em_andamento">Em andamento</option>
              <option value="aguardando_cliente">Aguard. cliente</option>
              <option value="concluida">Concluídas</option>
            </select>
          </div>

          <div class="text-xs text-[var(--ct-text-muted)]">
            {{ obrigacoesFiltradas.length }} resultado(s)
          </div>
        </div>
      </section>

      <!-- tabela -->
      <section
        class="ct-data-panel overflow-hidden rounded-xl border border-[var(--ct-border)] bg-white"
      >
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
                  <span :class="getStatusBadge(obrigacao.status).class">{{
                    getStatusBadge(obrigacao.status).label
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
                v-if="obrigacao.status !== 'concluida'"
                class="mt-3 text-xs font-semibold text-emerald-700"
                @click="concluirTarefa(obrigacao)"
              >
                Marcar como concluída
              </button>
            </article>
          </div>
          <table class="hidden min-w-full md:table">
            <thead class="border-b border-[var(--ct-border)] bg-slate-50/80">
              <tr>
                <th
                  class="px-6 py-4 text-left text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500"
                >
                  Tarefa
                </th>
                <th
                  class="px-6 py-4 text-left text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500"
                >
                  Cliente
                </th>
                <th
                  class="px-6 py-4 text-left text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500"
                >
                  Responsável
                </th>
                <th
                  class="px-6 py-4 text-left text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500"
                >
                  Prazo
                </th>
                <th
                  class="px-6 py-4 text-left text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500"
                >
                  Prioridade
                </th>
                <th
                  class="px-6 py-4 text-left text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500"
                >
                  Status
                </th>
                <th
                  class="px-6 py-4 text-right text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500"
                >
                  Ações
                </th>
              </tr>
            </thead>

            <tbody class="divide-y divide-[var(--ct-border)] bg-white">
              <tr
                v-for="obrigacao in obrigacoesFiltradas"
                :key="obrigacao.id"
                class="transition-colors hover:bg-slate-50/70"
              >
                <td class="px-6 py-4">
                  <button
                    @click="abrirDetalhes(obrigacao)"
                    class="flex max-w-sm items-start gap-3 text-left transition-colors hover:text-[var(--ct-primary)]"
                  >
                    <div
                      class="mt-0.5 flex h-9 w-9 items-center justify-center rounded-xl"
                      :class="
                        obrigacao.is_recurring
                          ? 'bg-[var(--ct-primary-soft)] text-[var(--ct-primary)]'
                          : 'bg-slate-100 text-slate-500'
                      "
                    >
                      <svg
                        v-if="obrigacao.is_recurring"
                        class="h-4 w-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                        />
                      </svg>
                      <svg
                        v-else
                        class="h-4 w-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2V9m-7-4h6m0 0v6m0-6L10 14"
                        />
                      </svg>
                    </div>

                    <div class="min-w-0">
                      <div class="flex items-center gap-2">
                        <p class="truncate text-sm font-semibold text-[var(--ct-ink)]">
                          {{ obrigacao.title }}
                        </p>
                        <span
                          v-if="obrigacao.is_recurring"
                          class="inline-flex rounded-full bg-[var(--ct-primary-soft)] px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.08em] text-[var(--ct-primary)]"
                        >
                          Recorrente
                        </span>
                      </div>

                      <p class="mt-1 truncate text-xs text-[var(--ct-text-muted)]">
                        {{ obrigacao.description || 'Sem descrição adicional.' }}
                      </p>
                    </div>
                  </button>
                </td>

                <td class="px-6 py-4 text-sm text-[var(--ct-ink)]">
                  {{ getNomeCliente(obrigacao.client_id) }}
                </td>

                <td class="px-6 py-4">
                  <div
                    class="flex items-center gap-2"
                    :title="getNomeMembro(obrigacao.assigned_to)"
                  >
                    <div
                      class="flex h-8 w-8 items-center justify-center rounded-full bg-[var(--ct-primary-soft)] text-[10px] font-semibold text-[var(--ct-primary)]"
                    >
                      {{ getIniciaisMembro(getNomeMembro(obrigacao.assigned_to)) }}
                    </div>
                    <span class="hidden text-xs text-[var(--ct-text-muted)] lg:block">
                      {{ getNomeMembro(obrigacao.assigned_to) }}
                    </span>
                  </div>
                </td>

                <td
                  class="px-6 py-4 text-sm"
                  :class="
                    isAtrasada(obrigacao.due_date, obrigacao.status)
                      ? 'font-semibold text-red-600'
                      : 'text-[var(--ct-ink)]'
                  "
                >
                  {{ formatDate(obrigacao.due_date) }}
                </td>

                <td class="px-6 py-4">
                  <span :class="getImportanciaBadge(obrigacao.grau_importancia).class">
                    {{ getImportanciaBadge(obrigacao.grau_importancia).label }}
                  </span>
                </td>

                <td class="px-6 py-4">
                  <span :class="getStatusBadge(obrigacao.status).class">
                    {{ getStatusBadge(obrigacao.status).label }}
                  </span>
                </td>

                <td class="px-6 py-4">
                  <div class="flex justify-end gap-2">
                    <button
                      v-if="obrigacao.status !== 'concluida'"
                      @click="concluirTarefa(obrigacao)"
                      class="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-700 transition-colors hover:bg-emerald-100"
                    >
                      Concluir
                    </button>

                    <button
                      @click="abrirDetalhes(obrigacao)"
                      class="rounded-lg border border-[var(--ct-border)] bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-50"
                    >
                      Detalhes
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
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
                  v-model="formularioObrigacao.assigned_to"
                  class="w-full rounded-xl border border-[var(--ct-border)] bg-white px-4 py-3 text-sm outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
                >
                  <option value="">Não atribuído</option>
                  <option v-for="m in membros" :key="m.id" :value="m.id">{{ m.name }}</option>
                </select>
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
                    Ao concluir, o sistema poderá gerar automaticamente a próxima competência.
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
              v-if="isEditando"
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
