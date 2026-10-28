<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import api from '../services/api'
import Layout from '../components/Layout.vue'
import { toast } from 'vue3-toastify'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import EmptyState from '../components/EmptyState.vue'
import { getApiErrorMessage } from '../utils/apiError'
import { useAuthStore } from '../stores/auth'
import PaginationControls from '../components/PaginationControls.vue'
import { fetchAllPages, fetchPage } from '../services/pagination'
import CollectionViewToggle from '../components/CollectionViewToggle.vue'

const authStore = useAuthStore()
const canManageDocuments = computed(() => ['admin', 'gerente'].includes(authStore.role))

interface DocumentRecord {
  id: string
  client_id: string
  nome_arquivo: string
  categoria: string
  created_at: string
}

interface ClientRecord {
  id: string
  nome?: string
  razao_social?: string
}

interface DocumentFolder {
  client_id: string
  client_name: string
  client_active: boolean
  document_count: number
  last_uploaded_at: string | null
}

const pastas = ref<DocumentFolder[]>([])
const visualizacao = ref<'cards' | 'lista'>('cards')
const pastaSelecionada = ref<DocumentFolder | null>(null)
const isFolderView = computed(() => visualizacao.value === 'cards' && !pastaSelecionada.value)
const loadError = ref(false)
let folderReturnPage = 1
let fetchVersion = 0

const documentos = ref<DocumentRecord[]>([])
const clientes = ref<ClientRecord[]>([])
const isLoading = ref(true)
const currentPage = ref(1)
const totalPages = ref(0)
const totalResults = ref(0)
const pageSize = 20

const isModalOpen = ref(false)
const isUploading = ref(false)
const documentToDelete = ref<{ id: string; name: string } | null>(null)

const filtroClienteId = ref('')
const filtroCategoria = ref('')
const searchQuery = ref('')

const documentosFiltrados = computed(() => documentos.value)

const docForm = ref({ client_id: '', categoria: 'Geral' })
const selectedFile = ref<File | null>(null)

const fetchData = async () => {
  const version = ++fetchVersion
  const folderMode = isFolderView.value
  isLoading.value = true
  loadError.value = false
  const params = {
    search: searchQuery.value.trim() || undefined,
    client_id: pastaSelecionada.value?.client_id || filtroClienteId.value || undefined,
    categoria: filtroCategoria.value || undefined,
  }
  try {
    const page = folderMode
      ? await fetchPage<DocumentFolder>(
          '/api/v1/documentos/pastas',
          currentPage.value,
          pageSize,
          params,
        )
      : await fetchPage<DocumentRecord>('/api/v1/documentos', currentPage.value, pageSize, params)
    if (version !== fetchVersion || folderMode !== isFolderView.value) return
    const lastPage = Math.max(1, page.pages)
    if (currentPage.value > lastPage) {
      currentPage.value = lastPage
      await fetchData()
      return
    }
    if (folderMode) pastas.value = page.items as DocumentFolder[]
    else documentos.value = page.items as DocumentRecord[]
    totalPages.value = page.pages
    totalResults.value = page.total
  } catch (error) {
    if (version !== fetchVersion) return
    loadError.value = true
    toast.error(getApiErrorMessage(error, 'Erro ao carregar documentos.'))
  } finally {
    if (version === fetchVersion) isLoading.value = false
  }
}

const abrirPasta = (pasta: DocumentFolder) => {
  folderReturnPage = currentPage.value
  pastaSelecionada.value = pasta
  currentPage.value = 1
  void fetchData()
}
const voltarPastas = () => {
  pastaSelecionada.value = null
  currentPage.value = folderReturnPage
  void fetchData()
}
const abrirEnvio = () => {
  const clientId = pastaSelecionada.value?.client_id || filtroClienteId.value
  docForm.value = {
    client_id: clientes.value.some((client) => client.id === clientId) ? clientId : '',
    categoria: filtroCategoria.value || 'Geral',
  }
  selectedFile.value = null
  isModalOpen.value = true
}

const fetchClients = async () => {
  try {
    clientes.value = await fetchAllPages<ClientRecord>('/api/v1/clientes')
  } catch {
    toast.error('Erro ao carregar os clientes disponíveis.')
  }
}

const changePage = (page: number) => {
  currentPage.value = page
  fetchData()
}

let filterTimer: ReturnType<typeof setTimeout> | undefined
watch([searchQuery, filtroClienteId, filtroCategoria], (values, previous) => {
  if (filterTimer) clearTimeout(filterTimer)
  fetchVersion += 1
  isLoading.value = true
  if (values[1] !== previous[1]) pastaSelecionada.value = null
  filterTimer = setTimeout(() => {
    currentPage.value = 1
    folderReturnPage = 1
    void fetchData()
  }, 300)
})
watch(visualizacao, () => {
  if (filterTimer) clearTimeout(filterTimer)
  pastaSelecionada.value = null
  currentPage.value = 1
  folderReturnPage = 1
  void fetchData()
})
onUnmounted(() => {
  if (filterTimer) clearTimeout(filterTimer)
  fetchVersion += 1
})

const handleFileChange = (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (file) selectedFile.value = file
}

const handleUpload = async () => {
  if (!selectedFile.value || !docForm.value.client_id) return

  isUploading.value = true

  try {
    const formData = new FormData()
    formData.append('client_id', docForm.value.client_id)
    formData.append('categoria', docForm.value.categoria)
    formData.append('file', selectedFile.value)

    await api.post('/api/v1/documentos', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })

    isModalOpen.value = false
    docForm.value = { client_id: '', categoria: 'Geral' }
    selectedFile.value = null
    currentPage.value = 1
    await fetchData()

    toast.success('Documento salvo com sucesso!')
  } catch (error: unknown) {
    toast.error(getApiErrorMessage(error, 'Erro ao enviar o documento.'))
  } finally {
    isUploading.value = false
  }
}

const baixarDocumento = async (docId: string, nomeArquivo: string) => {
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
    window.URL.revokeObjectURL(url)
  } catch (error) {
    toast.error('Erro ao baixar o arquivo.')
    console.error(error)
  }
}

const handleExcluirDocumento = async () => {
  const docId = documentToDelete.value?.id
  if (!docId) return
  try {
    await api.delete(`/api/v1/documentos/${docId}`)
    if (documentos.value.length === 1 && currentPage.value > 1) currentPage.value -= 1
    await fetchData()
    toast.success('Documento excluído.')
    documentToDelete.value = null
  } catch (error) {
    toast.error(getApiErrorMessage(error, 'Não foi possível excluir o documento.'))
  }
}

const getNomeCliente = (clientId: string) => {
  const cliente = clientes.value.find((c) => String(c.id) === String(clientId))
  return cliente
    ? cliente.nome || cliente.razao_social
    : pastaSelecionada.value?.client_id === clientId
      ? pastaSelecionada.value.client_name
      : 'Cliente indisponível'
}

const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('pt-BR')
}

const getFileIcon = (fileName: string) => {
  const ext = fileName.split('.').pop()?.toLowerCase()

  if (ext === 'pdf') {
    return {
      icon: 'PDF',
      color: 'text-red-600',
      bg: 'bg-red-100',
      label: 'PDF',
    }
  }

  if (ext === 'xml') {
    return {
      icon: 'XML',
      color: 'text-[var(--ct-primary)]',
      bg: 'bg-[var(--ct-primary-soft)]',
      label: 'XML',
    }
  }

  if (['xls', 'xlsx', 'csv'].includes(ext || '')) {
    return {
      icon: 'XLS',
      color: 'text-emerald-600',
      bg: 'bg-emerald-100',
      label: 'Planilha',
    }
  }

  if (['doc', 'docx'].includes(ext || '')) {
    return {
      icon: 'DOC',
      color: 'text-indigo-600',
      bg: 'bg-indigo-100',
      label: 'Documento',
    }
  }

  if (['jpg', 'jpeg', 'png'].includes(ext || '')) {
    return {
      icon: 'IMG',
      color: 'text-violet-600',
      bg: 'bg-violet-100',
      label: 'Imagem',
    }
  }

  return {
    icon: 'FILE',
    color: 'text-slate-500',
    bg: 'bg-slate-100',
    label: 'Arquivo',
  }
}

const getCategoriaBadge = (categoria: string) => {
  const styles: Record<string, string> = {
    Fiscal: 'bg-[var(--ct-primary-soft)] text-[var(--ct-primary)] border-[var(--ct-border)]',
    Contábil: 'bg-violet-100 text-violet-700 border-violet-200',
    'Departamento Pessoal': 'bg-amber-100 text-amber-700 border-amber-200',
    Societário: 'bg-emerald-100 text-emerald-700 border-emerald-200',
    Geral: 'bg-slate-100 text-slate-600 border-slate-200',
  }

  return `inline-flex rounded-md border px-2.5 py-1 text-[11px] font-semibold ${styles[categoria] || styles['Geral']}`
}

onMounted(() => {
  fetchData()
  fetchClients()
})
</script>

<template>
  <Layout title="Repositório de Documentos">
    <div class="ct-directory-workspace ct-workspace space-y-4">
      <!-- topo -->
      <header
        class="ct-page-header flex flex-col gap-4 border-b border-[var(--ct-border)] pb-5 xl:flex-row xl:items-end xl:justify-between"
      >
        <div>
          <h1 class="ct-page-title text-2xl font-semibold tracking-tight text-[var(--ct-ink)]">
            Repositório de documentos
          </h1>
          <p class="ct-page-description mt-1 text-sm text-[var(--ct-text-muted)]">
            Arquivos fiscais, contábeis e operacionais organizados por cliente.
          </p>
        </div>

        <button
          @click="abrirEnvio"
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
          <span>Enviar documento</span>
        </button>
      </header>

      <!-- filtros -->
      <section class="ct-filter-panel border-b border-[var(--ct-border)] pb-5">
        <div class="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
          <div class="grid w-full grid-cols-1 gap-3 md:grid-cols-3 xl:max-w-4xl">
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
                aria-label="Buscar documentos"
                type="text"
                placeholder="Buscar arquivo..."
                class="w-full rounded-xl border border-[var(--ct-border)] bg-white py-2.5 pl-10 pr-4 text-sm text-[var(--ct-ink)] outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
              />
            </div>

            <select
              v-model="filtroClienteId"
              aria-label="Filtrar documentos por cliente"
              class="w-full rounded-xl border border-[var(--ct-border)] bg-white px-4 py-2.5 text-sm text-[var(--ct-ink)] outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
            >
              <option value="">Todos os clientes</option>
              <option v-for="cliente in clientes" :key="cliente.id" :value="cliente.id">
                {{ cliente.nome || cliente.razao_social }}
              </option>
            </select>

            <select
              v-model="filtroCategoria"
              aria-label="Filtrar documentos por categoria"
              class="w-full rounded-xl border border-[var(--ct-border)] bg-white px-4 py-2.5 text-sm text-[var(--ct-ink)] outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
            >
              <option value="">Todas as categorias</option>
              <option value="Fiscal">Fiscal</option>
              <option value="Contábil">Contábil</option>
              <option value="Departamento Pessoal">Departamento Pessoal</option>
              <option value="Societário">Societário</option>
              <option value="Geral">Geral</option>
            </select>
          </div>

          <div class="flex flex-wrap items-center gap-3">
            <span class="text-xs text-slate-500" role="status"
              >{{ totalResults }} {{ isFolderView ? 'pasta(s)' : 'arquivo(s)' }}</span
            >
            <CollectionViewToggle v-model="visualizacao" cards-label="Pastas" />
          </div>
        </div>
      </section>

      <nav
        v-if="pastaSelecionada"
        aria-label="Navegação das pastas"
        class="flex flex-wrap items-center gap-2 text-sm"
      >
        <button
          type="button"
          class="font-medium text-blue-500 hover:underline"
          @click="voltarPastas"
        >
          ← Todas as pastas
        </button>
        <span aria-hidden="true" class="text-slate-300">/</span>
        <span aria-current="page" class="font-semibold text-slate-800">{{
          pastaSelecionada.client_name
        }}</span>
        <span
          v-if="!pastaSelecionada.client_active"
          class="rounded-full bg-slate-100 px-2 py-1 text-[10px] text-slate-500"
          >Cliente arquivado</span
        >
      </nav>
      <div
        v-if="loadError"
        role="alert"
        class="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-amber-200 bg-amber-50 p-5"
      >
        <p class="text-sm text-amber-900">
          Não foi possível carregar {{ isFolderView ? 'as pastas' : 'os documentos' }}.
        </p>
        <button
          type="button"
          class="text-sm font-semibold text-blue-600 hover:underline"
          @click="fetchData"
        >
          Tentar novamente
        </button>
      </div>
      <section v-else-if="isFolderView" aria-label="Pastas de documentos por cliente">
        <div
          v-if="isLoading"
          class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3"
          aria-label="Carregando pastas"
        >
          <div
            v-for="n in 6"
            :key="n"
            class="h-48 animate-pulse rounded-xl border border-[#e7edf5] bg-white"
          />
        </div>
        <EmptyState
          v-else-if="!pastas.length"
          title="Nenhuma pasta encontrada"
          :description="
            searchQuery || filtroCategoria || filtroClienteId
              ? 'Ajuste os filtros para encontrar os arquivos ou envie um novo documento.'
              : 'As pastas são organizadas a partir dos clientes da sua carteira.'
          "
          :action-label="clientes.length ? 'Enviar documento' : undefined"
          @action="abrirEnvio"
        />
        <div v-else class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          <button
            v-for="pasta in pastas"
            :key="pasta.client_id"
            type="button"
            class="ct-document-folder flex min-w-0 flex-col rounded-xl border border-[#e7edf5] bg-white p-5 text-left transition-colors hover:border-blue-200 hover:bg-blue-50/20"
            :aria-label="`Abrir pasta de ${pasta.client_name}`"
            @click="abrirPasta(pasta)"
          >
            <div class="mb-4 flex w-full items-start justify-between gap-3">
              <svg viewBox="0 0 64 52" class="h-12 w-14 shrink-0" fill="none" aria-hidden="true">
                <path
                  d="M5 12a5 5 0 0 1 5-5h15l6 6h23a5 5 0 0 1 5 5v24a5 5 0 0 1-5 5H10a5 5 0 0 1-5-5V12Z"
                  fill="#e8f2ff"
                  stroke="#8bbaff"
                  stroke-width="1.5"
                />
                <path d="M5 21h54" stroke="#8bbaff" stroke-width="1.5" />
              </svg>
              <span
                v-if="!pasta.client_active"
                class="rounded-full bg-slate-100 px-2 py-1 text-[10px] text-slate-500"
                >Arquivado</span
              >
            </div>
            <h2 class="break-words text-sm font-semibold leading-6 text-slate-900">
              {{ pasta.client_name }}
            </h2>
            <p class="mb-5 mt-2 text-xs leading-6 text-slate-500">
              {{
                pasta.last_uploaded_at
                  ? `Último envio: ${formatDate(pasta.last_uploaded_at)}`
                  : 'Nenhum arquivo enviado'
              }}
            </p>
            <div
              class="mt-auto flex w-full flex-wrap items-center justify-between gap-3 border-t border-[#edf1f7] pt-4 text-xs"
            >
              <span class="text-slate-500"
                >{{ pasta.document_count }} {{ pasta.document_count === 1 ? 'arquivo' : 'arquivos'
                }}{{
                  searchQuery || filtroCategoria
                    ? pasta.document_count === 1
                      ? ' encontrado'
                      : ' encontrados'
                    : ''
                }}</span
              >
              <span class="font-medium text-blue-500">Abrir pasta →</span>
            </div>
          </button>
        </div>
        <PaginationControls
          :page="currentPage"
          :pages="totalPages"
          :total="totalResults"
          class="mt-4 rounded-xl border border-[#e7edf5] bg-white"
          @change="changePage"
        />
      </section>

      <!-- tabela -->
      <section
        v-else
        class="ct-data-panel overflow-hidden rounded-xl border border-[var(--ct-border)] bg-white"
      >
        <div v-if="isLoading" class="space-y-3 p-6">
          <div class="h-12 animate-pulse rounded-xl bg-slate-100"></div>
          <div class="h-12 animate-pulse rounded-xl bg-slate-100"></div>
          <div class="h-12 animate-pulse rounded-xl bg-slate-100"></div>
          <div class="h-12 animate-pulse rounded-xl bg-slate-100"></div>
        </div>

        <EmptyState
          v-else-if="documentosFiltrados.length === 0"
          :title="pastaSelecionada ? 'Nenhum documento nesta pasta' : 'Nenhum documento encontrado'"
          description="Ajuste os filtros ou envie um novo arquivo."
          :action-label="clientes.length ? 'Enviar documento' : undefined"
          @action="abrirEnvio"
        />

        <div v-else class="overflow-x-auto">
          <div class="divide-y divide-[var(--ct-border)] md:hidden">
            <article v-for="doc in documentosFiltrados" :key="`mobile-${doc.id}`" class="p-4">
              <button class="w-full text-left" @click="baixarDocumento(doc.id, doc.nome_arquivo)">
                <div class="flex items-start justify-between gap-3">
                  <div class="min-w-0">
                    <p class="truncate text-sm font-semibold text-[var(--ct-ink)]">
                      {{ doc.nome_arquivo }}
                    </p>
                    <p class="mt-1 text-xs text-[var(--ct-text-muted)]">
                      {{ getNomeCliente(doc.client_id) }} · {{ formatDate(doc.created_at) }}
                    </p>
                  </div>
                  <span :class="getCategoriaBadge(doc.categoria || 'Geral')">{{
                    doc.categoria || 'Geral'
                  }}</span>
                </div>
              </button>
              <div class="mt-3 flex gap-4">
                <button
                  class="text-xs font-semibold text-[var(--ct-primary)]"
                  @click="baixarDocumento(doc.id, doc.nome_arquivo)"
                >
                  Baixar</button
                ><button
                  v-if="canManageDocuments"
                  class="text-xs font-semibold text-red-600"
                  @click="documentToDelete = { id: doc.id, name: doc.nome_arquivo }"
                >
                  Excluir
                </button>
              </div>
            </article>
          </div>
          <table class="hidden min-w-full md:table">
            <thead class="border-b border-[var(--ct-border)] bg-slate-50/80">
              <tr>
                <th
                  class="px-6 py-4 text-left text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500"
                >
                  Arquivo
                </th>
                <th
                  class="px-6 py-4 text-left text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500"
                >
                  Categoria
                </th>
                <th
                  class="px-6 py-4 text-left text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500"
                >
                  Cliente
                </th>
                <th
                  class="px-6 py-4 text-left text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500"
                >
                  Data de envio
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
                v-for="doc in documentosFiltrados"
                :key="doc.id"
                class="transition-colors hover:bg-slate-50/70"
              >
                <td class="px-6 py-4">
                  <button
                    @click="baixarDocumento(doc.id, doc.nome_arquivo)"
                    class="flex items-center gap-3 text-left transition-colors hover:text-[var(--ct-primary)]"
                  >
                    <div
                      class="flex h-10 w-10 items-center justify-center rounded-lg text-[9px] font-bold tracking-wide"
                      :class="getFileIcon(doc.nome_arquivo).bg"
                    >
                      {{ getFileIcon(doc.nome_arquivo).icon }}
                    </div>

                    <div class="min-w-0">
                      <p class="truncate text-sm font-semibold text-[var(--ct-ink)]">
                        {{ doc.nome_arquivo }}
                      </p>
                      <p class="mt-0.5 text-xs text-[var(--ct-text-muted)]">
                        {{ getFileIcon(doc.nome_arquivo).label }}
                      </p>
                    </div>
                  </button>
                </td>

                <td class="px-6 py-4">
                  <span :class="getCategoriaBadge(doc.categoria || 'Geral')">
                    {{ doc.categoria || 'Geral' }}
                  </span>
                </td>

                <td class="px-6 py-4 text-sm text-[var(--ct-ink)]">
                  {{ getNomeCliente(doc.client_id) }}
                </td>

                <td class="px-6 py-4 text-sm text-[var(--ct-text-muted)]">
                  {{ formatDate(doc.created_at) }}
                </td>

                <td class="px-6 py-4">
                  <div class="flex justify-end gap-2">
                    <button
                      @click="baixarDocumento(doc.id, doc.nome_arquivo)"
                      class="rounded-lg border border-[var(--ct-border)] bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-50"
                    >
                      Baixar
                    </button>

                    <button
                      v-if="canManageDocuments"
                      @click="documentToDelete = { id: doc.id, name: doc.nome_arquivo }"
                      class="rounded-lg border border-red-200 bg-red-50 px-3 py-1.5 text-xs font-semibold text-red-600 transition-colors hover:bg-red-100"
                    >
                      Excluir
                    </button>
                  </div>
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

      <!-- modal upload -->
      <div
        v-if="isModalOpen"
        v-focus-trap
        role="dialog"
        aria-modal="true"
        aria-labelledby="document-modal-title"
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4 backdrop-blur-[2px]"
      >
        <div
          class="w-full max-w-md overflow-hidden rounded-xl border border-[var(--ct-border)] bg-white shadow-2xl"
        >
          <div
            class="flex items-center justify-between border-b border-[var(--ct-border)] bg-slate-50 px-6 py-5"
          >
            <h3 id="document-modal-title" class="text-lg font-semibold text-[var(--ct-ink)]">
              Enviar novo documento
            </h3>
            <button
              @click="isModalOpen = false"
              aria-label="Fechar envio de documento"
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

          <form @submit.prevent="handleUpload" class="space-y-5 p-6">
            <div>
              <label
                for="document-upload-client"
                class="mb-1.5 block text-sm font-medium text-[var(--ct-ink)]/80"
              >
                Vincular a qual cliente?
              </label>
              <select
                v-model="docForm.client_id"
                id="document-upload-client"
                required
                class="w-full rounded-xl border border-[var(--ct-border)] bg-white px-4 py-3 text-sm outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
              >
                <option value="" disabled>Selecione um cliente...</option>
                <option v-for="cliente in clientes" :key="cliente.id" :value="cliente.id">
                  {{ cliente.nome || cliente.razao_social }}
                </option>
              </select>
            </div>

            <div>
              <label
                for="document-upload-category"
                class="mb-1.5 block text-sm font-medium text-[var(--ct-ink)]/80"
              >
                Categoria do documento
              </label>
              <select
                v-model="docForm.categoria"
                id="document-upload-category"
                required
                class="w-full rounded-xl border border-[var(--ct-border)] bg-white px-4 py-3 text-sm outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
              >
                <option value="Geral">Geral</option>
                <option value="Fiscal">Fiscal</option>
                <option value="Contábil">Contábil</option>
                <option value="Departamento Pessoal">Departamento Pessoal</option>
                <option value="Societário">Societário</option>
              </select>
            </div>

            <div>
              <label
                for="document-upload-file"
                class="mb-1.5 block text-sm font-medium text-[var(--ct-ink)]/80"
              >
                Selecionar arquivo
              </label>
              <input
                type="file"
                id="document-upload-file"
                accept=".pdf,.png,.jpg,.jpeg,.docx,.xlsx"
                @change="handleFileChange"
                required
                class="w-full rounded-xl border border-[var(--ct-border)] p-2 text-sm text-slate-500 file:mr-4 file:rounded-lg file:border-0 file:bg-[var(--ct-primary-soft)] file:px-4 file:py-2 file:text-sm file:font-semibold file:text-[var(--ct-primary)] hover:file:bg-[var(--ct-accent-soft)]"
              />
              <p class="mt-1.5 text-xs text-[var(--ct-text-muted)]">
                PDF, PNG, JPG, DOCX ou XLSX, com até 5 MB.
              </p>
            </div>

            <div
              v-if="selectedFile"
              class="rounded-xl border border-[var(--ct-border)] bg-slate-50 p-4"
            >
              <p class="text-xs font-semibold uppercase tracking-[0.08em] text-slate-500">
                Arquivo selecionado
              </p>
              <p class="mt-1 text-sm font-medium text-[var(--ct-ink)]">
                {{ selectedFile.name }}
              </p>
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
                :disabled="isUploading || !selectedFile"
                class="rounded-xl bg-[var(--ct-primary)] px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[var(--ct-primary-hover)] disabled:opacity-50"
              >
                {{ isUploading ? 'Enviando...' : 'Fazer upload' }}
              </button>
            </div>
          </form>
        </div>
      </div>
      <ConfirmDialog
        :open="!!documentToDelete"
        title="Excluir documento"
        :message="`Deseja apagar definitivamente o arquivo ${documentToDelete?.name || ''}?`"
        confirm-label="Excluir documento"
        @close="documentToDelete = null"
        @confirm="handleExcluirDocumento"
      />
    </div>
  </Layout>
</template>
