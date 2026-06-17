<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '../services/api'
import Layout from '../components/Layout.vue'
import { toast } from 'vue3-toastify'

// Estado
const documentos = ref<any[]>([])
const clientes = ref<any[]>([])
const isLoading = ref(true)

const isModalOpen = ref(false)
const isUploading = ref(false)

// Filtros
const filtroClienteId = ref('')
const searchQuery = ref('') // Adicionado para a busca de texto

// Computed: Filtra por cliente E por termo de busca
const documentosFiltrados = computed(() => {
  let resultado = documentos.value

  if (filtroClienteId.value) {
    resultado = resultado.filter((doc) => doc.client_id === filtroClienteId.value)
  }

  if (searchQuery.value) {
    const termo = searchQuery.value.toLowerCase()
    resultado = resultado.filter((doc) => 
      doc.nome_arquivo.toLowerCase().includes(termo)
    )
  }

  return resultado
})

// Formulário de Upload
const docForm = ref({ client_id: '' })
const selectedFile = ref<File | null>(null)

// Busca documentos e clientes
const fetchData = async () => {
  try {
    const [docsResponse, clientesResponse] = await Promise.all([
      api.get('/api/v1/documentos'),
      api.get('/api/v1/clientes'),
    ])
    documentos.value = docsResponse.data
    clientes.value = clientesResponse.data
  } catch (error) {
    toast.error('Erro ao carregar dados.')
  } finally {
    isLoading.value = false
  }
}

// Captura o arquivo
const handleFileChange = (event: any) => {
  const file = event.target.files[0]
  if (file) selectedFile.value = file
}

// Envia o arquivo
const handleUpload = async () => {
  if (!selectedFile.value || !docForm.value.client_id) return

  isUploading.value = true

  try {
    const formData = new FormData()
    formData.append('client_id', docForm.value.client_id)
    formData.append('file', selectedFile.value)

    const response = await api.post('/api/v1/documentos', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })

    documentos.value.unshift(response.data)
    isModalOpen.value = false
    docForm.value.client_id = ''
    selectedFile.value = null

    toast.success('Documento salvo com sucesso!')
  } catch (error: any) {
    const detail = error.response?.data?.detail || 'Erro ao enviar o documento.'
    toast.error(detail)
  } finally {
    isUploading.value = false
  }
}

// ==========================================
// NOVA FUNÇÃO: Download Seguro com Token
// ==========================================
const baixarDocumento = async (docId: string, nomeArquivo: string) => {
  try {
    // Faz a requisição enviando o Token no cabeçalho e recebendo um 'blob' (arquivo)
    const response = await api.get(`/api/v1/documentos/${docId}/download`, {
      responseType: 'blob',
    })

    // Cria uma URL temporária para o arquivo baixado
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    
    // Força o download com o nome original do arquivo
    link.setAttribute('download', nomeArquivo)
    document.body.appendChild(link)
    link.click()

    // Limpa o DOM
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    toast.error('Erro ao baixar o arquivo.')
    console.error(error)
  }
}

// Exclui o documento
const handleExcluirDocumento = async (docId: string, nomeArquivo: string) => {
  if (!window.confirm(`Tem certeza que deseja apagar definitivamente o arquivo "${nomeArquivo}"?`))
    return

  try {
    await api.delete(`/api/v1/documentos/${docId}`)
    documentos.value = documentos.value.filter((doc) => doc.id !== docId)
    toast.success('Documento excluído.')
  } catch (error) {
    toast.error('Não foi possível excluir o documento.')
  }
}

// Helpers
const getNomeCliente = (clientId: string) => {
  const cliente = clientes.value.find((c) => c.id === clientId)
  // Corrigido para mostrar nome se for PF
  return cliente ? (cliente.nome || cliente.razao_social) : 'Desconhecido'
}

const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('pt-BR')
}

onMounted(() => fetchData())
</script>

<template>
  <Layout title="Repositório de Documentos">
    <!-- Barra de Ações -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
      <div class="flex flex-col sm:flex-row gap-3 w-full sm:w-auto sm:max-w-2xl">
        <!-- Busca agora vinculada com v-model -->
        <div class="relative w-full sm:w-64">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar arquivo..."
            class="w-full pl-4 pr-10 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#ff8a65] text-sm"
          />
        </div>

        <select
          v-model="filtroClienteId"
          class="w-full sm:w-60 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#ff8a65] bg-white text-gray-700 cursor-pointer text-sm"
        >
          <option value="">📁 Todos os Clientes</option>
          <option v-for="cliente in clientes" :key="cliente.id" :value="cliente.id">
            {{ cliente.nome || cliente.razao_social }}
          </option>
        </select>
      </div>

      <button
        @click="isModalOpen = true"
        class="w-full sm:w-auto bg-[#ff8a65] hover:bg-[#f07047] text-white font-semibold py-2.5 px-5 rounded-xl transition-all flex items-center justify-center gap-2 whitespace-nowrap shadow-sm"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
        </svg>
        <span>Enviar Documento</span>
      </button>
    </div>

    <!-- Tabela -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div v-if="isLoading" class="p-8 text-center text-gray-500">Carregando arquivos...</div>
      <div v-else-if="documentosFiltrados.length === 0" class="p-8 text-center text-gray-500">
        Nenhum documento encontrado para esta seleção.
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Arquivo</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Cliente</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Data</th>
              <th class="px-6 py-4 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Ações</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="doc in documentosFiltrados" :key="doc.id" class="hover:bg-gray-50 transition-colors">
              <td class="px-6 py-4 whitespace-nowrap">
                <!-- Trocado <a> por <button> chamando a função segura -->
                <button
                  @click="baixarDocumento(doc.id, doc.nome_arquivo)"
                  class="flex items-center gap-2 text-sm font-medium text-[#19341a] hover:text-[#ff8a65] cursor-pointer"
                >
                  <svg class="w-5 h-5 text-red-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd"></path>
                  </svg>
                  {{ doc.nome_arquivo }}
                </button>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                {{ getNomeCliente(doc.client_id) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(doc.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button
                  @click="handleExcluirDocumento(doc.id, doc.nome_arquivo)"
                  class="text-red-600 hover:text-red-900 font-semibold"
                >
                  Excluir
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- MODAL DE UPLOAD -->
    <div v-if="isModalOpen" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-md p-6">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-lg font-semibold text-[#19341a]">Enviar Novo Documento</h3>
          <button @click="isModalOpen = false" class="text-gray-400 hover:text-gray-600 text-xl font-bold">&times;</button>
        </div>

        <form @submit.prevent="handleUpload" class="space-y-5">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Vincular a qual Cliente?</label>
            <select
              v-model="docForm.client_id"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#ff8a65] bg-white text-sm"
            >
              <option value="" disabled>Selecione um cliente...</option>
              <option v-for="cliente in clientes" :key="cliente.id" :value="cliente.id">
                {{ cliente.nome || cliente.razao_social }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Selecionar Arquivo</label>
            <input
              type="file"
              @change="handleFileChange"
              required
              class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-[#19341a]/10 file:text-[#19341a] hover:file:bg-[#19341a]/20 cursor-pointer"
            />
          </div>

          <div class="mt-6 flex justify-end gap-3">
            <button
              type="button"
              @click="isModalOpen = false"
              class="px-4 py-2 text-gray-600 font-medium hover:bg-gray-100 rounded-lg transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              :disabled="isUploading || !selectedFile"
              class="px-4 py-2 bg-[#ff8a65] hover:bg-[#f07047] text-white font-medium rounded-lg disabled:opacity-50 transition-colors shadow-sm"
            >
              {{ isUploading ? 'Enviando...' : 'Fazer Upload' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Layout>
</template>