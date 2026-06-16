<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '../services/api'
import Layout from '../components/Layout.vue'
import { toast } from 'vue3-toastify'

// 1. Tipagem
interface Cliente {
  id: string | number
  razao_social?: string
  nome?: string
}

interface Obrigacao {
  id: string | number
  title: string
  description?: string
  status: string
  due_date: string
  client_id: string | number
  type?: 'custom' | 'receita_federal'
  grau_importancia?: string
}

// Estados
const obrigacoes = ref<Obrigacao[]>([])
const clientes = ref<Cliente[]>([])
const isLoading = ref(true)

// Filtros Reativos
const filtroClienteId = ref('')
const searchQuery = ref('')

// Estados dos Modais
const isDetalhesModalOpen = ref(false)
const obrigacaoSelecionada = ref<Obrigacao | null>(null)
const isCadastroModalOpen = ref(false)

// Estado do Formulário (Usado para Criar e Editar)
const isEditando = ref(false)
const idSendoEditado = ref<string | number | null>(null)
const formularioObrigacao = ref({
  title: '',
  description: '',
  client_id: '' as string | number,
  due_date: '',
  status: 'pendente',
  grau_importancia: 'Média'
})

// 2. Computed Property (Motor de Busca + Ordenação Segura)
const obrigacoesFiltradas = computed(() => {
  let resultado = obrigacoes.value

  if (filtroClienteId.value) {
    resultado = resultado.filter((obrigacao) => obrigacao.client_id === filtroClienteId.value)
  }

  if (searchQuery.value) {
    const termoBusca = searchQuery.value.toLowerCase()
    resultado = resultado.filter((obrigacao) =>
      obrigacao.title.toLowerCase().includes(termoBusca) ||
      (obrigacao.description && obrigacao.description.toLowerCase().includes(termoBusca))
    )
  }

  const prioridadePeso: Record<string, number> = { 'Urgente': 4, 'Alta': 3, 'Média': 2, 'Baixa': 1 }
  return [...resultado].sort((a, b) => {
    const pesoA = prioridadePeso[a.grau_importancia || 'Média'] || 0
    const pesoB = prioridadePeso[b.grau_importancia || 'Média'] || 0
    return pesoB - pesoA
  })
})

// Funções do Modal de Detalhes
const abrirDetalhes = (obrigacao: Obrigacao) => {
  obrigacaoSelecionada.value = obrigacao
  isDetalhesModalOpen.value = true
}

const fecharDetalhes = () => {
  isDetalhesModalOpen.value = false
  obrigacaoSelecionada.value = null
}

// ==========================================
// FUNÇÕES DE CRUD (CRIAR, EDITAR, CONCLUIR, EXCLUIR)
// ==========================================
const abrirCadastro = () => {
  isEditando.value = false
  idSendoEditado.value = null
  formularioObrigacao.value = {
    title: '',
    description: '',
    client_id: '',
    due_date: '',
    status: 'pendente',
    grau_importancia: 'Média'
  }
  isCadastroModalOpen.value = true
}

const abrirEdicao = (obrigacao: Obrigacao) => {
  // Previne a edição de tarefas automáticas da Receita
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
    due_date: obrigacao.due_date,
    status: obrigacao.status,
    grau_importancia: obrigacao.grau_importancia || 'Média'
  }

  fecharDetalhes() // Fecha os detalhes se estiver aberto
  isCadastroModalOpen.value = true
}

const fecharCadastro = () => {
  isCadastroModalOpen.value = false
}

const salvarObrigacao = async () => {
  if (!formularioObrigacao.value.title || !formularioObrigacao.value.client_id || !formularioObrigacao.value.due_date) {
    toast.warn('Por favor, preencha todos os campos obrigatórios.')
    return
  }

  try {
    if (isEditando.value && idSendoEditado.value) {
      // 🔵 Rota de Edição (PUT)
      const response = await api.put(`/api/v1/obrigacoes/${idSendoEditado.value}`, formularioObrigacao.value)

      // Atualiza o item na lista localmente sem recarregar a página
      const index = obrigacoes.value.findIndex(o => o.id === idSendoEditado.value)
      if (index !== -1) obrigacoes.value[index] = response.data

      toast.success('Tarefa atualizada com sucesso!')
    } else {
      // 🟢 Rota de Criação (POST)
      const response = await api.post('/api/v1/obrigacoes', formularioObrigacao.value)
      obrigacoes.value.push(response.data)
      toast.success('Nova obrigação criada com sucesso!')
    }
    fecharCadastro()
  } catch (error) {
    toast.error('Erro ao salvar a obrigação.')
    console.error(error)
  }
}

// Ação Rápida (1 clique)
const concluirTarefa = async (obrigacao: Obrigacao) => {
  try {
    const response = await api.patch(`/api/v1/obrigacoes/${obrigacao.id}/concluir`)

    // Atualiza na tela
    const index = obrigacoes.value.findIndex(o => o.id === obrigacao.id)
    if (index !== -1) obrigacoes.value[index] = response.data

    // Se o modal de detalhes estiver aberto, atualiza a informação dele também
    if (obrigacaoSelecionada.value?.id === obrigacao.id) {
      obrigacaoSelecionada.value = response.data
    }

    toast.success('🎉 Obrigação concluída!')
  } catch (error) {
    toast.error('Erro ao concluir tarefa.')
  }
}

const excluirTarefa = async (id: string | number) => {
  if (!confirm('Tem certeza que deseja excluir esta tarefa permanentemente?')) return

  try {
    await api.delete(`/api/v1/obrigacoes/${id}`)
    obrigacoes.value = obrigacoes.value.filter(o => o.id !== id)
    fecharDetalhes()
    toast.success('Tarefa excluída.')
  } catch (error) {
    toast.error('Erro ao excluir tarefa.')
  }
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

// Helpers Visuais
const getNomeCliente = (clientId: string | number) => {
  const cliente = clientes.value.find((c) => c.id === clientId)
  if (cliente) return cliente.nome || cliente.razao_social || 'Nome Indisponível'
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

const getImportanciaBadge = (grau?: string) => {
  const nivel = grau || 'Média'
  const styles: Record<string, string> = {
    'Urgente': 'bg-red-50 text-red-700 border-red-200',
    'Alta': 'bg-orange-50 text-orange-700 border-orange-200',
    'Média': 'bg-blue-50 text-blue-700 border-blue-200',
    'Baixa': 'bg-gray-50 text-gray-700 border-gray-200'
  }
  return {
    class: `px-2 py-1 rounded-md text-[11px] font-bold uppercase tracking-wider border ${styles[nivel] || styles['Média']}`,
    label: nivel
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

      <button @click="abrirCadastro"
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
        <p class="text-sm text-gray-500 max-w-md">Não localizamos nenhuma tarefa com os filtros atuais.</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Arquivo</th>
              <th class="px-6 py-4 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">Cliente
              </th>
              <th class="px-6 py-4 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">Data</th>
              <th class="px-6 py-4 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">Prioridade
              </th>
              <th class="px-6 py-4 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
              <th class="px-6 py-4 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">Ações</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="obrigacao in obrigacoesFiltradas" :key="obrigacao.id"
              class="hover:bg-gray-50 transition-colors group">
              <td class="px-6 py-4">
                <div class="text-sm font-bold text-[#19341a]">{{ obrigacao.title }}</div>
                <div v-if="obrigacao.description" class="text-xs text-[#2a2a2a]/60 truncate max-w-xs mt-0.5">{{
                  obrigacao.description }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center text-sm text-gray-700 font-medium">{{
                getNomeCliente(obrigacao.client_id) }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-center text-sm text-gray-500">{{
                formatDate(obrigacao.due_date) }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <span :class="getImportanciaBadge(obrigacao.grau_importancia).class">{{
                  getImportanciaBadge(obrigacao.grau_importancia).label }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <span :class="getStatusBadge(obrigacao.status).class">{{ getStatusBadge(obrigacao.status).label
                  }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex justify-center items-center gap-2">

                  <button v-if="obrigacao.status !== 'concluida' && obrigacao.type !== 'receita_federal'"
                    @click="concluirTarefa(obrigacao)"
                    class="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 rounded-lg text-xs font-bold transition-colors shadow-sm"
                    title="Concluir Tarefa">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path>
                    </svg>
                    Concluir
                  </button>

                  <button @click="abrirDetalhes(obrigacao)"
                    class="flex items-center gap-1.5 px-3 py-1.5 bg-white text-gray-700 hover:bg-gray-50 border border-gray-200 rounded-lg text-xs font-bold transition-colors shadow-sm">
                    Detalhes
                  </button>

                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="isCadastroModalOpen" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden">
        <div class="px-6 py-5 border-b border-gray-100 flex justify-between items-center bg-[#f8f8f8]">
          <h3 class="text-xl font-bold text-[#19341a]">
            {{ isEditando ? '✏️ Editar Obrigação' : '✨ Criar Nova Obrigação' }}
          </h3>
          <button @click="fecharCadastro" class="text-gray-400 hover:text-gray-600 text-2xl font-bold">&times;</button>
        </div>

        <div class="p-6 space-y-4">
          <div>
            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Título da Tarefa *</label>
            <input v-model="formularioObrigacao.title" type="text" placeholder="Ex: Declarar Simples Nacional"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-coral" />
          </div>

          <div>
            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Descrição / Instruções</label>
            <textarea v-model="formularioObrigacao.description" rows="3"
              placeholder="Instruções adicionais para a tarefa..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-coral"></textarea>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Vincular Cliente *</label>
              <select v-model="formularioObrigacao.client_id"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-brand-coral">
                <option value="">Selecione...</option>
                <option v-for="cliente in clientes" :key="cliente.id" :value="cliente.id">
                  {{ cliente.nome || cliente.razao_social }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Prazo Limite *</label>
              <input v-model="formularioObrigacao.due_date" type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-coral" />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Grau de Importância</label>
              <select v-model="formularioObrigacao.grau_importancia"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-brand-coral">
                <option value="Urgente">🚨 Urgente</option>
                <option value="Alta">🟠 Alta</option>
                <option value="Média">🔵 Média</option>
                <option value="Baixa">🟢 Baixa</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-bold text-gray-500 uppercase mb-1">Status Atual</label>
              <select v-model="formularioObrigacao.status"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-brand-coral">
                <option value="pendente">Pendente</option>
                <option value="em_andamento">Em Andamento</option>
                <option value="aguardando_cliente">Aguardando Cliente</option>
                <option v-if="isEditando" value="concluida">✅ Concluída</option>
              </select>
            </div>
          </div>
        </div>

        <div class="px-6 py-4 border-t border-gray-100 flex justify-between items-center bg-gray-50">
          <button v-if="isEditando" @click="excluirTarefa(idSendoEditado!)"
            class="px-4 py-2 text-red-600 hover:bg-red-50 rounded-xl text-sm font-bold transition-colors">🗑️
            Excluir</button>
          <div v-else></div>
          <div class="flex gap-2">
            <button @click="fecharCadastro"
              class="px-4 py-2 border text-gray-600 rounded-xl hover:bg-gray-100 text-sm font-semibold">Cancelar</button>
            <button @click="salvarObrigacao"
              class="px-5 py-2 bg-[#ff8a65] hover:bg-[#f07047] text-white rounded-xl text-sm font-semibold shadow-sm">
              {{ isEditando ? 'Salvar Alterações' : 'Salvar Obrigação' }}
            </button>
          </div>
        </div>
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
          <div class="flex items-center gap-2">
            <button v-if="obrigacaoSelecionada.type !== 'receita_federal'" @click="abrirEdicao(obrigacaoSelecionada)"
              class="text-sm font-bold text-[#ff8a65] hover:text-[#f07047] px-2 py-1 rounded hover:bg-orange-50 transition-colors">✏️
              Editar</button>
            <button @click="fecharDetalhes"
              class="text-gray-400 hover:text-gray-600 text-2xl font-bold">&times;</button>
          </div>
        </div>

        <div class="p-6 space-y-5">
          <div class="flex justify-between items-start">
            <div>
              <span class="block text-xs font-bold text-[#2a2a2a]/40 uppercase tracking-wider mb-1">Título</span>
              <p class="text-[#19341a] font-bold text-lg">{{ obrigacaoSelecionada.title }}</p>
            </div>
            <span :class="getImportanciaBadge(obrigacaoSelecionada.grau_importancia).class">{{
              getImportanciaBadge(obrigacaoSelecionada.grau_importancia).label }}</span>
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
            <div class="flex gap-3 items-center">
              <span :class="getStatusBadge(obrigacaoSelecionada.status).class">{{
                getStatusBadge(obrigacaoSelecionada.status).label }}</span>
              <button
                v-if="obrigacaoSelecionada.status !== 'concluida' && obrigacaoSelecionada.type !== 'receita_federal'"
                @click="concluirTarefa(obrigacaoSelecionada)"
                class="text-xs font-bold text-emerald-600 hover:underline">
                Marcar como Concluída ✓
              </button>
            </div>
          </div>
        </div>

        <div class="px-6 py-4 border-t border-gray-100 flex justify-end">
          <button @click="fecharDetalhes"
            class="px-6 py-2.5 bg-white border border-gray-200 text-[#2a2a2a]/70 font-semibold hover:bg-gray-50 rounded-xl transition-colors shadow-sm">Fechar</button>
        </div>
      </div>
    </div>

  </Layout>
</template>