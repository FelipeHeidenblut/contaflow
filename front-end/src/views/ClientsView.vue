<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../services/api'
import Layout from '../components/Layout.vue'
import { toast } from 'vue3-toastify'
import { vMaska } from 'maska/vue'

const clients = ref<any[]>([])
const isLoading = ref(true)

// Controle do Modal
const isModalOpen = ref(false)
const isSubmitting = ref(false)

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

// Função para trocar o tipo de pessoa e limpar os campos específicos
const setTipoPessoa = (tipo: string) => {
  newClient.value.tipo_pessoa = tipo
  // Limpa os campos ao trocar para não enviar dados sujos na requisição
  if (tipo === 'PJ') {
    newClient.value.nome = ''
    newClient.value.cpf = ''
  } else {
    newClient.value.razao_social = ''
    newClient.value.cnpj = ''
  }
  // Limpa os erros de validação também
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
    // O backend vai receber os campos conforme o tipo selecionado
    const response = await api.post('/api/v1/clientes', newClient.value)

    clients.value.unshift(response.data)

    // Limpa o formulário e fecha o modal
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
  if (
    !window.confirm(
      'Tem certeza que deseja arquivar este cliente? Ele não aparecerá mais na listagem principal, mas os documentos e obrigações ficarão salvos para auditoria.',
    )
  )
    return

  try {
    await api.patch(`/api/v1/clientes/${clientId}/desativar`)
    clients.value = clients.value.filter((c) => c.id !== clientId)
    toast.success('Cliente arquivado com sucesso.')
  } catch (error) {
    toast.error('Erro ao arquivar o cliente.')
  }
}

onMounted(() => {
  fetchClients()
})
</script>

<template>
  <Layout title="Gerenciar Clientes">
    <!-- Barra de Ações Responsiva -->
    <div class="flex flex-col sm:flex-row items-center justify-between gap-4 mb-6">
      <div class="relative w-full sm:w-72">
        <input
          type="text"
          placeholder="Buscar cliente..."
          class="w-full pl-4 pr-10 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#ff8a65] focus:border-transparent text-sm bg-white"
        />
      </div>
      <button
        @click="isModalOpen = true"
        class="w-full sm:w-auto bg-[#ff8a65] hover:bg-[#f07047] text-white font-semibold py-2.5 px-5 rounded-xl transition-all flex items-center justify-center gap-2 whitespace-nowrap shadow-sm"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 4v16m8-8H4"
          ></path>
        </svg>
        <span>Novo Cliente</span>
      </button>
    </div>

    <!-- Tabela com Overflow Responsivo -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-200/80 overflow-hidden">
      <div v-if="isLoading" class="p-8 text-center text-[#2a2a2a]/50">
        Carregando carteira de clientes...
      </div>
      <div v-else-if="clients.length === 0" class="p-8 text-center text-[#2a2a2a]/50">
        Nenhum cliente ativo cadastrado no escritório ainda.
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-100">
          <thead class="bg-[#f8f8f8]">
            <tr>
              <th
                class="px-6 py-4 text-left text-xs font-bold text-[#2a2a2a]/50 uppercase tracking-wider"
              >
                Identificação
              </th>
              <th
                class="px-6 py-4 text-left text-xs font-bold text-[#2a2a2a]/50 uppercase tracking-wider"
              >
                Documento
              </th>
              <th
                class="px-6 py-4 text-left text-xs font-bold text-[#2a2a2a]/50 uppercase tracking-wider"
              >
                Regime
              </th>
              <th
                class="px-6 py-4 text-center text-xs font-bold text-[#2a2a2a]/50 uppercase tracking-wider"
              >
                Ações
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-100">
            <tr
              v-for="client in clients"
              :key="client.id"
              class="hover:bg-[#f8f8f8]/50 transition-colors"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <!-- Exibe Razão Social ou Nome dependendo do que vier preenchido do banco -->
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
                <span
                  class="px-2.5 py-1 inline-flex text-xs leading-5 font-semibold rounded-lg bg-[#eaf3ea] text-[#19341a]"
                >
                  {{ client.regime_tributario }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center text-sm font-medium">
                <button
                  @click="handleDesativar(client.id)"
                  class="text-[#2a2a2a]/40 hover:text-red-500 font-semibold transition-colors"
                >
                  Arquivar
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- MODAL DE CADASTRO -->
    <div
      v-if="isModalOpen"
      class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
    >
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
        <div class="px-6 py-5 border-b border-gray-100 flex justify-between items-center">
          <h3 class="text-xl font-bold text-[#19341a]">Cadastrar Cliente</h3>
          <button
            @click="isModalOpen = false"
            class="text-gray-400 hover:text-gray-600 text-2xl font-bold"
          >
            &times;
          </button>
        </div>

        <form @submit.prevent="handleCreateClient" class="p-6 space-y-5">
          <!-- Toggle Pessoa Física / Jurídica -->
          <div class="flex gap-2 bg-[#f8f8f8] p-1.5 rounded-xl">
            <button
              type="button"
              @click="setTipoPessoa('PJ')"
              class="flex-1 py-2.5 text-sm font-semibold rounded-lg transition-all"
              :class="
                newClient.tipo_pessoa === 'PJ'
                  ? 'bg-white text-[#19341a] shadow-sm'
                  : 'text-[#2a2a2a]/50 hover:text-[#2a2a2a]'
              "
            >
              Pessoa Jurídica
            </button>
            <button
              type="button"
              @click="setTipoPessoa('PF')"
              class="flex-1 py-2.5 text-sm font-semibold rounded-lg transition-all"
              :class="
                newClient.tipo_pessoa === 'PF'
                  ? 'bg-white text-[#19341a] shadow-sm'
                  : 'text-[#2a2a2a]/50 hover:text-[#2a2a2a]'
              "
            >
              Pessoa Física
            </button>
          </div>

          <!-- Campos Dinâmicos PJ -->
          <template v-if="newClient.tipo_pessoa === 'PJ'">
            <div>
              <label class="block text-sm font-medium text-[#2a2a2a]/70 mb-1.5">Razão Social</label>
              <input
                v-model="newClient.razao_social"
                type="text"
                required
                placeholder="Empresa LTDA"
                class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#ff8a65] focus:border-transparent text-sm transition-colors"
                :class="formErrors.razao_social ? 'border-red-400 bg-red-50/30' : ''"
              />
              <p v-if="formErrors.razao_social" class="text-red-500 text-xs mt-1.5">
                {{ formErrors.razao_social }}
              </p>
            </div>
            <div>
              <label class="block text-sm font-medium text-[#2a2a2a]/70 mb-1.5">CNPJ</label>
              <input
                v-model="newClient.cnpj"
                v-maska="'##.###.###/####-##'"
                type="text"
                required
                placeholder="00.000.000/0000-00"
                class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#ff8a65] focus:border-transparent text-sm transition-colors"
                :class="formErrors.cnpj ? 'border-red-400 bg-red-50/30' : ''"
              />
              <p v-if="formErrors.cnpj" class="text-red-500 text-xs mt-1.5">
                {{ formErrors.cnpj }}
              </p>
            </div>
          </template>

          <!-- Campos Dinâmicos PF -->
          <template v-if="newClient.tipo_pessoa === 'PF'">
            <div>
              <label class="block text-sm font-medium text-[#2a2a2a]/70 mb-1.5"
                >Nome Completo</label
              >
              <input
                v-model="newClient.nome"
                type="text"
                required
                placeholder="João da Silva"
                class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#ff8a65] focus:border-transparent text-sm transition-colors"
                :class="formErrors.nome ? 'border-red-400 bg-red-50/30' : ''"
              />
              <p v-if="formErrors.nome" class="text-red-500 text-xs mt-1.5">
                {{ formErrors.nome }}
              </p>
            </div>
            <div>
              <label class="block text-sm font-medium text-[#2a2a2a]/70 mb-1.5">CPF</label>
              <input
                v-model="newClient.cpf"
                v-maska="'###.###.###-##'"
                type="text"
                required
                placeholder="000.000.000-00"
                class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#ff8a65] focus:border-transparent text-sm transition-colors"
                :class="formErrors.cpf ? 'border-red-400 bg-red-50/30' : ''"
              />
              <p v-if="formErrors.cpf" class="text-red-500 text-xs mt-1.5">{{ formErrors.cpf }}</p>
            </div>
          </template>

          <div>
            <label class="block text-sm font-medium text-[#2a2a2a]/70 mb-1.5"
              >Regime Tributário</label
            >
            <select
              v-model="newClient.regime_tributario"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#ff8a65] focus:border-transparent bg-white text-sm"
            >
              <option value="Simples Nacional">Simples Nacional</option>
              <option value="Lucro Presumido">Lucro Presumido</option>
              <option value="Lucro Real">Lucro Real</option>
              <option value="MEI">MEI</option>
            </select>
          </div>

          <div class="mt-8 flex justify-end gap-3">
            <button
              type="button"
              @click="isModalOpen = false"
              class="px-5 py-2.5 text-[#2a2a2a]/60 font-semibold hover:bg-gray-100 rounded-xl transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              :disabled="isSubmitting"
              class="px-6 py-2.5 bg-[#ff8a65] text-white font-semibold hover:bg-[#f07047] rounded-xl transition-colors disabled:opacity-50 shadow-sm"
            >
              {{ isSubmitting ? 'Salvando...' : 'Salvar Cliente' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Layout>
</template>
