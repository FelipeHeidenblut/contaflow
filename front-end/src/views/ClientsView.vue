<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '../services/api'
import Layout from '../components/Layout.vue'
import { toast } from 'vue3-toastify'
import { vMaska } from 'maska/vue'

const clients = ref<any[]>([])
const isLoading = ref(true)

// Controle do Modal de Cadastro
const isModalOpen = ref(false)
const isSubmitting = ref(false)

// Estado da busca por texto
const searchQuery = ref('')

// Dados do novo cliente
const newClient = ref({
  tipo_pessoa: 'PJ', // 'PJ' para Jurídica, 'PF' para Física
  razao_social: '',
  cnpj: '',
  nome: '', // Novo campo para PF
  cpf: '', // Novo campo para PF
  regime_tributario: 'Simples Nacional',
})

// Validação de erro no formulário
const formErrors = ref({
  razao_social: '',
  cnpj: '',
  nome: '',
  cpf: '',
})

// O MOTOR DE BUSCA: Filtra por nome, razão social, CNPJ ou CPF
const clientsFiltrados = computed(() => {
  const termo = searchQuery.value.trim().toLowerCase()

  if (!termo) {
    return clients.value
  }

  return clients.value.filter((client) => {
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

// Função para trocar o tipo de pessoa e limpar os campos
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

// 1. Busca os clientes
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

// 2. Validação Frontend antes de enviar
const validateForm = () => {
  let isValid = true
  formErrors.value = { razao_social: '', cnpj: '', nome: '', cpf: '' }

  if (newClient.value.tipo_pessoa === 'PJ') {
    if (!newClient.value.razao_social) {
      formErrors.value.razao_social = 'A razão social é obrigatória.'
      isValid = false
    }
    const cnpjClean = newClient.value.cnpj.replace(/\D/g, '')
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

// 3. Salva o novo cliente
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

// 4. Arquivar (Soft Delete)
const handleDesativar = async (clientId: string) => {
  if (!window.confirm('Tem certeza que deseja arquivar este cliente? Ele não aparecerá mais na listagem principal.')) return

  try {
    await api.patch(`/api/v1/clientes/${clientId}/desativar`)
    clients.value = clients.value.filter((c) => c.id !== clientId)
    toast.success('Cliente arquivado com sucesso.')
  } catch (error) {
    toast.error('Erro ao arquivar o cliente.')
  }
}

// ==========================================
// IMPORTAÇÃO DE CSV - LÓGICA
// ==========================================
const isImportModalOpen = ref(false)
const isUploadingCsv = ref(false)
const csvFile = ref<File | null>(null)

// Captura o arquivo
const handleCsvChange = (event: any) => {
  const file = event.target.files[0]
  if (file && file.name.endsWith('.csv')) {
    csvFile.value = file
  } else {
    toast.error("Por favor, selecione apenas arquivos .csv")
    event.target.value = '' // Reseta o input visualmente
    csvFile.value = null
  }
}

// Envia o arquivo para o Back-end
const handleUploadCsv = async () => {
  if (!csvFile.value) return
  isUploadingCsv.value = true

  try {
    const formData = new FormData()
    formData.append('file', csvFile.value)

    const response = await api.post('/api/v1/clientes/importar-csv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    const { importados, erros } = response.data
    
    if (importados > 0) {
      toast.success(`${importados} clientes importados com sucesso!`)
      fetchClients() // Sincroniza a tabela na mesma hora
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

// Gera o Template CSV no navegador para download (Sem precisar de backend)
const baixarTemplate = () => {
  const cabecalhos = "TIPO (PF/PJ);NOME_OU_RAZAO;CPF_OU_CNPJ;REGIME_TRIBUTARIO\n"
  const exemplo1 = "PJ;Transportes LTDA;12.345.678/0001-90;Simples Nacional\n"
  const exemplo2 = "PF;João da Silva;123.456.789-00;MEI\n"
  
  const blob = new Blob([cabecalhos + exemplo1 + exemplo2], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement("a")
  link.setAttribute("href", url)
  link.setAttribute("download", "template_clientes.csv")
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
    <div class="flex flex-col sm:flex-row items-center justify-between gap-4 mb-6">
      <div class="relative w-full sm:w-72">
        <input v-model="searchQuery" type="text" placeholder="Buscar cliente..."
          class="w-full pl-4 pr-10 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#ff8a65] focus:border-transparent text-sm bg-white" />
      </div>
      
      <div class="flex gap-3 w-full sm:w-auto">
        <button @click="isImportModalOpen = true"
          class="w-full sm:w-auto bg-white border border-gray-200 text-[#2a2a2a]/80 font-bold py-2.5 px-5 rounded-xl hover:bg-gray-50 transition-all flex items-center justify-center gap-2 shadow-sm">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>
          <span>Importar CSV</span>
        </button>

        <button @click="isModalOpen = true"
          class="w-full sm:w-auto bg-[#ff8a65] hover:bg-[#f07047] text-white font-bold py-2.5 px-5 rounded-xl transition-all flex items-center justify-center gap-2 whitespace-nowrap shadow-sm">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          <span>Novo Cliente</span>
        </button>
      </div>
    </div>

    <div class="bg-white rounded-2xl shadow-sm border border-gray-200/80 overflow-hidden">
      <div v-if="isLoading" class="p-8 text-center text-[#2a2a2a]/50">
        Carregando carteira de clientes...
      </div>
      <div v-else-if="clients.length === 0" class="p-8 text-center text-[#2a2a2a]/50">
        Nenhum cliente ativo cadastrado no escritório ainda.
      </div>
      <div v-else-if="clientsFiltrados.length === 0" class="p-12 text-center text-gray-500 text-sm">
        Nenhum cliente corresponde à sua busca por "{{ searchQuery }}".
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-100">
          <thead class="bg-[#f8f8f8]">
            <tr>
              <th class="px-6 py-4 text-left text-xs font-bold text-[#2a2a2a]/50 uppercase tracking-wider">Identificação</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-[#2a2a2a]/50 uppercase tracking-wider">Documento</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-[#2a2a2a]/50 uppercase tracking-wider">Regime</th>
              <th class="px-6 py-4 text-center text-xs font-bold text-[#2a2a2a]/50 uppercase tracking-wider">Ações</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-100">
            <tr v-for="client in clientsFiltrados" :key="client.id" class="hover:bg-[#f8f8f8]/50 transition-colors">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-semibold text-[#19341a]">
                  {{ client.razao_social || client.nome }}
                </div>
                <div class="text-xs text-[#2a2a2a]/40 mt-0.5">
                  {{ client.razao_social ? 'Pessoa Jurídica' : 'Pessoa Física' }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-[#2a2a2a]/70">
                {{ client.cnpj || client.cpf }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <span class="px-2.5 py-1 inline-flex text-xs leading-5 font-semibold rounded-lg bg-[#eaf3ea] text-[#19341a]">
                  {{ client.regime_tributario }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center text-sm font-medium">
                <button @click="handleDesativar(client.id)"
                  class="text-[#2a2a2a]/40 hover:text-red-500 font-semibold transition-colors">
                  Arquivar
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="isModalOpen" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
        <div class="px-6 py-5 border-b border-gray-100 flex justify-between items-center">
          <h3 class="text-xl font-bold text-[#19341a]">Cadastrar Cliente</h3>
          <button @click="isModalOpen = false" class="text-gray-400 hover:text-gray-600 text-2xl font-bold">&times;</button>
        </div>

        <form @submit.prevent="handleCreateClient" class="p-6 space-y-5">
          <div class="flex gap-2 bg-[#f8f8f8] p-1.5 rounded-xl">
            <button type="button" @click="setTipoPessoa('PJ')"
              class="flex-1 py-2.5 text-sm font-semibold rounded-lg transition-all"
              :class="newClient.tipo_pessoa === 'PJ' ? 'bg-white text-[#19341a] shadow-sm' : 'text-[#2a2a2a]/50 hover:text-[#2a2a2a]'">
              Pessoa Jurídica
            </button>
            <button type="button" @click="setTipoPessoa('PF')"
              class="flex-1 py-2.5 text-sm font-semibold rounded-lg transition-all"
              :class="newClient.tipo_pessoa === 'PF' ? 'bg-white text-[#19341a] shadow-sm' : 'text-[#2a2a2a]/50 hover:text-[#2a2a2a]'">
              Pessoa Física
            </button>
          </div>

          <template v-if="newClient.tipo_pessoa === 'PJ'">
            <div>
              <label class="block text-sm font-medium text-[#2a2a2a]/70 mb-1.5">Razão Social</label>
              <input v-model="newClient.razao_social" type="text" required placeholder="Empresa LTDA"
                class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#ff8a65] focus:border-transparent text-sm transition-colors"
                :class="formErrors.razao_social ? 'border-red-400 bg-red-50/30' : ''" />
              <p v-if="formErrors.razao_social" class="text-red-500 text-xs mt-1.5">{{ formErrors.razao_social }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-[#2a2a2a]/70 mb-1.5">CNPJ</label>
              <input v-model="newClient.cnpj" v-maska="'##.###.###/####-##'" type="text" required placeholder="00.000.000/0000-00"
                class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#ff8a65] focus:border-transparent text-sm transition-colors"
                :class="formErrors.cnpj ? 'border-red-400 bg-red-50/30' : ''" />
              <p v-if="formErrors.cnpj" class="text-red-500 text-xs mt-1.5">{{ formErrors.cnpj }}</p>
            </div>
          </template>

          <template v-if="newClient.tipo_pessoa === 'PF'">
            <div>
              <label class="block text-sm font-medium text-[#2a2a2a]/70 mb-1.5">Nome Completo</label>
              <input v-model="newClient.nome" type="text" required placeholder="João da Silva"
                class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#ff8a65] focus:border-transparent text-sm transition-colors"
                :class="formErrors.nome ? 'border-red-400 bg-red-50/30' : ''" />
              <p v-if="formErrors.nome" class="text-red-500 text-xs mt-1.5">{{ formErrors.nome }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-[#2a2a2a]/70 mb-1.5">CPF</label>
              <input v-model="newClient.cpf" v-maska="'###.###.###-##'" type="text" required placeholder="000.000.000-00"
                class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#ff8a65] focus:border-transparent text-sm transition-colors"
                :class="formErrors.cpf ? 'border-red-400 bg-red-50/30' : ''" />
              <p v-if="formErrors.cpf" class="text-red-500 text-xs mt-1.5">{{ formErrors.cpf }}</p>
            </div>
          </template>

          <div>
            <label class="block text-sm font-medium text-[#2a2a2a]/70 mb-1.5">Regime Tributário</label>
            <select v-model="newClient.regime_tributario" class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#ff8a65] focus:border-transparent bg-white text-sm">
              <option value="Simples Nacional">Simples Nacional</option>
              <option value="Lucro Presumido">Lucro Presumido</option>
              <option value="Lucro Real">Lucro Real</option>
              <option value="MEI">MEI</option>
            </select>
          </div>

          <div class="mt-8 flex justify-end gap-3">
            <button type="button" @click="isModalOpen = false" class="px-5 py-2.5 text-[#2a2a2a]/60 font-semibold hover:bg-gray-100 rounded-xl transition-colors">
              Cancelar
            </button>
            <button type="submit" :disabled="isSubmitting" class="px-6 py-2.5 bg-[#ff8a65] text-white font-semibold hover:bg-[#f07047] rounded-xl transition-colors disabled:opacity-50 shadow-sm">
              {{ isSubmitting ? 'Salvando...' : 'Salvar Cliente' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="isImportModalOpen" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
        <div class="px-6 py-5 border-b border-gray-100 flex justify-between items-center bg-[#f8f8f8]">
          <h3 class="text-xl font-bold text-[#19341a]">Importar Clientes</h3>
          <button @click="isImportModalOpen = false" class="text-gray-400 hover:text-gray-600 text-2xl font-bold">&times;</button>
        </div>

        <div class="p-6 space-y-6">
          <div class="bg-blue-50 border border-blue-100 p-4 rounded-xl">
            <h4 class="text-sm font-bold text-blue-800 mb-2">Como importar?</h4>
            <ol class="text-xs text-blue-700 space-y-1 list-decimal list-inside">
              <li>Baixe o template de exemplo abaixo.</li>
              <li>Preencha com os dados do seu sistema (sem alterar cabeçalhos).</li>
              <li>Salve como "CSV (separado por vírgulas)".</li>
              <li>Faça o upload do arquivo aqui.</li>
            </ol>
            <button @click="baixarTemplate" class="mt-3 text-xs font-bold text-blue-600 hover:text-blue-800 underline flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
              Baixar Template CSV
            </button>
          </div>

          <div>
            <label class="block text-sm font-bold text-[#2a2a2a]/70 mb-2">Arquivo CSV</label>
            <input
              type="file"
              accept=".csv"
              @change="handleCsvChange"
              class="w-full text-sm text-gray-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-bold file:bg-[#19341a]/10 file:text-[#19341a] hover:file:bg-[#19341a]/20 cursor-pointer border border-gray-200 rounded-xl p-1"
            />
          </div>

          <div class="mt-8 flex justify-end gap-3">
            <button @click="isImportModalOpen = false" class="px-5 py-2.5 text-[#2a2a2a]/60 font-bold hover:bg-gray-100 rounded-xl transition-colors">
              Cancelar
            </button>
            <button
              @click="handleUploadCsv"
              :disabled="isUploadingCsv || !csvFile"
              class="px-6 py-2.5 bg-[#19341a] text-white font-bold hover:bg-[#0f2010] rounded-xl transition-colors disabled:opacity-50 shadow-md"
            >
              {{ isUploadingCsv ? 'Processando...' : 'Iniciar Importação' }}
            </button>
          </div>
        </div>
      </div>
    </div>

  </Layout>
</template>