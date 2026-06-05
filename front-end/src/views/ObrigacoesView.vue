<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../services/api'
import Layout from '../components/Layout.vue'
import { toast } from 'vue3-toastify'

// Estados
const tasks = ref<any[]>([])
const clients = ref<any[]>([]) // Para popular o dropdown e mostrar o nome na tabela
const isLoading = ref(true)

// Controle do Modal
const isModalOpen = ref(false)
const isSubmitting = ref(false)

// Dados da nova obrigação
const newTask = ref({
  title: '',
  description: '',
  due_date: '',
  status: 'pendente',
  client_id: '',
})

// Erros de validação
const formErrors = ref({
  title: '',
  client_id: '',
  due_date: '',
})

// Função para definir a cor do badge de status
const getStatusClass = (status: string) => {
  switch (status) {
    case 'concluida':
      return 'bg-green-100 text-green-800'
    case 'em_andamento':
      return 'bg-blue-100 text-blue-800'
    case 'aguardando_cliente':
      return 'bg-orange-100 text-orange-800'
    case 'pendente':
      return 'bg-yellow-100 text-yellow-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

// Formata a data para o padrão brasileiro (DD/MM/YYYY)
const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  const date = new Date(dateString + 'T00:00:00') // Evita bug de fuso horário
  return date.toLocaleDateString('pt-BR')
}

// Helper: Buscar nome do Cliente pelo ID
const getNomeCliente = (clientId: string) => {
  const cliente = clients.value.find((c) => c.id === clientId)
  return cliente ? cliente.razao_social : 'Cliente não encontrado'
}

// 1. Busca as obrigações
const fetchTasks = async () => {
  try {
    const response = await api.get('/api/v1/obrigacoes')
    tasks.value = response.data
  } catch (error) {
    toast.error('Erro ao carregar obrigações.')
  } finally {
    isLoading.value = false
  }
}

// 2. Busca os clientes
const fetchClients = async () => {
  try {
    const response = await api.get('/api/v1/clientes')
    clients.value = response.data
  } catch (error) {
    toast.error('Erro ao carregar a lista de clientes.')
  }
}

// 3. Validação do Formulário
const validateForm = () => {
  let isValid = true
  formErrors.value = { title: '', client_id: '', due_date: '' }

  if (!newTask.value.title) {
    formErrors.value.title = 'O título da obrigação é obrigatório.'
    isValid = false
  }
  if (!newTask.value.client_id) {
    formErrors.value.client_id = 'Selecione um cliente.'
    isValid = false
  }
  if (!newTask.value.due_date) {
    formErrors.value.due_date = 'A data de vencimento é obrigatória.'
    isValid = false
  }

  return isValid
}

// 4. Salva a nova obrigação
const handleCreateTask = async () => {
  if (!validateForm()) {
    toast.warning('Por favor, corrija os erros no formulário.')
    return
  }

  isSubmitting.value = true
  try {
    const response = await api.post('/api/v1/obrigacoes', newTask.value)

    tasks.value.unshift(response.data) // Adiciona no topo da lista
    newTask.value = { title: '', description: '', due_date: '', status: 'pendente', client_id: '' }
    isModalOpen.value = false

    toast.success('Obrigação criada com sucesso!')
  } catch (error: any) {
    const detail = error.response?.data?.detail || 'Erro ao criar a obrigação.'
    toast.error(detail)
  } finally {
    isSubmitting.value = false
  }
}

// 5. Concluir Obrigação
const handleConcluir = async (taskId: string) => {
  try {
    const response = await api.patch(`/api/v1/obrigacoes/${taskId}/concluir`)
    const index = tasks.value.findIndex((t) => t.id === taskId)
    if (index !== -1) {
      tasks.value[index] = response.data // Atualiza a lista localmente
    }
    toast.success('Obrigação marcada como concluída!')
  } catch (error) {
    toast.error('Erro ao concluir a obrigação.')
  }
}

// 6. Excluir Obrigação
const handleDelete = async (taskId: string) => {
  if (!window.confirm('Tem certeza que deseja excluir esta obrigação?')) return

  try {
    await api.delete(`/api/v1/obrigacoes/${taskId}`)
    tasks.value = tasks.value.filter((t) => t.id !== taskId)
    toast.success('Obrigação excluída com sucesso.')
  } catch (error) {
    toast.error('Erro ao excluir a obrigação.')
  }
}

onMounted(() => {
  fetchTasks()
  fetchClients()
})
</script>

<template>
  <Layout title="Obrigações e Prazos">
    <!-- Barra de Ações Responsiva -->
    <div class="flex flex-col sm:flex-row items-center justify-between gap-4 mb-6">
      <div class="relative w-full sm:w-72">
        <input
          type="text"
          placeholder="Buscar obrigação..."
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
        <span>Nova Obrigação</span>
      </button>
    </div>

    <!-- Tabela com Overflow Responsivo -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div v-if="isLoading" class="p-8 text-center text-gray-500">Carregando obrigações...</div>
      <div v-else-if="tasks.length === 0" class="p-8 text-center text-gray-500">
        Nenhuma obrigação cadastrada ainda.
      </div>

      <!-- WRAPPER MÁGICO: Permite rolar a tabela no mobile -->
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th
                class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider"
              >
                Título
              </th>
              <th
                class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider"
              >
                Cliente
              </th>
              <th
                class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider"
              >
                Vencimento
              </th>
              <th
                class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider"
              >
                Status
              </th>
              <th
                class="px-6 py-4 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider"
              >
                Ações
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="task in tasks" :key="task.id" class="hover:bg-gray-50 transition-colors">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ task.title }}</div>
                <div v-if="task.description" class="text-xs text-gray-500 truncate max-w-xs">
                  {{ task.description }}
                </div>
              </td>
              <!-- CORREÇÃO: Mostra o Nome do Cliente em vez do ID -->
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                {{ getNomeCliente(task.client_id) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                {{ formatDate(task.due_date) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                  :class="getStatusClass(task.status)"
                >
                  {{ task.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center text-sm font-medium space-x-2">
                <button
                  v-if="task.status !== 'concluida'"
                  @click="handleConcluir(task.id)"
                  class="text-green-600 hover:text-green-900 font-semibold"
                >
                  Concluir
                </button>
                <button
                  @click="handleDelete(task.id)"
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

    <!-- MODAL DE CADASTRO -->
    <div
      v-if="isModalOpen"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
    >
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-md overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center">
          <h3 class="text-lg font-semibold text-gray-800">Nova Obrigação</h3>
          <button
            @click="isModalOpen = false"
            class="text-gray-400 hover:text-gray-600 text-xl font-bold"
          >
            &times;
          </button>
        </div>

        <form @submit.prevent="handleCreateTask" class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Título da Obrigação</label>
            <input
              v-model="newTask.title"
              type="text"
              required
              placeholder="Ex: Declaração IRPF 2024"
              class="w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm transition-colors"
              :class="formErrors.title ? 'border-red-500' : 'border-gray-300'"
            />
            <p v-if="formErrors.title" class="text-red-500 text-xs mt-1">{{ formErrors.title }}</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Cliente</label>
            <select
              v-model="newTask.client_id"
              required
              class="w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white text-sm"
              :class="formErrors.client_id ? 'border-red-500' : 'border-gray-300'"
            >
              <option value="" disabled>Selecione um cliente...</option>
              <option v-for="client in clients" :key="client.id" :value="client.id">
                {{ client.razao_social }}
              </option>
            </select>
            <p v-if="formErrors.client_id" class="text-red-500 text-xs mt-1">
              {{ formErrors.client_id }}
            </p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Data de Vencimento</label>
            <input
              v-model="newTask.due_date"
              type="date"
              required
              class="w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
              :class="formErrors.due_date ? 'border-red-500' : 'border-gray-300'"
            />
            <p v-if="formErrors.due_date" class="text-red-500 text-xs mt-1">
              {{ formErrors.due_date }}
            </p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Descrição (Opcional)</label>
            <textarea
              v-model="newTask.description"
              rows="3"
              placeholder="Observações sobre a obrigação..."
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
            ></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Status Inicial</label>
            <select
              v-model="newTask.status"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white text-sm"
            >
              <option value="pendente">Pendente</option>
              <option value="em_andamento">Em Andamento</option>
              <option value="aguardando_cliente">Aguardando Cliente</option>
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
              {{ isSubmitting ? 'Salvando...' : 'Criar Obrigação' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Layout>
</template>
