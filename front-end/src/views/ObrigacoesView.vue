<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '../services/api'
import Layout from '../components/Layout.vue'
import { toast } from 'vue3-toastify'

// 1. Tipagem (Prevenção de Bugs)
interface Cliente {
  id: string | number
  razao_social?: string
  nome?: string // Adicionado suporte para Pessoa Física
}

interface Obrigacao {
  id: string | number
  title: string
  description?: string
  status: string
  due_date: string
  client_id: string | number
  type?: 'custom' | 'receita_federal'
}

// Estados
const obrigacoes = ref<Obrigacao[]>([])
const clientes = ref<Cliente[]>([])
const isLoading = ref(true)

// Filtros Reativos
const filtroClienteId = ref('')
const searchQuery = ref('')

// 2. Computed Property (O Motor de Busca)
const obrigacoesFiltradas = computed(() => {
  let resultado = obrigacoes.value

  // Filtro 1: Dropdown de Cliente
  if (filtroClienteId.value) {
    resultado = resultado.filter((obrigacao) => obrigacao.client_id === filtroClienteId.value)
  }

  // Filtro 2: Barra de Pesquisa de Texto
  if (searchQuery.value) {
    const termoBusca = searchQuery.value.toLowerCase()
    resultado = resultado.filter((obrigacao) =>
      obrigacao.title.toLowerCase().includes(termoBusca) ||
      (obrigacao.description && obrigacao.description.toLowerCase().includes(termoBusca))
    )
  }

  return resultado
})

// Controle do Modal de Detalhes
const isDetalhesModalOpen = ref(false)
const obrigacaoSelecionada = ref<Obrigacao | null>(null)

const abrirDetalhes = (obrigacao: Obrigacao) => {
  obrigacaoSelecionada.value = obrigacao
  isDetalhesModalOpen.value = true
}

const fecharDetalhes = () => {
  isDetalhesModalOpen.value = false
  obrigacaoSelecionada.value = null
}

// Sincronização com o Backend
const fetchData = async () => {
  isLoading.value = true
  try {
    const [obrigacoesRes, clientesRes] = await Promise.all([
      api.get('/api/v1/obrigacoes'),
      api.get('/api/v1/clientes'),
    ])
    obrigacoes.value = obrigacoesRes.data
    clientes.value = clientesRes.data
  } catch (error) {
    toast.error('Erro ao carregar as obrigações e clientes.')
    console.error(error)
  } finally {
    isLoading.value = false
  }
}

// Helpers da Interface
const getNomeCliente = (clientId: string | number) => {
  const cliente = clientes.value.find((c) => c.id === clientId)
  // Checa primeiro se tem NOME (Física), senão usa RAZÃO SOCIAL (Jurídica)
  if (cliente) {
    return cliente.nome || cliente.razao_social || 'Nome Indisponível'
  }
  return 'Não vinculado / Federal'
}

const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  const [year, month, day] = dateString.split('-')
  return `${day}/${month}/${year}`
}

const getStatusBadge = (status: string) => {
  const styles: Record<string, string> = {
    'concluida': 'bg-emerald-100 text-emerald-800 border-emerald-200',
    'em_andamento': 'bg-blue-100 text-blue-800 border-blue-200',
    'aguardando_cliente': 'bg-orange-100 text-orange-800 border-orange-200',
    'pendente': 'bg-yellow-100 text-yellow-800 border-yellow-200'
  }

  const labels: Record<string, string> = {
    'concluida': 'Concluída',
    'em_andamento': 'Em Andamento',
    'aguardando_cliente': 'Aguard. Cliente',
    'pendente': 'Pendente'
  }

  return {
    class: `px-2.5 py-0.5 rounded-full text-xs font-semibold border ${styles[status] || styles['pendente']}`,
    label: labels[status] || 'Pendente'
  }
}

onMounted(() => fetchData())
</script>

<template>
  <Layout title="Controle de Obrigações">

    <header class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Obrigações e Tarefas</h1>
      <p class="text-gray-500 text-sm mt-1">Gerencie os prazos e pendências do seu escritório.</p>
    </header>

    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
      <div class="flex flex-col sm:flex-row gap-3 w-full sm:w-auto sm:max-w-2xl">

        <div class="relative w-full sm:w-64">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
          </div>
          <input v-model="searchQuery" type="text" placeholder="Buscar por nome..."
            class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-coral focus:border-brand-coral text-sm transition-all shadow-sm" />
        </div>

        <select v-model="filtroClienteId"
          class="w-full sm:w-60 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-coral bg-white text-gray-700 cursor-pointer text-sm shadow-sm">
          <option value="">🏢 Todos os Clientes</option>
          <option v-for="cliente in clientes" :key="cliente.id" :value="cliente.id">
            {{ cliente.nome || cliente.razao_social }}
          </option>
        </select>
      </div>

      <button
        class="w-full sm:w-auto bg-[#ff8a65] hover:bg-[#f07047] text-white font-semibold py-2.5 px-5 rounded-xl transition-all flex items-center justify-center gap-2 whitespace-nowrap shadow-sm">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
        </svg>
        <span>Nova Obrigação</span>
      </button>
    </div>

    <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">

      <div v-if="isLoading" class="p-10 text-center text-gray-500">
        Sincronizando obrigações...
      </div>

      <div v-else-if="obrigacoesFiltradas.length === 0" class="p-16 text-center flex flex-col items-center">
        <div class="h-16 w-16 bg-gray-50 rounded-full flex items-center justify-center mb-4">
          <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z">
            </path>
          </svg>
        </div>
        <h3 class="text-lg font-bold text-gray-900 mb-1">Nenhuma obrigação encontrada</h3>
        <p class="text-sm text-gray-500 max-w-md">Não localizamos nenhuma tarefa com os filtros atuais. Tente limpar a
          busca ou selecionar outro cliente.</p>
        <button v-if="searchQuery || filtroClienteId" @click="searchQuery = ''; filtroClienteId = ''"
          class="mt-4 text-brand-coral font-bold text-sm hover:underline">
          Limpar Filtros
        </button>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Arquivo</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Cliente</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Data</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
              <th class="px-6 py-4 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Ações</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="obrigacao in obrigacoesFiltradas" :key="obrigacao.id"
              class="hover:bg-gray-50 transition-colors group">

              <td class="px-6 py-4">
                <div class="text-sm font-bold text-[#19341a]">{{ obrigacao.title }}</div>
                <div v-if="obrigacao.description" class="text-xs text-[#2a2a2a]/60 truncate max-w-xs mt-0.5">
                  {{ obrigacao.description }}
                </div>
              </td>

              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700 font-medium">
                {{ getNomeCliente(obrigacao.client_id) }}
              </td>

              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(obrigacao.due_date) }}
              </td>

              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusBadge(obrigacao.status).class">
                  {{ getStatusBadge(obrigacao.status).label }}
                </span>
              </td>

              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button @click="abrirDetalhes(obrigacao)"
                  class="text-gray-600 hover:text-gray-900 font-semibold transition-colors">
                  Ver Detalhes
                </button>
              </td>

            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="obrigacoesFiltradas.length > 0"
        class="bg-white px-6 py-3 border-t border-gray-200 flex justify-between items-center text-xs text-gray-500">
        <span>Mostrando <strong>{{ obrigacoesFiltradas.length }}</strong> registros</span>
      </div>

    </div>
    <div v-if="isDetalhesModalOpen && obrigacaoSelecionada"
      class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden">

        <div class="px-6 py-5 border-b border-gray-100 flex justify-between items-center bg-[#f8f8f8]">
          <h3 class="text-xl font-bold text-[#19341a] flex items-center gap-2">
            <span v-if="obrigacaoSelecionada.type === 'receita_federal'">🏛️</span>
            Detalhes da Tarefa
          </h3>
          <button @click="fecharDetalhes"
            class="text-gray-400 hover:text-gray-600 text-2xl font-bold transition-colors">
            &times;
          </button>
        </div>

        <div class="p-6 space-y-5">
          <div>
            <span class="block text-xs font-bold text-[#2a2a2a]/40 uppercase tracking-wider mb-1">Título</span>
            <p class="text-[#19341a] font-bold text-lg">{{ obrigacaoSelecionada.title }}</p>
          </div>

          <div v-if="obrigacaoSelecionada.description">
            <span class="block text-xs font-bold text-[#2a2a2a]/40 uppercase tracking-wider mb-1">Descrição /
              Instruções</span>
            <p class="text-[#2a2a2a]/70 text-sm whitespace-pre-wrap bg-gray-50 p-3 rounded-lg border border-gray-100">{{
              obrigacaoSelecionada.description }}</p>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <span class="block text-xs font-bold text-[#2a2a2a]/40 uppercase tracking-wider mb-1">Vínculo</span>
              <p class="text-[#2a2a2a]/80 text-sm font-semibold">{{ getNomeCliente(obrigacaoSelecionada.client_id) }}
              </p>
            </div>
            <div>
              <span class="block text-xs font-bold text-[#2a2a2a]/40 uppercase tracking-wider mb-1">Prazo Limite</span>
              <p class="text-[#2a2a2a]/80 text-sm font-semibold">{{ formatDate(obrigacaoSelecionada.due_date) }}</p>
            </div>
          </div>

          <div>
            <span class="block text-xs font-bold text-[#2a2a2a]/40 uppercase tracking-wider mb-2">Status Atual</span>
            <span :class="getStatusBadge(obrigacaoSelecionada.status).class">
              {{ getStatusBadge(obrigacaoSelecionada.status).label }}
            </span>
          </div>
        </div>

        <div class="px-6 py-4 border-t border-gray-100 flex justify-end">
          <button @click="fecharDetalhes"
            class="px-6 py-2.5 bg-white border border-gray-200 text-[#2a2a2a]/70 font-semibold hover:bg-gray-50 rounded-xl transition-colors shadow-sm">
            Fechar
          </button>
        </div>

      </div>
    </div>
  </Layout>
</template>