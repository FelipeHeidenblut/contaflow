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
  razao_social: '',
  cnpj: '',
  regime_tributario: 'Simples Nacional',
})

// Validação simples de erro no formulário
const formErrors = ref({
  razao_social: '',
  cnpj: '',
})

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
  formErrors.value = { razao_social: '', cnpj: '' }

  if (!newClient.value.razao_social) {
    formErrors.value.razao_social = 'A razão social é obrigatória.'
    isValid = false
  }

  const cnpjClean = newClient.value.cnpj.replace(/\D/g, '')
  if (cnpjClean.length < 14) {
    formErrors.value.cnpj = 'CNPJ inválido.'
    isValid = false
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

    clients.value.unshift(response.data) // Adiciona no topo da lista

    // Limpa o formulário e fecha o modal
    newClient.value = { razao_social: '', cnpj: '', regime_tributario: 'Simples Nacional' }
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
    // Remove o cliente da lista da tela instantaneamente
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
          class="w-full pl-4 pr-10 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
        />
      </div>
      <button
        @click="isModalOpen = true"
        class="w-full sm:w-auto bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2 whitespace-nowrap shadow-sm"
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
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div v-if="isLoading" class="p-8 text-center text-gray-500">
        Carregando carteira de clientes...
      </div>
      <div v-else-if="clients.length === 0" class="p-8 text-center text-gray-500">
        Nenhum cliente ativo cadastrado no escritório ainda.
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th
                class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider"
              >
                Razão Social
              </th>
              <th
                class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider"
              >
                CNPJ
              </th>
              <th
                class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider"
              >
                Regime
              </th>
              <th
                class="px-6 py-4 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider"
              >
                Ações
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="client in clients"
              :key="client.id"
              class="hover:bg-gray-50 transition-colors"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ client.razao_social }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{{ client.cnpj }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                <span
                  class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-indigo-50 text-indigo-800"
                >
                  {{ client.regime_tributario }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center text-sm font-medium">
                <button
                  @click="handleDesativar(client.id)"
                  class="text-gray-500 hover:text-red-600 font-semibold transition-colors"
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
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
    >
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-md overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center">
          <h3 class="text-lg font-semibold text-gray-800">Cadastrar Novo Cliente</h3>
          <button
            @click="isModalOpen = false"
            class="text-gray-400 hover:text-gray-600 text-xl font-bold"
          >
            &times;
          </button>
        </div>

        <form @submit.prevent="handleCreateClient" class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Razão Social</label>
            <input
              v-model="newClient.razao_social"
              type="text"
              required
              class="w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm transition-colors"
              :class="formErrors.razao_social ? 'border-red-500' : 'border-gray-300'"
            />
            <p v-if="formErrors.razao_social" class="text-red-500 text-xs mt-1">
              {{ formErrors.razao_social }}
            </p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">CNPJ</label>
            <!-- CORRIGIDO DE CNJP -->
            <input
              v-model="newClient.cnpj"
              v-maska="'##.###.###/####-##'"
              type="text"
              required
              placeholder="00.000.000/0000-00"
              class="w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm transition-colors"
              :class="formErrors.cnpj ? 'border-red-500' : 'border-gray-300'"
            />
            <p v-if="formErrors.cnpj" class="text-red-500 text-xs mt-1">{{ formErrors.cnpj }}</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Regime Tributário</label>
            <select
              v-model="newClient.regime_tributario"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white text-sm"
            >
              <option value="Simples Nacional">Simples Nacional</option>
              <option value="Lucro Presumido">Lucro Presumido</option>
              <option value="Lucro Real">Lucro Real</option>
              <option value="MEI">MEI</option>
            </select>
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
              :disabled="isSubmitting"
              class="px-4 py-2 bg-indigo-600 text-white font-medium hover:bg-indigo-700 rounded-lg transition-colors disabled:opacity-50"
            >
              {{ isSubmitting ? 'Salvando...' : 'Salvar Cliente' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Layout>
</template>
