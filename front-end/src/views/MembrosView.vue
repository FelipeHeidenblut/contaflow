<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '../services/api'
import Layout from '../components/Layout.vue'
import { toast } from 'vue3-toastify'

interface Membro {
  id: string
  name: string
  email: string
  role: 'admin' | 'colaborador'
}

const membros = ref<Membro[]>([])
const isLoading = ref(true)
const isModalOpen = ref(false)

const loggedUserRole = ref('admin')
const loggedUserId = ref('id-do-usuario-logado-aqui')

const novoMembro = ref({
  name: '',
  email: '',
  role: 'colaborador',
  password: '',
})

const totalMembros = computed(() => membros.value.length)
const totalAdmins = computed(() => membros.value.filter((m) => m.role === 'admin').length)
const totalColaboradores = computed(
  () => membros.value.filter((m) => m.role === 'colaborador').length,
)

const gerarSenhaSugestao = () => {
  const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#'
  let senha = ''
  for (let i = 0; i < 10; i++) {
    senha += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  novoMembro.value.password = senha
}

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

const getRoleBadge = (role: string) => {
  return role === 'admin'
    ? 'bg-violet-100 text-violet-700 border-violet-200'
    : 'bg-blue-100 text-blue-700 border-blue-200'
}

const formatRole = (role: string) => {
  if (role === 'admin') return 'Administrador'
  if (role === 'colaborador') return 'Colaborador'
  return role
}

const getInitials = (name: string) => {
  const parts = name.trim().split(' ')
  if (parts.length === 1) return parts[0].charAt(0)
  return `${parts[0].charAt(0)}${parts[parts.length - 1].charAt(0)}`
}

onMounted(() => fetchData())
</script>

<template>
  <Layout title="Membros e Acessos">
    <div class="space-y-6">
      <!-- cabeçalho -->
      <header class="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
        <div>
          <h1 class="text-2xl font-semibold tracking-tight text-[var(--ct-ink)]">
            Membros da equipe
          </h1>
          <p class="mt-1 text-sm text-[var(--ct-text-muted)]">
            Gerencie usuários, níveis de acesso e permissões internas do escritório.
          </p>
        </div>

        <button
          v-if="loggedUserRole === 'admin'"
          @click="isModalOpen = true"
          class="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-[var(--ct-primary)] px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-[var(--ct-primary-hover)] sm:w-auto"
        >
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
            />
          </svg>
          <span>Adicionar membro</span>
        </button>
      </header>

      <!-- indicadores -->
      <section class="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div class="rounded-xl border border-[var(--ct-border)] bg-white p-4 shadow-sm">
          <p class="text-xs font-medium text-[var(--ct-text-muted)]">Total de membros</p>
          <p class="mt-2 text-3xl font-semibold text-[var(--ct-ink)] [font-variant-numeric:tabular-nums]">
            {{ totalMembros }}
          </p>
        </div>

        <div class="rounded-xl border border-[var(--ct-border)] bg-white p-4 shadow-sm">
          <p class="text-xs font-medium text-[var(--ct-text-muted)]">Administradores</p>
          <p class="mt-2 text-3xl font-semibold text-[var(--ct-ink)] [font-variant-numeric:tabular-nums]">
            {{ totalAdmins }}
          </p>
        </div>

        <div class="rounded-xl border border-[var(--ct-border)] bg-white p-4 shadow-sm">
          <p class="text-xs font-medium text-[var(--ct-text-muted)]">Colaboradores</p>
          <p class="mt-2 text-3xl font-semibold text-[var(--ct-ink)] [font-variant-numeric:tabular-nums]">
            {{ totalColaboradores }}
          </p>
        </div>
      </section>

      <!-- tabela -->
      <section class="overflow-hidden rounded-2xl border border-[var(--ct-border)] bg-white shadow-sm">
        <div v-if="isLoading" class="space-y-3 p-6">
          <div class="h-14 animate-pulse rounded-xl bg-slate-100"></div>
          <div class="h-14 animate-pulse rounded-xl bg-slate-100"></div>
          <div class="h-14 animate-pulse rounded-xl bg-slate-100"></div>
        </div>

        <div v-else-if="membros.length === 0" class="p-16 text-center">
          <p class="text-sm font-medium text-[var(--ct-ink)]">Nenhum membro cadastrado.</p>
          <p class="mt-1 text-sm text-[var(--ct-text-muted)]">
            Adicione usuários para distribuir acessos e responsabilidades.
          </p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="min-w-full">
            <thead class="border-b border-[var(--ct-border)] bg-slate-50/80">
              <tr>
                <th class="px-6 py-4 text-left text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500">
                  Usuário
                </th>
                <th class="px-6 py-4 text-center text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500">
                  Nível de acesso
                </th>
                <th
                  v-if="loggedUserRole === 'admin'"
                  class="px-6 py-4 text-right text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500"
                >
                  Ações
                </th>
              </tr>
            </thead>

            <tbody class="divide-y divide-[var(--ct-border)] bg-white">
              <tr
                v-for="membro in membros"
                :key="membro.id"
                class="transition-colors hover:bg-slate-50/70"
              >
                <td class="px-6 py-4">
                  <div class="flex items-center gap-3">
                    <div
                      class="flex h-11 w-11 items-center justify-center rounded-full bg-[var(--ct-primary-soft)] text-sm font-bold uppercase text-[var(--ct-primary)]"
                    >
                      {{ getInitials(membro.name) }}
                    </div>

                    <div class="min-w-0">
                      <p class="truncate text-sm font-semibold text-[var(--ct-ink)]">
                        {{ membro.name }}
                      </p>
                      <p class="truncate text-xs text-[var(--ct-text-muted)]">
                        {{ membro.email }}
                      </p>
                    </div>
                  </div>
                </td>

                <td class="px-6 py-4 text-center">
                  <span
                    class="inline-flex rounded-full border px-2.5 py-1 text-[11px] font-bold uppercase tracking-[0.08em]"
                    :class="getRoleBadge(membro.role)"
                  >
                    {{ formatRole(membro.role) }}
                  </span>
                </td>

                <td v-if="loggedUserRole === 'admin'" class="px-6 py-4">
                  <div class="flex justify-end">
                    <button
                      v-if="membro.id !== loggedUserId"
                      @click="removerMembro(membro)"
                      class="rounded-lg border border-red-200 bg-red-50 px-3 py-1.5 text-xs font-semibold text-red-600 transition-colors hover:bg-red-100"
                    >
                      Excluir
                    </button>

                    <span
                      v-else
                      class="inline-flex rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-400"
                    >
                      Você
                    </span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- modal -->
      <div
        v-if="isModalOpen"
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4 backdrop-blur-[2px]"
      >
        <div class="w-full max-w-md overflow-hidden rounded-2xl border border-[var(--ct-border)] bg-white shadow-2xl">
          <div class="flex items-center justify-between border-b border-[var(--ct-border)] bg-slate-50 px-6 py-5">
            <div>
              <h3 class="text-lg font-semibold text-[var(--ct-ink)]">Adicionar membro</h3>
              <p class="mt-1 text-xs text-[var(--ct-text-muted)]">
                Crie um novo acesso para a equipe.
              </p>
            </div>

            <button
              @click="isModalOpen = false"
              class="rounded-lg p-1 text-slate-400 transition-colors hover:bg-white hover:text-slate-700"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>

          <div class="space-y-4 p-6">
            <div>
              <label class="mb-1.5 block text-xs font-semibold uppercase tracking-[0.08em] text-slate-500">
                Nome completo
              </label>
              <input
                v-model="novoMembro.name"
                type="text"
                class="w-full rounded-xl border border-[var(--ct-border)] px-4 py-3 text-sm outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
              />
            </div>

            <div>
              <label class="mb-1.5 block text-xs font-semibold uppercase tracking-[0.08em] text-slate-500">
                E-mail
              </label>
              <input
                v-model="novoMembro.email"
                type="email"
                class="w-full rounded-xl border border-[var(--ct-border)] px-4 py-3 text-sm outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
              />
            </div>

            <div>
              <label class="mb-1.5 block text-xs font-semibold uppercase tracking-[0.08em] text-slate-500">
                Nível de acesso
              </label>
              <select
                v-model="novoMembro.role"
                class="w-full rounded-xl border border-[var(--ct-border)] bg-white px-4 py-3 text-sm outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
              >
                <option value="colaborador">Colaborador (visualiza e edita tarefas)</option>
                <option value="admin">Administrador (acesso total)</option>
              </select>
            </div>

            <div>
              <label class="mb-1.5 block text-xs font-semibold uppercase tracking-[0.08em] text-slate-500">
                Senha temporária
              </label>

              <div class="flex gap-2">
                <input
                  v-model="novoMembro.password"
                  type="text"
                  placeholder="Mínimo 6 caracteres"
                  class="flex-1 rounded-xl border border-[var(--ct-border)] px-4 py-3 text-sm outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
                />

                <button
                  type="button"
                  @click="gerarSenhaSugestao"
                  class="rounded-xl bg-[var(--ct-primary-soft)] px-3 py-2 text-xs font-semibold text-[var(--ct-primary)] transition-colors hover:bg-[#BFDBFE] whitespace-nowrap"
                >
                  Gerar senha
                </button>
              </div>

              <p class="mt-1.5 text-[11px] text-[var(--ct-text-muted)]">
                Entregue esta senha ao funcionário. Ele poderá alterá-la após o primeiro login.
              </p>
            </div>
          </div>

          <div class="flex justify-end gap-3 border-t border-[var(--ct-border)] bg-slate-50 px-6 py-4">
            <button
              @click="isModalOpen = false"
              class="rounded-xl px-4 py-2.5 text-sm font-medium text-slate-500 transition-colors hover:bg-slate-100"
            >
              Cancelar
            </button>

            <button
              @click="salvarMembro"
              class="rounded-xl bg-[var(--ct-primary)] px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[var(--ct-primary-hover)]"
            >
              Criar acesso
            </button>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>