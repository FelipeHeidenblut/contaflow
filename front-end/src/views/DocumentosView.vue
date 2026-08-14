<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '../services/api'
import Layout from '../components/Layout.vue'
import { toast } from 'vue3-toastify'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import EmptyState from '../components/EmptyState.vue'
import { getApiErrorMessage } from '../utils/apiError'
import { useAuthStore } from '../stores/auth'

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

const documentos = ref<DocumentRecord[]>([])
const clientes = ref<ClientRecord[]>([])
const isLoading = ref(true)

const isModalOpen = ref(false)
const isUploading = ref(false)
const documentToDelete = ref<{ id: string; name: string } | null>(null)

const filtroClienteId = ref('')
const filtroCategoria = ref('')
const searchQuery = ref('')

const documentosFiltrados = computed(() => {
  let resultado = documentos.value

  if (filtroClienteId.value) {
    resultado = resultado.filter((doc) => String(doc.client_id) === String(filtroClienteId.value))
  }

  if (filtroCategoria.value) {
    resultado = resultado.filter((doc) => doc.categoria === filtroCategoria.value)
  }

  if (searchQuery.value) {
    const termo = searchQuery.value.toLowerCase()
    resultado = resultado.filter((doc) => doc.nome_arquivo.toLowerCase().includes(termo))
  }

  return resultado
})

const totalDocumentos = computed(() => documentos.value.length)
const totalFiscal = computed(
  () => documentos.value.filter((doc) => doc.categoria === 'Fiscal').length,
)
const totalContabil = computed(
  () => documentos.value.filter((doc) => doc.categoria === 'Contábil').length,
)
const totalGeral = computed(
  () => documentos.value.filter((doc) => !doc.categoria || doc.categoria === 'Geral').length,
)

const docForm = ref({ client_id: '', categoria: 'Geral' })
const selectedFile = ref<File | null>(null)

const fetchData = async () => {
  try {
    const [docsResponse, clientesResponse] = await Promise.all([
      api.get<DocumentRecord[]>('/api/v1/documentos'),
      api.get<ClientRecord[]>('/api/v1/clientes'),
    ])
    documentos.value = docsResponse.data
    clientes.value = clientesResponse.data
  } catch (error) {
    toast.error(getApiErrorMessage(error, 'Erro ao carregar dados.'))
  } finally {
    isLoading.value = false
  }
}

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

    const response = await api.post('/api/v1/documentos', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })

    documentos.value.unshift(response.data)
    isModalOpen.value = false
    docForm.value = { client_id: '', categoria: 'Geral' }
    selectedFile.value = null

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
    documentos.value = documentos.value.filter((doc) => doc.id !== docId)
    toast.success('Documento excluído.')
    documentToDelete.value = null
  } catch (error) {
    toast.error(getApiErrorMessage(error, 'Não foi possível excluir o documento.'))
  }
}

const getNomeCliente = (clientId: string) => {
  const cliente = clientes.value.find((c) => String(c.id) === String(clientId))
  return cliente ? cliente.nome || cliente.razao_social : 'Desconhecido'
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

onMounted(() => fetchData())
</script>

<template>
  <Layout title="Repositório de Documentos">
    <div class="ct-workspace space-y-4">
      <!-- topo -->
      <header
        class="ct-page-header flex flex-col gap-4 border-b border-[var(--ct-border)] pb-5 xl:flex-row xl:items-end xl:justify-between"
      >
        <div>
          <h1 class="ct-page-title text-2xl font-semibold tracking-tight text-[var(--ct-ink)]">
            Repositório de documentos
          </h1>
          <p class="ct-page-description mt-1 text-sm text-[var(--ct-text-muted)]">
            Centralize arquivos fiscais, contábeis e operacionais dos seus clientes.
          </p>
        </div>

        <button
          @click="isModalOpen = true"
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

      <!-- cards -->
      <section
        class="ct-summary-grid flex flex-wrap items-center gap-x-10 gap-y-4 border-b border-[var(--ct-border)] pb-5"
      >
        <div class="flex items-baseline gap-2">
          <p class="text-xs font-medium text-[var(--ct-text-muted)]">Total de arquivos</p>
          <p
            class="text-xl font-semibold tracking-tight text-[var(--ct-ink)] [font-variant-numeric:tabular-nums]"
          >
            {{ totalDocumentos }}
          </p>
        </div>

        <div class="flex items-baseline gap-2">
          <p class="text-xs font-medium text-[var(--ct-text-muted)]">Fiscal</p>
          <p
            class="text-xl font-semibold tracking-tight text-[var(--ct-ink)] [font-variant-numeric:tabular-nums]"
          >
            {{ totalFiscal }}
          </p>
        </div>

        <div class="flex items-baseline gap-2">
          <p class="text-xs font-medium text-[var(--ct-text-muted)]">Contábil</p>
          <p
            class="text-xl font-semibold tracking-tight text-[var(--ct-ink)] [font-variant-numeric:tabular-nums]"
          >
            {{ totalContabil }}
          </p>
        </div>

        <div class="flex items-baseline gap-2">
          <p class="text-xs font-medium text-[var(--ct-text-muted)]">Geral</p>
          <p
            class="text-xl font-semibold tracking-tight text-[var(--ct-ink)] [font-variant-numeric:tabular-nums]"
          >
            {{ totalGeral }}
          </p>
        </div>
      </section>

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

          <div class="text-xs text-[var(--ct-text-muted)]">
            {{ documentosFiltrados.length }} resultado(s)
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
          v-else-if="documentosFiltrados.length === 0"
          title="Nenhum documento encontrado"
          description="Ajuste os filtros ou envie um novo arquivo."
          action-label="Enviar documento"
          @action="isModalOpen = true"
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
              <label class="mb-1.5 block text-sm font-medium text-[var(--ct-ink)]/80">
                Vincular a qual cliente?
              </label>
              <select
                v-model="docForm.client_id"
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
              <label class="mb-1.5 block text-sm font-medium text-[var(--ct-ink)]/80">
                Categoria do documento
              </label>
              <select
                v-model="docForm.categoria"
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
              <label class="mb-1.5 block text-sm font-medium text-[var(--ct-ink)]/80">
                Selecionar arquivo
              </label>
              <input
                type="file"
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
