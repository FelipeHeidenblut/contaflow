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

interface Membro {
  id: string | number
  name: string
}

interface Obrigacao {
  id: string | number
  title: string
  description?: string
  status: string
  due_date: string
  client_id: string | number
  assigned_to?: string | number | null // Já existed no seu backend
  type?: 'custom' | 'receita_federal'
  grau_importancia?: string
}

// Estados
const obrigacoes = ref<Obrigacao[]>([])
const clientes = ref<Cliente[]>([])
const membros = ref<Membro[]>([]) // NOVO: Lista de membros da equipe
const isLoading = ref(true)

// Filtros Reativos (Adicionado filtroResponsavel)
const filtroClienteId = ref('')
const filtroStatus = ref('')
const filtroResponsavel = ref('') // NOVO
const searchQuery = ref('')

// Estados dos Modais
const isDetalhesModalOpen = ref(false)
const obrigacaoSelecionada = ref<Obrigacao | null>(null)
const isCadastroModalOpen = ref(false)

// Estado do Formulário (Adicionado assigned_to)
const isEditando = ref(false)
const idSendoEditado = ref<string | number | null>(null)
const formularioObrigacao = ref({
  title: '',
  description: '',
  client_id: '' as string | number,
  assigned_to: '' as string | number | '', // NOVO CAMPO
  due_date: '',
  status: 'pendente',
  grau_importancia: 'Média'
})

// ==========================================
// TEMPLATES CONTÁBEIS
// ==========================================
interface TemplateContabil {
  nome: string
  title: string
  description: string
  grau_importancia: string
  status?: string
}

const templatesContabeis: TemplateContabil[] = [
  { nome: '🧾 Apuração DAS (Simples Nacional)', title: 'Apuração DAS - Simples Nacional', description: 'Verificar receitas do período, calcular tributos devidos e gerar guia de DAS para pagamento.', grau_importancia: 'Alta' },
  { nome: '💼 Folha de Pagamento Mensal', title: 'Folha de Pagamento', description: 'Conferir ponto, calcular salários, encargos sociais e gerar holerites.', grau_importancia: 'Alta' },
  { nome: '📄 SPED Fiscal', title: 'SPED Fiscal', description: 'Validar livros fiscais, conferir notas fiscais de entrada/saída e gerar arquivo do SPED.', grau_importancia: 'Urgente' },
  { nome: '🏛️ DCTFWeb', title: 'DCTFWeb', description: 'Gerar e transmitar a DCTFWeb com as apurações do eSocial e EFD-Contribuições.', grau_importancia: 'Alta' },
  { nome: '🤝 Solicitar Documentos (Aguardando Cliente)', title: 'Aguardando Documentos do Cliente', description: 'Solicitar e organizar documentos enviados pelo cliente para fechamento da competência.', grau_importancia: 'Média', status: 'aguardando_cliente' },
  { nome: '🏢 ECD (Escrituração Contábil)', title: 'ECD - Escrituração Contábil Digital', description: 'Conferir lançamentos contábeis e gerar arquivo da ECD para envio ao SPED.', grau_importancia: 'Urgente' }
]

const aplicarTemplate = (event: Event) => {
  const target = event.target as HTMLSelectElement
  const selectedIndex = parseInt(target.value)
  if (!isNaN(selectedIndex)) {
    const template = templatesContabeis[selectedIndex]
    if (template) {
      formularioObrigacao.value.title = template.title
      formularioObrigacao.value.description = template.description
      formularioObrigacao.value.grau_importancia = template.grau_importancia
      if (template.status) formularioObrigacao.value.status = template.status
    }
  }
}

// ==========================================
// COMPUTED E FILTROS
// ==========================================
const obrigacoesFiltradas = computed(() => {
  let resultado = obrigacoes.value

  if (filtroClienteId.value) resultado = resultado.filter((o) => o.client_id === filtroClienteId.value)
  if (filtroStatus.value) resultado = resultado.filter((o) => o.status === filtroStatus.value)
  
  // NOVO FILTRO DE RESPONSÁVEL
  if (filtroResponsavel.value) {
    resultado = resultado.filter((o) => o.assigned_to === filtroResponsavel.value)
  }

  if (searchQuery.value) {
    const termoBusca = searchQuery.value.toLowerCase()
    resultado = resultado.filter((o) => o.title.toLowerCase().includes(termoBusca) || (o.description && o.description.toLowerCase().includes(termoBusca)))
  }

  const prioridadePeso: Record<string, number> = { 'Urgente': 4, 'Alta': 3, 'Média': 2, 'Baixa': 1 }
  return [...resultado].sort((a, b) => {
    const pesoA = prioridadePeso[a.grau_importancia || 'Média'] || 0
    const pesoB = prioridadePeso[b.grau_importancia || 'Média'] || 0
    return pesoB - pesoA
  })
})

// ==========================================
// FUNÇÕES DO MODAL
// ==========================================
const abrirDetalhes = (obrigacao: Obrigacao) => { obrigacaoSelecionada.value = obrigacao; isDetalhesModalOpen.value = true }
const fecharDetalhes = () => { isDetalhesModalOpen.value = false; obrigacaoSelecionada.value = null }

const abrirCadastro = () => {
  isEditando.value = false; idSendoEditado.value = null
  formularioObrigacao.value = { title: '', description: '', client_id: '', assigned_to: '', due_date: '', status: 'pendente', grau_importancia: 'Média' }
  isCadastroModalOpen.value = true
}

const abrirEdicao = (obrigacao: Obrigacao) => {
  if (obrigacao.type === 'receita_federal') { toast.info('Não é possível editar prazos federais fixos.'); return }
  isEditando.value = true; idSendoEditado.value = obrigacao.id
  formularioObrigacao.value = {
    title: obrigacao.title,
    description: obrigacao.description || '',
    client_id: obrigacao.client_id,
    assigned_to: obrigacao.assigned_to || '', // CARREGA O RESPONSÁVEL
    due_date: obrigacao.due_date,
    status: obrigacao.status,
    grau_importancia: obrigacao.grau_importancia || 'Média'
  }
  fecharDetalhes(); isCadastroModalOpen.value = true
}

const fecharCadastro = () => { isCadastroModalOpen.value = false }

const salvarObrigacao = async () => {
  if (!formularioObrigacao.value.title || !formularioObrigacao.value.client_id || !formularioObrigacao.value.due_date) {
    toast.warn('Por favor, preencha os campos obrigatórios (Título, Cliente e Prazo).'); return
  }
  try {
    // Limpa o assigned_to se for vazio (para não salvar string vazia no DB)
    const payload = { ...formularioObrigacao.value }
    if (!payload.assigned_to) payload.assigned_to = null as any

    if (isEditando.value && idSendoEditado.value) {
      const response = await api.put(`/api/v1/obrigacoes/${idSendoEditado.value}`, payload)
      const index = obrigacoes.value.findIndex(o => o.id === idSendoEditado.value)
      if (index !== -1) obrigacoes.value[index] = response.data
      toast.success('Tarefa atualizada com sucesso!')
    } else {
      const response = await api.post('/api/v1/obrigacoes', payload)
      obrigacoes.value.push(response.data)
      toast.success('Nova obrigação criada com sucesso!')
    }
    fecharCadastro()
  } catch (error) { toast.error('Erro ao salvar a obrigação.'); console.error(error) }
}

const concluirTarefa = async (obrigacao: Obrigacao) => {
  try {
    const response = await api.patch(`/api/v1/obrigacoes/${obrigacao.id}/concluir`)
    const index = obrigacoes.value.findIndex(o => o.id === obrigacao.id)
    if (index !== -1) obrigacoes.value[index] = response.data
    if (obrigacaoSelecionada.value?.id === obrigacao.id) obrigacaoSelecionada.value = response.data
    toast.success('🎉 Obrigação concluída!')
  } catch (error) { toast.error('Erro ao concluir tarefa.') }
}

const excluirTarefa = async (id: string | number) => {
  if (!confirm('Tem certeza que deseja excluir esta tarefa permanentemente?')) return
  try {
    await api.delete(`/api/v1/obrigacoes/${id}`)
    obrigacoes.value = obrigacoes.value.filter(o => o.id !== id)
    fecharDetalhes(); toast.success('Tarefa excluída.')
  } catch (error) { toast.error('Erro ao excluir tarefa.') }
}

// ==========================================
// FETCH DE DADOS (Busca membros também)
// ==========================================
const fetchData = async () => {
  isLoading.value = true
  try {
    const [obrigacoesRes, clientesRes, membrosRes] = await Promise.all([
      api.get('/api/v1/obrigacoes'),
      api.get('/api/v1/clientes'),
      api.get('/api/v1/membros') // BUSCANDO EQUIPE
    ])
    obrigacoes.value = obrigacoesRes.data
    clientes.value = clientesRes.data
    membros.value = membrosRes.data
  } catch (error) { toast.error('Erro ao carregar os dados.'); console.error(error) } 
  finally { isLoading.value = false }
}

// ==========================================
// HELPERS VISUAIS
// ==========================================
const getNomeCliente = (clientId: string | number) => {
  const cliente = clientes.value.find((c) => c.id === clientId)
  return cliente ? cliente.nome || cliente.razao_social || 'Nome Indisponível' : 'Não vinculado'
}

const getNomeMembro = (membroId?: string | number | null) => {
  if (!membroId) return 'Não atribuído'
  const membro = membros.value.find((m) => m.id === membroId)
  return membro ? membro.name : 'Desconhecido'
}

const getIniciaisMembro = (nome: string) => {
  if (!nome || nome === 'Não atribuído') return '?'
  
  // O .filter(p => p) remove espaços vazios extras
  const partes = nome.trim().split(' ').filter(p => p)
  
  if (partes.length === 0) return '?'
  if (partes.length === 1) return (partes[0]?.charAt(0) || '?').toUpperCase()
  
  // Usamos ?. para evitar o erro de tipagem do TypeScript
  const primeiraLetra = partes[0]?.charAt(0) || ''
  const ultimaLetra = partes[partes.length - 1]?.charAt(0) || ''
  
  return (primeiraLetra + ultimaLetra).toUpperCase() || '?'
}

const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  const [year, month, day] = dateString.split('-')
  return `${day}/${month}/${year}`
}

const isAtrasada = (dateString: string, status: string) => {
  if (status === 'concluida' || !dateString) return false
  const today = new Date()
  const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
  return dateString < todayStr
}

const getStatusBadge = (status: string) => {
  const styles: Record<string, string> = {
    'concluida': 'bg-emerald-100 text-emerald-800 border-emerald-200',
    'em_andamento': 'bg-blue-100 text-blue-800 border-blue-200',
    'aguardando_cliente': 'bg-orange-100 text-orange-800 border-orange-200',
    'pendente': 'bg-yellow-100 text-yellow-800 border-yellow-200'
  }
  const labels: Record<string, string> = { 'concluida': 'Concluída', 'em_andamento': 'Em Andamento', 'aguardando_cliente': 'Aguard. Cliente', 'pendente': 'Pendente' }
  return { class: `px-2.5 py-0.5 rounded-full text-xs font-semibold border ${styles[status] || styles['pendente']}`, label: labels[status] || 'Pendente' }
}

const getImportanciaBadge = (grau?: string) => {
  const nivel = grau || 'Média'
  const styles: Record<string, string> = {
    'Urgente': 'bg-red-50 text-red-700 border-red-200', 'Alta': 'bg-orange-50 text-orange-700 border-orange-200',
    'Média': 'bg-blue-50 text-blue-700 border-blue-200', 'Baixa': 'bg-gray-50 text-gray-700 border-gray-200'
  }
  return { class: `px-2 py-1 rounded-md text-[11px] font-bold uppercase tracking-wider border ${styles[nivel] || styles['Média']}`, label: nivel }
}

onMounted(() => fetchData())
</script>

<template>
  <Layout title="Controle de Obrigações">

    <header class="mb-6">
      <h1 class="text-2xl font-bold text-[#19341a]">Obrigações e Tarefas</h1>
      <p class="text-gray-500 text-sm mt-1">Gerencie prazos, delegue responsabilidades e acompanhe pendências.</p>
    </header>

    <!-- FILTROS -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
      <div class="flex flex-col sm:flex-row gap-3 w-full sm:w-auto sm:max-w-2xl">
        <div class="relative w-full sm:w-48">
          <input v-model="searchQuery" type="text" placeholder="Buscar tarefa..."
            class="w-full pl-4 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#ff8a65] text-sm shadow-sm" />
        </div>

        <select v-model="filtroClienteId" class="w-full sm:w-44 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#ff8a65] bg-white text-gray-700 text-sm shadow-sm">
          <option value="">🏢 Todos Clientes</option>
          <option v-for="c in clientes" :key="c.id" :value="c.id">{{ c.nome || c.razao_social }}</option>
        </select>

        <!-- NOVO FILTRO DE RESPONSÁVEL -->
        <select v-model="filtroResponsavel" class="w-full sm:w-44 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#ff8a65] bg-white text-gray-700 text-sm shadow-sm">
          <option value="">👥 Todos Responsáveis</option>
          <option v-for="m in membros" :key="m.id" :value="m.id">{{ m.name }}</option>
        </select>

        <select v-model="filtroStatus" class="w-full sm:w-40 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#ff8a65] bg-white text-gray-700 text-sm shadow-sm">
          <option value="">Todos Status</option>
          <option value="pendente">Pendentes</option>
          <option value="em_andamento">Em Andamento</option>
          <option value="aguardando_cliente">Aguard. Cliente</option>
          <option value="concluida">Concluídas</option>
        </select>
      </div>

      <button @click="abrirCadastro" class="w-full sm:w-auto bg-[#ff8a65] hover:bg-[#f07047] text-white font-semibold py-2.5 px-5 rounded-xl transition-all flex items-center justify-center gap-2 shadow-sm">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
        <span>Nova Obrigação</span>
      </button>
    </div>

    <!-- TABELA -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div v-if="isLoading" class="p-10 text-center text-gray-500">Sincronizando obrigações...</div>
      <div v-else-if="obrigacoesFiltradas.length === 0" class="p-16 text-center text-gray-500">
        Nenhuma obrigação encontrada.
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Tarefa</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Cliente</th>
              <!-- NOVA COLUNA -->
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Responsável</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Prazo</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Prioridade</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Status</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Ações</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="obrigacao in obrigacoesFiltradas" :key="obrigacao.id" class="hover:bg-gray-50">
              <td class="px-6 py-4">
                <div class="text-sm font-bold text-[#19341a]">{{ obrigacao.title }}</div>
                <div class="text-xs text-gray-400 truncate max-w-xs">{{ obrigacao.description }}</div>
              </td>
              <td class="px-6 py-4 text-sm text-gray-700 font-medium">{{ getNomeCliente(obrigacao.client_id) }}</td>
              
              <!-- NOVA CÉLULA: AVATAR DO RESPONSÁVEL -->
              <td class="px-6 py-4">
                <div class="flex items-center gap-2" :title="getNomeMembro(obrigacao.assigned_to)">
                  <div class="w-7 h-7 rounded-full bg-[#19341a]/10 text-[#19341a] flex items-center justify-center text-[10px] font-bold">
                    {{ getIniciaisMembro(getNomeMembro(obrigacao.assigned_to)) }}
                  </div>
                  <span class="text-xs text-gray-500 hidden md:block">{{ getNomeMembro(obrigacao.assigned_to) }}</span>
                </div>
              </td>

              <td class="px-6 py-4 text-sm" :class="isAtrasada(obrigacao.due_date, obrigacao.status) ? 'text-red-600 font-bold' : 'text-gray-500'">
                {{ formatDate(obrigacao.due_date) }}
              </td>
              <td class="px-6 py-4"><span :class="getImportanciaBadge(obrigacao.grau_importancia).class">{{ getImportanciaBadge(obrigacao.grau_importancia).label }}</span></td>
              <td class="px-6 py-4"><span :class="getStatusBadge(obrigacao.status).class">{{ getStatusBadge(obrigacao.status).label }}</span></td>
              <td class="px-6 py-4">
                <div class="flex gap-2">
                  <button v-if="obrigacao.status !== 'concluida'" @click="concluirTarefa(obrigacao)" class="px-3 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-md text-xs font-bold">Concluir</button>
                  <button @click="abrirDetalhes(obrigacao)" class="px-3 py-1 bg-white text-gray-700 border border-gray-200 rounded-md text-xs font-bold">Detalhes</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- MODAL CADASTRO/EDIÇÃO -->
    <div v-if="isCadastroModalOpen" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden">
        <div class="px-6 py-5 border-b flex justify-between items-center bg-[#f8f8f8]">
          <h3 class="text-xl font-bold text-[#19341a]">{{ isEditando ? '✏️ Editar' : '✨ Nova Obrigação' }}</h3>
          <button @click="fecharCadastro" class="text-gray-400 text-2xl">&times;</button>
        </div>

        <div class="p-6 space-y-4">
          <div v-if="!isEditando">
            <label class="text-xs font-bold text-gray-500 uppercase mb-1 block">Modelo Rápido</label>
            <select @change="aplicarTemplate($event)" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white">
              <option value="">Escolher modelo...</option>
              <option v-for="(t, i) in templatesContabeis" :key="i" :value="i">{{ t.nome }}</option>
            </select>
            <hr class="my-3 border-gray-100">
          </div>

          <div>
            <label class="text-xs font-bold text-gray-500 uppercase mb-1 block">Título *</label>
            <input v-model="formularioObrigacao.title" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
          </div>
          <div>
            <label class="text-xs font-bold text-gray-500 uppercase mb-1 block">Descrição</label>
            <textarea v-model="formularioObrigacao.description" rows="2" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"></textarea>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-xs font-bold text-gray-500 uppercase mb-1 block">Cliente *</label>
              <select v-model="formularioObrigacao.client_id" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white">
                <option value="">Selecione...</option>
                <option v-for="c in clientes" :key="c.id" :value="c.id">{{ c.nome || c.razao_social }}</option>
              </select>
            </div>
            <!-- CAMPO NOVO: ATRIBUIR A -->
            <div>
              <label class="text-xs font-bold text-gray-500 uppercase mb-1 block">Atribuir para</label>
              <select v-model="formularioObrigacao.assigned_to" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white">
                <option value="">Não atribuído</option>
                <option v-for="m in membros" :key="m.id" :value="m.id">{{ m.name }}</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-xs font-bold text-gray-500 uppercase mb-1 block">Prazo *</label>
              <input v-model="formularioObrigacao.due_date" type="date" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm" />
            </div>
            <div>
              <label class="text-xs font-bold text-gray-500 uppercase mb-1 block">Prioridade</label>
              <select v-model="formularioObrigacao.grau_importancia" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white">
                <option value="Urgente">🚨 Urgente</option><option value="Alta">🟠 Alta</option><option value="Média">🔵 Média</option><option value="Baixa">🟢 Baixa</option>
              </select>
            </div>
          </div>
        </div>

        <div class="px-6 py-4 border-t bg-gray-50 flex justify-between">
          <button v-if="isEditando" @click="excluirTarefa(idSendoEditado!)" class="text-red-600 text-sm font-bold">🗑️ Excluir</button>
          <div class="flex gap-2 ml-auto">
            <button @click="fecharCadastro" class="px-4 py-2 text-gray-600 text-sm">Cancelar</button>
            <button @click="salvarObrigacao" class="px-5 py-2 bg-[#ff8a65] text-white text-sm font-semibold rounded-xl">{{ isEditando ? 'Salvar' : 'Criar' }}</button>
          </div>
        </div>
      </div>
    </div>

    <!-- MODAL DETALHES -->
    <div v-if="isDetalhesModalOpen && obrigacaoSelecionada" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg">
        <div class="px-6 py-5 border-b flex justify-between bg-[#f8f8f8]">
          <h3 class="text-xl font-bold text-[#19341a]">Detalhes</h3>
          <button @click="fecharDetalhes" class="text-gray-400 text-2xl">&times;</button>
        </div>
        <div class="p-6 space-y-4">
          <p class="text-lg font-bold text-[#19341a]">{{ obrigacaoSelecionada.title }}</p>
          <p class="text-sm text-gray-600">{{ obrigacaoSelecionada.description }}</p>
          <div class="grid grid-cols-2 gap-4 pt-4 border-t">
            <div><span class="text-xs text-gray-400 block">Cliente</span><span class="text-sm font-semibold">{{ getNomeCliente(obrigacaoSelecionada.client_id) }}</span></div>
            <div><span class="text-xs text-gray-400 block">Responsável</span><span class="text-sm font-semibold">{{ getNomeMembro(obrigacaoSelecionada.assigned_to) }}</span></div>
            <div><span class="text-xs text-gray-400 block">Prazo</span><span class="text-sm font-semibold">{{ formatDate(obrigacaoSelecionada.due_date) }}</span></div>
            <div><span class="text-xs text-gray-400 block">Status</span><span :class="getStatusBadge(obrigacaoSelecionada.status).class">{{ getStatusBadge(obrigacaoSelecionada.status).label }}</span></div>
          </div>
        </div>
        <div class="px-6 py-4 border-t bg-gray-50 flex justify-end gap-2">
          <button v-if="obrigacaoSelecionada.status !== 'concluida'" @click="concluirTarefa(obrigacaoSelecionada)" class="px-4 py-2 bg-emerald-500 text-white text-sm font-semibold rounded-xl">Concluir ✓</button>
          <button @click="abrirEdicao(obrigacaoSelecionada)" class="px-4 py-2 bg-[#19341a] text-white text-sm font-semibold rounded-xl">Editar</button>
        </div>
      </div>
    </div>

  </Layout>
</template>