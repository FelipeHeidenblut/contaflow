<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '../services/api'
import Layout from '../components/Layout.vue'
import { toast } from 'vue3-toastify'
import { vMaska } from 'maska/vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const clients = ref<any[]>([])
const isLoading = ref(true)

const isModalOpen = ref(false)
const isSubmitting = ref(false)

const searchQuery = ref('')
const filtroNatureza = ref('Todos')

const newClient = ref({
  tipo_pessoa: 'PJ',
  razao_social: '',
  cnpj: '',
  nome: '',
  cpf: '',
  regime_tributario: 'Simples Nacional',
  natureza_operacao: 'Serviços',
})

const formErrors = ref({
  razao_social: '',
  cnpj: '',
  nome: '',
  cpf: '',
})

const isDossierOpen = ref(false)
const selectedClient = ref<any>(null)
const clientTasks = ref<any[]>([])
const clientDocuments = ref<any[]>([])
const isLoadingDossier = ref(false)
const activeTab = ref('info')

const isImportModalOpen = ref(false)
const isUploadingCsv = ref(false)
const csvFile = ref<File | null>(null)

const abrirDossier = async (client: any) => {
  selectedClient.value = client
  activeTab.value = 'info'
  isDossierOpen.value = true
  isLoadingDossier.value = true

  try {
    const [tasksRes, docsRes] = await Promise.all([
      api.get('/api/v1/obrigacoes'),
      api.get('/api/v1/documentos'),
    ])

    clientTasks.value = tasksRes.data
      .filter((t: any) => t.client_id === client.id)
      .sort((a: any, b: any) => new Date(b.due_date).getTime() - new Date(a.due_date).getTime())
      .slice(0, 5)

    clientDocuments.value = docsRes.data
      .filter((d: any) => d.client_id === client.id)
      .sort((a: any, b: any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 5)
  } catch (error) {
    toast.error('Erro ao carregar o dossiê do cliente.')
  } finally {
    isLoadingDossier.value = false
  }
}

const formatDocDate = (dateString: string) => {
  if (!dateString) return '-'
  const [year, month, day] = dateString.split('-')
  return `${day}/${month}/${year}`
}

const getStatusColor = (status: string) => {
  if (status === 'concluida') return 'bg-emerald-100 text-emerald-700'
  if (status === 'em_andamento') return 'bg-blue-100 text-blue-700'
  if (status === 'aguardando_cliente') return 'bg-amber-100 text-amber-700'
  return 'bg-slate-100 text-slate-600'
}

const baixarDocDossier = async (docId: string, nomeArquivo: string) => {
  try {
    const response = await api.get(`/api/v1/documentos/${docId}/download`, {
      responseType: 'blob',
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', nomeArquivo)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    toast.error('Erro ao baixar arquivo.')
  }
}

const clientsFiltrados = computed(() => {
  let listaFiltrada = clients.value

  if (filtroNatureza.value !== 'Todos') {
    listaFiltrada = listaFiltrada.filter(
      (client) => client.natureza_operacao === filtroNatureza.value,
    )
  }

  const termo = searchQuery.value.trim().toLowerCase()
  if (!termo) return listaFiltrada

  return listaFiltrada.filter((client) => {
    const nome = (client.nome || '').toLowerCase()
    const razaoSocial = (client.razao_social || '').toLowerCase()
    const cnpj = (client.cnpj || '').replace(/\D/g, '')
    const cpf = (client.cpf || '').replace(/\D/g, '')
    const termoLimpo = termo.replace(/\D/g, '')

    return (
      nome.includes(termo) ||
      razaoSocial.includes(termo) ||
      (termoLimpo && cnpj.includes(termoLimpo)) ||
      (termoLimpo && cpf.includes(termoLimpo))
    )
  })
})

const totalPJ = computed(() => clients.value.filter((c) => !!c.razao_social).length)
const totalPF = computed(() => clients.value.filter((c) => !c.razao_social).length)
const totalServicos = computed(
  () => clients.value.filter((c) => c.natureza_operacao === 'Serviços').length,
)

const setTipoPessoa = (tipo: string) => {
  newClient.value.tipo_pessoa = tipo
  if (tipo === 'PJ') {
    newClient.value.nome = ''
    newClient.value.cpf = ''
  } else {
    newClient.value.razao_social = ''
    newClient.value.cnpj = ''
  }
  formErrors.value = { razao_social: '', cnpj: '', nome: '', cpf: '' }
}

const fetchClients = async () => {
  isLoading.value = true
  try {
    const response = await api.get('/api/v1/clientes')
    clients.value = response.data
  } catch (error) {
    toast.error('Erro ao carregar a lista de clientes.')
  } finally {
    isLoading.value = false
  }
}

const validateForm = () => {
  let isValid = true
  formErrors.value = { razao_social: '', cnpj: '', nome: '', cpf: '' }

  if (newClient.value.tipo_pessoa === 'PJ') {
    if (!newClient.value.razao_social) {
      formErrors.value.razao_social = 'A razão social é obrigatória.'
      isValid = false
    }
    const cnpjClean = newClient.value.cnpj.replace(/[^a-zA-Z0-9]/g, '')
    if (cnpjClean.length < 14) {
      formErrors.value.cnpj = 'CNPJ inválido.'
      isValid = false
    }
  } else {
    if (!newClient.value.nome) {
      formErrors.value.nome = 'O nome completo é obrigatório.'
      isValid = false
    }
    const cpfClean = newClient.value.cpf.replace(/\D/g, '')
    if (cpfClean.length < 11) {
      formErrors.value.cpf = 'CPF inválido.'
      isValid = false
    }
  }

  return isValid
}

const handleCreateClient = async () => {
  if (!validateForm()) {
    toast.warning('Por favor, corrija os erros no formulário.')
    return
  }

  isSubmitting.value = true
  try {
    const response = await api.post('/api/v1/clientes', newClient.value)
    clients.value.unshift(response.data)

    newClient.value = {
      tipo_pessoa: 'PJ',
      razao_social: '',
      cnpj: '',
      nome: '',
      cpf: '',
      regime_tributario: 'Simples Nacional',
      natureza_operacao: 'Serviços',
    }

    isModalOpen.value = false
    toast.success('Cliente cadastrado com sucesso!')
  } catch (error: any) {
    const detail = error.response?.data?.detail || 'Erro ao cadastrar o cliente.'
    toast.error(detail)
  } finally {
    isSubmitting.value = false
  }
}

const handleDesativar = async (clientId: string) => {
  if (
    !window.confirm(
      'Tem certeza que deseja arquivar este cliente? Ele não aparecerá mais na listagem principal.',
    )
  ) {
    return
  }

  try {
    await api.patch(`/api/v1/clientes/${clientId}/desativar`)
    clients.value = clients.value.filter((c) => c.id !== clientId)
    toast.success('Cliente arquivado com sucesso.')
  } catch (error) {
    toast.error('Erro ao arquivar o cliente.')
  }
}

const handleCsvChange = (event: any) => {
  const file = event.target.files[0]
  if (file && file.name.endsWith('.csv')) {
    csvFile.value = file
  } else {
    toast.error('Por favor, selecione apenas arquivos .csv')
    event.target.value = ''
    csvFile.value = null
  }
}

const handleUploadCsv = async () => {
  if (!csvFile.value) return

  isUploadingCsv.value = true
  try {
    const formData = new FormData()
    formData.append('file', csvFile.value)

    const response = await api.post('/api/v1/clientes/importar-csv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })

    const { importados, erros } = response.data

    if (importados > 0) {
      toast.success(`${importados} clientes importados com sucesso!`)
      fetchClients()
    }

    if (erros > 0) {
      toast.warning(`${erros} linhas ignoradas por dados incompletos.`)
    }

    isImportModalOpen.value = false
    csvFile.value = null
  } catch (error: any) {
    const detail = error.response?.data?.detail || 'Erro ao processar arquivo CSV.'
    toast.error(detail)
  } finally {
    isUploadingCsv.value = false
  }
}

const baixarTemplate = () => {
  const cabecalhos = 'TIPO (PF/PJ);NOME_OU_RAZAO;CPF_OU_CNPJ;REGIME_TRIBUTARIO;NATUREZA_OPERACAO\n'
  const exemplo1 = 'PJ;Transportes LTDA;12.345.678/0001-90;Simples Nacional;Comércio\n'
  const exemplo2 = 'PJ;Contabilidade XYZ;12.345.678/0001-91;Lucro Presumido;Serviços\n'
  const exemplo3 = 'PF;João da Silva;123.456.789-00;MEI;Serviços\n'

  const blob = new Blob([cabecalhos + exemplo1 + exemplo2 + exemplo3], {
    type: 'text/csv;charset=utf-8;',
  })

  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.setAttribute('href', url)
  link.setAttribute('download', 'template_clientes.csv')
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

onMounted(() => {
  fetchClients()
})
</script>

<template>
  <Layout title="Gerenciar Clientes">
    <div class="relative space-y-6">
      <!-- topo -->
      <div class="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
        <div>
          <h2 class="text-2xl font-semibold tracking-tight text-[var(--ct-ink)]">
            Carteira de clientes
          </h2>
          <p class="mt-1 text-sm text-[var(--ct-text-muted)]">
            Busque, filtre, cadastre e consulte o dossiê de cada cliente.
          </p>
        </div>

        <div class="flex w-full flex-col gap-3 sm:flex-row xl:w-auto">
          <button
            @click="isImportModalOpen = true"
            class="inline-flex w-full items-center justify-center gap-2 rounded-xl border border-[var(--ct-border)] bg-white px-4 py-2.5 text-sm font-medium text-[var(--ct-ink)] shadow-sm transition-colors hover:bg-slate-50 sm:w-auto"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
            </svg>
            <span>Importar CSV</span>
          </button>

          <button
            @click="isModalOpen = true"
            class="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-[var(--ct-primary)] px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-[var(--ct-primary-hover)] sm:w-auto"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
            <span>Novo cliente</span>
          </button>
        </div>
      </div>

      <!-- cards -->
      <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div class="rounded-xl border border-[var(--ct-border)] bg-white p-4 shadow-sm">
          <p class="text-xs font-medium text-[var(--ct-text-muted)]">Clientes ativos</p>
          <p class="mt-2 text-3xl font-semibold tracking-tight text-[var(--ct-ink)] [font-variant-numeric:tabular-nums]">
            {{ clients.length }}
          </p>
        </div>

        <div class="rounded-xl border border-[var(--ct-border)] bg-white p-4 shadow-sm">
          <p class="text-xs font-medium text-[var(--ct-text-muted)]">Pessoa jurídica</p>
          <p class="mt-2 text-3xl font-semibold tracking-tight text-[var(--ct-ink)] [font-variant-numeric:tabular-nums]">
            {{ totalPJ }}
          </p>
        </div>

        <div class="rounded-xl border border-[var(--ct-border)] bg-white p-4 shadow-sm">
          <p class="text-xs font-medium text-[var(--ct-text-muted)]">Pessoa física</p>
          <p class="mt-2 text-3xl font-semibold tracking-tight text-[var(--ct-ink)] [font-variant-numeric:tabular-nums]">
            {{ totalPF }}
          </p>
        </div>
      </div>

      <!-- filtros -->
      <div class="rounded-2xl border border-[var(--ct-border)] bg-white p-4 shadow-sm">
        <div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div class="flex w-full flex-col gap-3 sm:flex-row lg:max-w-2xl">
            <div class="relative w-full sm:flex-1">
              <svg
                class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35M10.5 18a7.5 7.5 0 100-15 7.5 7.5 0 000 15z"/>
              </svg>

              <input
                v-model="searchQuery"
                type="text"
                placeholder="Buscar por nome, razão social, CPF ou CNPJ..."
                class="w-full rounded-xl border border-[var(--ct-border)] bg-white py-2.5 pl-10 pr-4 text-sm text-[var(--ct-ink)] outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
              />
            </div>

            <select
              v-model="filtroNatureza"
              class="w-full rounded-xl border border-[var(--ct-border)] bg-white px-4 py-2.5 text-sm text-[var(--ct-ink)] outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10 sm:w-56"
            >
              <option value="Todos">Todas as naturezas</option>
              <option value="Comércio">Comércio</option>
              <option value="Serviços">Serviços</option>
              <option value="Indústria">Indústria</option>
            </select>
          </div>

          <div class="text-xs text-[var(--ct-text-muted)]">
            {{ clientsFiltrados.length }} resultado(s)
          </div>
        </div>
      </div>

      <!-- tabela -->
      <div class="overflow-hidden rounded-2xl border border-[var(--ct-border)] bg-white shadow-sm">
        <div v-if="isLoading" class="space-y-3 p-6">
          <div class="h-12 animate-pulse rounded-xl bg-slate-100"></div>
          <div class="h-12 animate-pulse rounded-xl bg-slate-100"></div>
          <div class="h-12 animate-pulse rounded-xl bg-slate-100"></div>
          <div class="h-12 animate-pulse rounded-xl bg-slate-100"></div>
        </div>

        <div v-else-if="clients.length === 0" class="p-12 text-center">
          <p class="text-sm font-medium text-[var(--ct-ink)]">Nenhum cliente ativo cadastrado.</p>
          <p class="mt-1 text-sm text-[var(--ct-text-muted)]">
            Cadastre o primeiro cliente para começar a montar sua carteira.
          </p>
        </div>

        <div v-else-if="clientsFiltrados.length === 0" class="p-12 text-center">
          <p class="text-sm font-medium text-[var(--ct-ink)]">Nenhum cliente encontrado.</p>
          <p class="mt-1 text-sm text-[var(--ct-text-muted)]">
            Tente ajustar a busca ou remover filtros.
          </p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="min-w-full">
            <thead class="border-b border-[var(--ct-border)] bg-slate-50/80">
              <tr>
                <th class="px-6 py-4 text-left text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500">
                  Cliente
                </th>
                <th class="px-6 py-4 text-left text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500">
                  Documento
                </th>
                <th class="px-6 py-4 text-left text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500">
                  Regime
                </th>
                <th class="px-6 py-4 text-left text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500">
                  Natureza
                </th>
                <th class="px-6 py-4 text-right text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500">
                  Ações
                </th>
              </tr>
            </thead>

            <tbody class="divide-y divide-[var(--ct-border)] bg-white">
              <tr
                v-for="client in clientsFiltrados"
                :key="client.id"
                class="transition-colors hover:bg-slate-50/70"
              >
                <td class="px-6 py-4">
                  <button
                    @click="abrirDossier(client)"
                    class="text-left transition-colors hover:text-[var(--ct-primary)]"
                  >
                    <div class="flex items-start gap-3">
                      <div
                        class="flex h-10 w-10 items-center justify-center rounded-full bg-[var(--ct-primary-soft)] text-xs font-semibold text-[var(--ct-primary)]"
                      >
                        {{ (client.razao_social || client.nome || '?').slice(0, 2).toUpperCase() }}
                      </div>

                      <div>
                        <p class="text-sm font-semibold text-[var(--ct-ink)]">
                          {{ client.razao_social || client.nome }}
                        </p>
                        <p class="mt-0.5 text-xs text-[var(--ct-text-muted)]">
                          {{ client.razao_social ? 'Pessoa jurídica' : 'Pessoa física' }} · Abrir dossiê
                        </p>
                      </div>
                    </div>
                  </button>
                </td>

                <td class="px-6 py-4 text-sm text-[var(--ct-ink)]">
                  {{ client.cnpj || client.cpf }}
                </td>

                <td class="px-6 py-4">
                  <span class="inline-flex rounded-lg bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700">
                    {{ client.regime_tributario }}
                  </span>
                </td>

                <td class="px-6 py-4">
                  <span
                    class="inline-flex rounded-lg px-2.5 py-1 text-xs font-medium"
                    :class="
                      client.natureza_operacao === 'Comércio'
                        ? 'bg-blue-100 text-blue-700'
                        : client.natureza_operacao === 'Indústria'
                          ? 'bg-violet-100 text-violet-700'
                          : 'bg-amber-100 text-amber-700'
                    "
                  >
                    {{ client.natureza_operacao || 'Não definido' }}
                  </span>
                </td>

                <td class="px-6 py-4 text-right">
                  <button
                    v-if="authStore.role === 'admin'"
                    @click="handleDesativar(client.id)"
                    class="text-xs font-medium text-slate-500 transition-colors hover:text-red-600"
                  >
                    Arquivar
                  </button>
                  <span v-else class="text-xs text-slate-300">Apenas leitura</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- DOSSIÊ LATERAL (DRAWER) -->
      <div
        v-if="isDossierOpen"
        class="fixed inset-0 z-50 overflow-hidden"
        aria-labelledby="dossier-title"
        role="dialog"
        aria-modal="true"
      >
        <div class="absolute inset-0 bg-slate-950/50 transition-opacity" @click="isDossierOpen = false"></div>

        <div class="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-10">
          <div
            class="pointer-events-auto w-screen max-w-2xl transform transition-transform"
            :class="isDossierOpen ? 'translate-x-0' : 'translate-x-full'"
          >
            <div class="flex h-full flex-col overflow-y-auto bg-white shadow-2xl">
              <!-- cabeçalho -->
              <div class="border-b border-[var(--ct-border)] bg-[var(--ct-navy)] px-6 py-5">
                <div class="flex items-start justify-between gap-4">
                  <div>
                    <h3 id="dossier-title" class="text-xl font-semibold tracking-tight text-white">
                      {{ selectedClient?.razao_social || selectedClient?.nome }}
                    </h3>
                    <p class="mt-1 text-sm text-white/65">
                      {{ selectedClient?.cnpj || selectedClient?.cpf }}
                    </p>
                  </div>

                  <button
                    @click="isDossierOpen = false"
                    class="rounded-lg p-1 text-white/60 transition-colors hover:bg-white/10 hover:text-white"
                  >
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                  </button>
                </div>
              </div>

              <!-- tabs -->
              <div class="flex border-b border-[var(--ct-border)] bg-slate-50">
                <button
                  @click="activeTab = 'info'"
                  :class="
                    activeTab === 'info'
                      ? 'border-[var(--ct-primary)] text-[var(--ct-primary)]'
                      : 'border-transparent text-slate-500'
                  "
                  class="flex-1 border-b-2 px-4 py-3 text-sm font-medium transition-colors"
                >
                  Dados cadastrais
                </button>

                <button
                  @click="activeTab = 'tasks'"
                  :class="
                    activeTab === 'tasks'
                      ? 'border-[var(--ct-primary)] text-[var(--ct-primary)]'
                      : 'border-transparent text-slate-500'
                  "
                  class="flex-1 border-b-2 px-4 py-3 text-sm font-medium transition-colors"
                >
                  Tarefas recentes
                </button>

                <button
                  @click="activeTab = 'docs'"
                  :class="
                    activeTab === 'docs'
                      ? 'border-[var(--ct-primary)] text-[var(--ct-primary)]'
                      : 'border-transparent text-slate-500'
                  "
                  class="flex-1 border-b-2 px-4 py-3 text-sm font-medium transition-colors"
                >
                  Documentos
                </button>
              </div>

              <!-- conteúdo -->
              <div class="flex-1 space-y-6 p-6">
                <div v-if="isLoadingDossier" class="space-y-3">
                  <div class="h-12 animate-pulse rounded-xl bg-slate-100"></div>
                  <div class="h-12 animate-pulse rounded-xl bg-slate-100"></div>
                  <div class="h-12 animate-pulse rounded-xl bg-slate-100"></div>
                </div>

                <div v-else-if="activeTab === 'info'" class="grid grid-cols-1 gap-4 md:grid-cols-2">
                  <div class="rounded-xl border border-[var(--ct-border)] bg-slate-50 p-4">
                    <span class="block text-xs text-[var(--ct-text-muted)]">Tipo de pessoa</span>
                    <span class="mt-1 block text-sm font-semibold text-[var(--ct-ink)]">
                      {{ selectedClient?.razao_social ? 'Pessoa Jurídica' : 'Pessoa Física' }}
                    </span>
                  </div>

                  <div class="rounded-xl border border-[var(--ct-border)] bg-slate-50 p-4">
                    <span class="block text-xs text-[var(--ct-text-muted)]">Natureza da operação</span>
                    <span class="mt-1 block text-sm font-semibold text-[var(--ct-ink)]">
                      {{ selectedClient?.natureza_operacao || 'Não definido' }}
                    </span>
                  </div>

                  <div class="rounded-xl border border-[var(--ct-border)] bg-slate-50 p-4">
                    <span class="block text-xs text-[var(--ct-text-muted)]">Regime tributário</span>
                    <span class="mt-1 block text-sm font-semibold text-[var(--ct-ink)]">
                      {{ selectedClient?.regime_tributario }}
                    </span>
                  </div>

                  <div class="rounded-xl border border-[var(--ct-border)] bg-slate-50 p-4">
                    <span class="block text-xs text-[var(--ct-text-muted)]">Status no sistema</span>
                    <span class="mt-1 block text-sm font-semibold text-emerald-600">Ativo</span>
                  </div>
                </div>

                <div v-else-if="activeTab === 'tasks'">
                  <div
                    v-if="clientTasks.length === 0"
                    class="py-10 text-center text-sm text-[var(--ct-text-muted)]"
                  >
                    Nenhuma tarefa encontrada para este cliente.
                  </div>

                  <div v-else class="space-y-3">
                    <div
                      v-for="task in clientTasks"
                      :key="task.id"
                      class="flex items-center justify-between rounded-xl border border-[var(--ct-border)] bg-slate-50 p-4"
                    >
                      <div>
                        <p class="text-sm font-semibold text-[var(--ct-ink)]">{{ task.title }}</p>
                        <p class="mt-1 text-xs text-[var(--ct-text-muted)]">
                          Prazo: {{ formatDocDate(task.due_date) }}
                        </p>
                      </div>

                      <span
                        class="rounded-md px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.08em]"
                        :class="getStatusColor(task.status)"
                      >
                        {{ task.status.replace('_', ' ') }}
                      </span>
                    </div>
                  </div>
                </div>

                <div v-else-if="activeTab === 'docs'">
                  <div
                    v-if="clientDocuments.length === 0"
                    class="py-10 text-center text-sm text-[var(--ct-text-muted)]"
                  >
                    Nenhum documento enviado para este cliente.
                  </div>

                  <div v-else class="space-y-3">
                    <div
                      v-for="doc in clientDocuments"
                      :key="doc.id"
                      class="flex items-center justify-between rounded-xl border border-[var(--ct-border)] bg-slate-50 p-4"
                    >
                      <div class="flex items-center gap-3">
                        <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-red-100 text-red-600">
                          <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                            <path
                              fill-rule="evenodd"
                              d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z"
                              clip-rule="evenodd"
                            />
                          </svg>
                        </div>

                        <div>
                          <p class="text-sm font-semibold text-[var(--ct-ink)]">{{ doc.nome_arquivo }}</p>
                          <p class="mt-1 text-xs text-[var(--ct-text-muted)]">
                            Enviado em: {{ formatDocDate(doc.created_at) }}
                          </p>
                        </div>
                      </div>

                      <button
                        @click="baixarDocDossier(doc.id, doc.nome_arquivo)"
                        class="text-xs font-semibold text-[var(--ct-primary)] transition-colors hover:text-[var(--ct-primary-hover)]"
                      >
                        Baixar
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- modal cadastro -->
      <div
        v-if="isModalOpen"
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4 backdrop-blur-[2px]"
      >
        <div class="w-full max-w-md overflow-hidden rounded-2xl border border-[var(--ct-border)] bg-white shadow-2xl">
          <div class="flex items-center justify-between border-b border-[var(--ct-border)] px-6 py-5">
            <h3 class="text-lg font-semibold text-[var(--ct-ink)]">Cadastrar cliente</h3>
            <button
              @click="isModalOpen = false"
              class="rounded-lg p-1 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-700"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>

          <form @submit.prevent="handleCreateClient" class="space-y-5 p-6">
            <div class="flex gap-2 rounded-xl bg-slate-100 p-1">
              <button
                type="button"
                @click="setTipoPessoa('PJ')"
                class="flex-1 rounded-lg py-2.5 text-sm font-medium transition-all"
                :class="
                  newClient.tipo_pessoa === 'PJ'
                    ? 'bg-white text-[var(--ct-ink)] shadow-sm'
                    : 'text-slate-500 hover:text-[var(--ct-ink)]'
                "
              >
                Pessoa jurídica
              </button>

              <button
                type="button"
                @click="setTipoPessoa('PF')"
                class="flex-1 rounded-lg py-2.5 text-sm font-medium transition-all"
                :class="
                  newClient.tipo_pessoa === 'PF'
                    ? 'bg-white text-[var(--ct-ink)] shadow-sm'
                    : 'text-slate-500 hover:text-[var(--ct-ink)]'
                "
              >
                Pessoa física
              </button>
            </div>

            <!-- formulário como antes -->
            <template v-if="newClient.tipo_pessoa === 'PJ'">
              <div>
                <label class="mb-1.5 block text-sm font-medium text-[var(--ct-ink)]/80">Razão social</label>
                <input
                  v-model="newClient.razao_social"
                  type="text"
                  required
                  placeholder="Empresa LTDA"
                  class="w-full rounded-xl border border-[var(--ct-border)] px-4 py-3 text-sm outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
                  :class="formErrors.razao_social ? 'border-red-400 bg-red-50/30' : ''"
                />
                <p v-if="formErrors.razao_social" class="mt-1.5 text-xs text-red-500">
                  {{ formErrors.razao_social }}
                </p>
              </div>

              <div>
                <label class="mb-1.5 block text-sm font-medium text-[var(--ct-ink)]/80">CNPJ</label>
                <input
                  v-model="newClient.cnpj"
                  v-maska="{ mask: 'XX.XXX.XXX/XXXX-XX', tokens: { 'X': { pattern: /[a-zA-Z0-9]/ } } }"
                  type="text"
                  required
                  placeholder="00.000.000/0000-00"
                  class="w-full rounded-xl border border-[var(--ct-border)] px-4 py-3 text-sm outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
                  :class="formErrors.cnpj ? 'border-red-400 bg-red-50/30' : ''"
                />
                <p v-if="formErrors.cnpj" class="mt-1.5 text-xs text-red-500">
                  {{ formErrors.cnpj }}
                </p>
              </div>
            </template>

            <template v-if="newClient.tipo_pessoa === 'PF'">
              <div>
                <label class="mb-1.5 block text-sm font-medium text-[var(--ct-ink)]/80">Nome completo</label>
                <input
                  v-model="newClient.nome"
                  type="text"
                  required
                  placeholder="João da Silva"
                  class="w-full rounded-xl border border-[var(--ct-border)] px-4 py-3 text-sm outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
                  :class="formErrors.nome ? 'border-red-400 bg-red-50/30' : ''"
                />
                <p v-if="formErrors.nome" class="mt-1.5 text-xs text-red-500">
                  {{ formErrors.nome }}
                </p>
              </div>

              <div>
                <label class="mb-1.5 block text-sm font-medium text-[var(--ct-ink)]/80">CPF</label>
                <input
                  v-model="newClient.cpf"
                  v-maska="'###.###.###-##'"
                  type="text"
                  required
                  placeholder="000.000.000-00"
                  class="w-full rounded-xl border border-[var(--ct-border)] px-4 py-3 text-sm outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
                  :class="formErrors.cpf ? 'border-red-400 bg-red-50/30' : ''"
                />
                <p v-if="formErrors.cpf" class="mt-1.5 text-xs text-red-500">
                  {{ formErrors.cpf }}
                </p>
              </div>
            </template>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="mb-1.5 block text-sm font-medium text-[var(--ct-ink)]/80">Regime tributário</label>
                <select
                  v-model="newClient.regime_tributario"
                  class="w-full rounded-xl border border-[var(--ct-border)] bg-white px-4 py-3 text-sm outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
                >
                  <option value="Simples Nacional">Simples Nacional</option>
                  <option value="Lucro Presumido">Lucro Presumido</option>
                  <option value="Lucro Real">Lucro Real</option>
                  <option value="MEI">MEI</option>
                </select>
              </div>

              <div>
                <label class="mb-1.5 block text-sm font-medium text-[var(--ct-ink)]/80">Natureza</label>
                <select
                  v-model="newClient.natureza_operacao"
                  class="w-full rounded-xl border border-[var(--ct-border)] bg-white px-4 py-3 text-sm outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
                >
                  <option value="Serviços">Serviços</option>
                  <option value="Comércio">Comércio</option>
                  <option value="Indústria">Indústria</option>
                </select>
              </div>
            </div>

            <div class="flex justify-end gap-3 pt-2">
              <button
                type="button"
                @click="isModalOpen = false"
                class="rounded-xl px-4 py-2.5 text-sm font-medium text-slate-500 transition-colors hover:bg-slate-100"
              >
                Cancelar
              </button>

              <button
                type="submit"
                :disabled="isSubmitting"
                class="rounded-xl bg-[var(--ct-primary)] px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[var(--ct-primary-hover)] disabled:opacity-50"
              >
                {{ isSubmitting ? 'Salvando...' : 'Salvar cliente' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- modal csv -->
      <div
        v-if="isImportModalOpen"
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4 backdrop-blur-[2px]"
      >
        <div class="w-full max-w-md overflow-hidden rounded-2xl border border-[var(--ct-border)] bg-white shadow-2xl">
          <div class="flex items-center justify-between border-b border-[var(--ct-border)] bg-slate-50 px-6 py-5">
            <h3 class="text-lg font-semibold text-[var(--ct-ink)]">Importar clientes</h3>
            <button
              @click="isImportModalOpen = false"
              class="rounded-lg p-1 text-slate-400 transition-colors hover:bg-white hover:text-slate-700"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>

          <div class="space-y-6 p-6">
            <div class="rounded-xl border border-blue-200 bg-blue-50 p-4">
              <h4 class="mb-2 text-sm font-semibold text-blue-800">Como importar</h4>
              <ol class="list-inside list-decimal space-y-1 text-xs text-blue-700">
                <li>Baixe o template de exemplo.</li>
                <li>Preencha os dados sem alterar os cabeçalhos.</li>
                <li>Salve como CSV.</li>
                <li>Envie o arquivo nesta tela.</li>
              </ol>

              <button
                @click="baixarTemplate"
                class="mt-3 inline-flex items-center gap-1 text-xs font-semibold text-blue-700 underline transition-colors hover:text-blue-900"
              >
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
                </svg>
                Baixar template CSV
              </button>
            </div>

            <div>
              <label class="mb-2 block text-sm font-medium text-[var(--ct-ink)]/80">Arquivo CSV</label>
              <input
                type="file"
                accept=".csv"
                @change="handleCsvChange"
                class="w-full rounded-xl border border-[var(--ct-border)] p-2 text-sm text-slate-500 file:mr-4 file:rounded-lg file:border-0 file:bg-[var(--ct-primary-soft)] file:px-4 file:py-2 file:text-sm file:font-semibold file:text-[var(--ct-primary)] hover:file:bg-[#BFDBFE]"
              />
            </div>

            <div class="flex justify-end gap-3">
              <button
                @click="isImportModalOpen = false"
                class="rounded-xl px-4 py-2.5 text-sm font-medium text-slate-500 transition-colors hover:bg-slate-100"
              >
                Cancelar
              </button>

              <button
                @click="handleUploadCsv"
                :disabled="isUploadingCsv || !csvFile"
                class="rounded-xl bg-[var(--ct-navy)] px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#0F1B46] disabled:opacity-50"
              >
                {{ isUploadingCsv ? 'Processando...' : 'Iniciar importação' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>