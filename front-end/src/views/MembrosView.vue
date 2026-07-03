<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../services/api'
import Layout from '../components/Layout.vue'
import { toast } from 'vue3-toastify'

// 1. Tipagem exata baseada no seu model Profile
interface Membro {
  id: string
  name: string
  email: string
  role: 'admin' | 'colaborador'
}

// Estados
const membros = ref<Membro[]>([])
const isLoading = ref(true)
const isModalOpen = ref(false)

// Mock do usuário logado
const loggedUserRole = ref('admin')
const loggedUserId = ref('id-do-usuario-logado-aqui')

const novoMembro = ref({
  name: '',
  email: '',
  role: 'colaborador',
  password: '', // NOVO CAMPO
})

// Gera uma senha forte automática para sugerir ao admin
const gerarSenhaSugestao = () => {
  const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#'
  let senha = ''
  for (let i = 0; i < 10; i++) {
    senha += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  novoMembro.value.password = senha
}

// Busca de Membros
const fetchData = async () => {
  isLoading.value = true
  try {
    const response = await api.get('/api/v1/membros')
    membros.value = response.data
  } catch (error) {
    toast.error('Erro ao carregar a equipe.')
  } finally {
    isLoading.value = false
  }
}

// Ações de Admin
const salvarMembro = async () => {
  if (!novoMembro.value.name || !novoMembro.value.email || !novoMembro.value.password) {
    toast.warn('Preencha nome, e-mail e senha.')
    return
  }

  if (novoMembro.value.password.length < 6) {
    toast.warn('A senha deve ter no mínimo 6 caracteres.')
    return
  }

  try {
    const response = await api.post('/api/v1/membros', novoMembro.value)
    membros.value.push(response.data)
    toast.success('Membro criado com sucesso! Ele já pode fazer login com a senha definida.')
    isModalOpen.value = false
    novoMembro.value = { name: '', email: '', role: 'colaborador', password: '' }
  } catch (error: any) {
    toast.error(error.response?.data?.detail || 'Erro ao adicionar membro.')
  }
}

const removerMembro = async (membro: Membro) => {
  if (!confirm(`Tem certeza que deseja remover ${membro.name} da equipe?`)) return

  try {
    await api.delete(`/api/v1/membros/${membro.id}`)
    membros.value = membros.value.filter((m) => m.id !== membro.id)
    toast.success('Membro removido com sucesso.')
  } catch (error: any) {
    toast.error(error.response?.data?.detail || 'Erro ao remover membro.')
  }
}

// Helpers Visuais
const getRoleBadge = (role: string) => {
  return role === 'admin'
    ? 'bg-purple-100 text-purple-800 border-purple-200'
    : 'bg-blue-100 text-blue-800 border-blue-200'
}

const formatRole = (role: string) => {
  if (role === 'admin') return 'Administrador'
  if (role === 'colaborador') return 'Colaborador'
  return role
}

onMounted(() => fetchData())
</script>

<template>
  <Layout title="Membros e Acessos">
    <header
      class="mb-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4"
    >
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Membros da Equipe</h1>
        <p class="text-gray-500 text-sm mt-1">
          Gerencie os acessos e permissões do seu escritório.
        </p>
      </div>

      <button
        v-if="loggedUserRole === 'admin'"
        @click="isModalOpen = true"
        class="w-full sm:w-auto bg-[#ff8a65] hover:bg-[#f07047] text-white font-semibold py-2.5 px-5 rounded-xl transition-all flex items-center justify-center gap-2 whitespace-nowrap shadow-sm"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
          ></path>
        </svg>
        <span>Adicionar Membro</span>
      </button>
    </header>

    <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div v-if="isLoading" class="p-10 text-center text-gray-500">Carregando equipe...</div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">
                Usuário
              </th>
              <th class="px-6 py-4 text-center text-xs font-semibold text-gray-500 uppercase">
                Nível de Acesso
              </th>
              <th
                v-if="loggedUserRole === 'admin'"
                class="px-6 py-4 text-right text-xs font-semibold text-gray-500 uppercase"
              >
                Ações
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="membro in membros"
              :key="membro.id"
              class="hover:bg-gray-50 transition-colors"
            >
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div
                    class="h-10 w-10 rounded-full bg-[#19341a]/10 flex items-center justify-center text-[#19341a] font-bold uppercase shadow-sm"
                  >
                    {{ membro.name.charAt(0) }}
                  </div>
                  <div>
                    <div class="text-sm font-bold text-gray-900">{{ membro.name }}</div>
                    <div class="text-xs text-gray-500">{{ membro.email }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 text-center">
                <span
                  class="px-2.5 py-1 rounded-full text-[11px] font-bold uppercase tracking-wider border"
                  :class="getRoleBadge(membro.role)"
                >
                  {{ formatRole(membro.role) }}
                </span>
              </td>
              <td v-if="loggedUserRole === 'admin'" class="px-6 py-4 text-right">
                <button
                  v-if="membro.id !== loggedUserId"
                  @click="removerMembro(membro)"
                  class="text-xs font-bold text-red-500 hover:text-red-700 hover:underline transition-colors"
                >
                  Excluir
                </button>
                <span v-else class="text-xs text-gray-300 italic">Você</span>
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
        <div
          class="px-6 py-5 border-b border-gray-100 flex justify-between items-center bg-[#f8f8f8]"
        >
          <h3 class="text-xl font-bold text-[#19341a]">Adicionar Membro</h3>
          <button
            @click="isModalOpen = false"
            class="text-gray-400 hover:text-gray-600 text-2xl font-bold"
          >
            &times;
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-xs font-bold text-gray-500 uppercase mb-1"
              >Nome Completo</label
            >
            <input
              v-model="novoMembro.name"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#ff8a65]"
            />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-500 uppercase mb-1">E-mail</label>
            <input
              v-model="novoMembro.email"
              type="email"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#ff8a65]"
            />
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-500 uppercase mb-1"
              >Nível de Acesso</label
            >
            <select
              v-model="novoMembro.role"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-[#ff8a65]"
            >
              <option value="colaborador">Colaborador (Visualiza e edita tarefas)</option>
              <option value="admin">Administrador (Acesso total)</option>
            </select>
          </div>

          <!-- NOVO CAMPO DE SENHA -->
          <div>
            <label class="block text-xs font-bold text-gray-500 uppercase mb-1"
              >Senha Temporária</label
            >
            <div class="flex gap-2">
              <input
                v-model="novoMembro.password"
                type="text"
                placeholder="Mínimo 6 caracteres"
                class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#ff8a65]"
              />
              <button
                type="button"
                @click="gerarSenhaSugestao"
                class="px-3 py-2 bg-[#19341a]/10 text-[#19341a] rounded-lg text-xs font-bold hover:bg-[#19341a]/20 transition-colors whitespace-nowrap"
              >
                Gerar Senha
              </button>
            </div>
            <p class="text-[11px] text-gray-400 mt-1">
              Entregue esta senha ao funcionário. Ele poderá trocá-la depois de logar.
            </p>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-gray-100 flex justify-end gap-2 bg-gray-50">
          <button
            @click="isModalOpen = false"
            class="px-4 py-2 border text-gray-600 rounded-xl hover:bg-gray-100 text-sm font-semibold"
          >
            Cancelar
          </button>
          <button
            @click="salvarMembro"
            class="px-5 py-2 bg-[#ff8a65] hover:bg-[#f07047] text-white rounded-xl text-sm font-semibold shadow-sm"
          >
            Criar Acesso
          </button>
        </div>
      </div>
    </div>
  </Layout>
</template>
