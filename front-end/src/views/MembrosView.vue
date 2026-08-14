<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '../services/api'
import Layout from '../components/Layout.vue'
import { toast } from 'vue3-toastify'
import { useAuthStore } from '../stores/auth'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import EmptyState from '../components/EmptyState.vue'
import { getApiErrorMessage } from '../utils/apiError'

interface Membro {
  id: string
  name: string
  email: string
  role: 'admin' | 'gerente' | 'colaborador'
}

const membros = ref<Membro[]>([])
const isLoading = ref(true)
const isModalOpen = ref(false)
const isSaving = ref(false)
const memberToRemove = ref<Membro | null>(null)
const authStore = useAuthStore()

const loggedUserRole = computed(() => authStore.role)
const loggedUserId = computed(() => authStore.userId)

const novoMembro = ref({
  name: '',
  email: '',
  role: 'colaborador',
  password: '',
})

const totalMembros = computed(() => membros.value.length)
const totalAdmins = computed(() => membros.value.filter((m) => m.role === 'admin').length)
const totalGerentes = computed(() => membros.value.filter((m) => m.role === 'gerente').length)
const totalColaboradores = computed(
  () => membros.value.filter((m) => m.role === 'colaborador').length,
)

const gerarSenhaSugestao = () => {
  const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#'
  const random = new Uint32Array(14)
  crypto.getRandomValues(random)
  const senha = Array.from(random, (value) => chars[value % chars.length]).join('')
  novoMembro.value.password = senha
}

const fetchData = async () => {
  isLoading.value = true
  try {
    const response = await api.get('/api/v1/membros')
    membros.value = response.data
  } catch {
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

  if (novoMembro.value.password.length < 8) {
    toast.warn('A senha deve ter no mínimo 8 caracteres.')
    return
  }

  try {
    isSaving.value = true
    const response = await api.post('/api/v1/membros', novoMembro.value)
    membros.value.push(response.data)
    toast.success('Membro criado com sucesso! Ele já pode fazer login com a senha definida.')
    isModalOpen.value = false
    novoMembro.value = { name: '', email: '', role: 'colaborador', password: '' }
  } catch (error: unknown) {
    toast.error(getApiErrorMessage(error, 'Erro ao adicionar membro.'))
  } finally {
    isSaving.value = false
  }
}

const removerMembro = async () => {
  const membro = memberToRemove.value
  if (!membro) return
  try {
    await api.delete(`/api/v1/membros/${membro.id}`)
    membros.value = membros.value.filter((m) => m.id !== membro.id)
    toast.success('Membro removido com sucesso.')
    memberToRemove.value = null
  } catch (error: unknown) {
    toast.error(getApiErrorMessage(error, 'Erro ao remover membro.'))
  }
}

const getRoleBadge = (role: string) => {
  if (role === 'admin') return 'bg-violet-100 text-violet-700 border-violet-200'
  if (role === 'gerente') return 'bg-amber-100 text-amber-700 border-amber-200'
  return 'bg-[var(--ct-primary-soft)] text-[var(--ct-primary)] border-[var(--ct-border)]'
}

const formatRole = (role: string) => {
  if (role === 'admin') return 'Administrador'
  if (role === 'gerente') return 'Gerente'
  if (role === 'colaborador') return 'Colaborador'
  return role
}

const getIniciaisMembro = (nome: string) => {
  if (!nome) return '?'

  // Renomeie de 'parts' para 'partes' para manter o padrão, ou mantenha 'parts' se preferir
  const partes = nome
    .trim()
    .split(' ')
    .filter((p) => p)

  if (partes.length === 0) return '?'

  // Usando ?. e || para evitar o erro de 'Object is possibly undefined'
  if (partes.length === 1) return (partes[0]?.charAt(0) || '?').toUpperCase()

  const primeiraLetra = partes[0]?.charAt(0) || ''
  const ultimaLetra = partes[partes.length - 1]?.charAt(0) || ''

  // Adicionei a crave de fechamento ` no final que estava faltando
  return (primeiraLetra + ultimaLetra).toUpperCase() || '?'
}

onMounted(() => fetchData())
</script>

<template>
  <Layout title="Membros e Acessos">
    <div class="ct-workspace space-y-4">
      <!-- cabeçalho -->
      <header
        class="ct-page-header flex flex-col gap-4 border-b border-[var(--ct-border)] pb-5 xl:flex-row xl:items-end xl:justify-between"
      >
        <div>
          <h1 class="ct-page-title text-2xl font-semibold tracking-tight text-[var(--ct-ink)]">
            Membros da equipe
          </h1>
          <p class="ct-page-description mt-1 text-sm text-[var(--ct-text-muted)]">
            Gerencie usuários, níveis de acesso e permissões internas do escritório.
          </p>
        </div>

        <button
          v-if="loggedUserRole === 'admin'"
          @click="isModalOpen = true"
          class="ct-primary-action inline-flex w-full items-center justify-center gap-2 rounded-lg bg-[var(--ct-primary)] px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[var(--ct-primary-hover)] sm:w-auto"
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
      <section
        class="ct-summary-grid flex flex-wrap items-center gap-x-10 gap-y-4 border-b border-[var(--ct-border)] pb-5"
      >
        <div class="flex items-baseline gap-2">
          <p class="text-xs font-medium text-[var(--ct-text-muted)]">Total de membros</p>
          <p class="text-xl font-semibold text-[var(--ct-ink)] [font-variant-numeric:tabular-nums]">
            {{ totalMembros }}
          </p>
        </div>

        <div class="flex items-baseline gap-2">
          <p class="text-xs font-medium text-[var(--ct-text-muted)]">Gerentes</p>
          <p class="text-xl font-semibold text-[var(--ct-ink)] [font-variant-numeric:tabular-nums]">
            {{ totalGerentes }}
          </p>
        </div>

        <div class="flex items-baseline gap-2">
          <p class="text-xs font-medium text-[var(--ct-text-muted)]">Administradores</p>
          <p class="text-xl font-semibold text-[var(--ct-ink)] [font-variant-numeric:tabular-nums]">
            {{ totalAdmins }}
          </p>
        </div>

        <div class="flex items-baseline gap-2">
          <p class="text-xs font-medium text-[var(--ct-text-muted)]">Colaboradores</p>
          <p class="text-xl font-semibold text-[var(--ct-ink)] [font-variant-numeric:tabular-nums]">
            {{ totalColaboradores }}
          </p>
        </div>
      </section>

      <!-- tabela -->
      <section
        class="ct-data-panel overflow-hidden rounded-xl border border-[var(--ct-border)] bg-white"
      >
        <div v-if="isLoading" class="space-y-3 p-6">
          <div class="h-14 animate-pulse rounded-xl bg-slate-100"></div>
          <div class="h-14 animate-pulse rounded-xl bg-slate-100"></div>
          <div class="h-14 animate-pulse rounded-xl bg-slate-100"></div>
        </div>

        <EmptyState
          v-else-if="membros.length === 0"
          title="Nenhum membro cadastrado"
          description="Adicione usuários para distribuir acessos e responsabilidades."
          :action-label="loggedUserRole === 'admin' ? 'Adicionar membro' : undefined"
          @action="isModalOpen = true"
        />

        <div v-else class="overflow-x-auto">
          <div class="divide-y divide-[var(--ct-border)] md:hidden">
            <article
              v-for="membro in membros"
              :key="`mobile-${membro.id}`"
              class="flex items-center justify-between gap-3 p-4"
            >
              <div class="min-w-0">
                <p class="truncate text-sm font-semibold text-[var(--ct-ink)]">{{ membro.name }}</p>
                <p class="truncate text-xs text-[var(--ct-text-muted)]">{{ membro.email }}</p>
                <span
                  class="mt-2 inline-flex rounded-lg border px-2 py-1 text-[11px] font-semibold"
                  :class="getRoleBadge(membro.role)"
                  >{{ formatRole(membro.role) }}</span
                >
              </div>
              <button
                v-if="loggedUserRole === 'admin' && membro.id !== loggedUserId"
                class="text-xs font-semibold text-red-600"
                @click="memberToRemove = membro"
              >
                Remover</button
              ><span
                v-else-if="membro.id === loggedUserId"
                class="text-xs font-medium text-slate-400"
                >Você</span
              >
            </article>
          </div>
          <table class="hidden min-w-full md:table">
            <thead class="border-b border-[var(--ct-border)] bg-slate-50/80">
              <tr>
                <th
                  class="px-6 py-4 text-left text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500"
                >
                  Usuário
                </th>
                <th
                  class="px-6 py-4 text-center text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500"
                >
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
                      {{ getIniciaisMembro(membro.name) }}
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
                      @click="memberToRemove = membro"
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
        v-focus-trap
        role="dialog"
        aria-modal="true"
        aria-labelledby="member-modal-title"
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4 backdrop-blur-[2px]"
      >
        <div
          class="w-full max-w-md overflow-hidden rounded-xl border border-[var(--ct-border)] bg-white shadow-2xl"
        >
          <div
            class="flex items-center justify-between border-b border-[var(--ct-border)] bg-slate-50 px-6 py-5"
          >
            <div>
              <h3 id="member-modal-title" class="text-lg font-semibold text-[var(--ct-ink)]">
                Adicionar membro
              </h3>
              <p class="mt-1 text-xs text-[var(--ct-text-muted)]">
                Crie um novo acesso para a equipe.
              </p>
            </div>

            <button
              @click="isModalOpen = false"
              aria-label="Fechar cadastro de membro"
              class="rounded-lg p-1 text-slate-400 transition-colors hover:bg-white hover:text-slate-700"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          <form id="member-form" class="space-y-4 p-6" @submit.prevent="salvarMembro">
            <div>
              <label
                for="member-name"
                class="mb-1.5 block text-xs font-semibold uppercase tracking-[0.08em] text-slate-500"
              >
                Nome completo
              </label>
              <input
                v-model="novoMembro.name"
                id="member-name"
                autocomplete="name"
                required
                autofocus
                type="text"
                class="w-full rounded-xl border border-[var(--ct-border)] px-4 py-3 text-sm outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
              />
            </div>

            <div>
              <label
                for="member-email"
                class="mb-1.5 block text-xs font-semibold uppercase tracking-[0.08em] text-slate-500"
              >
                E-mail
              </label>
              <input
                v-model="novoMembro.email"
                id="member-email"
                autocomplete="email"
                required
                type="email"
                class="w-full rounded-xl border border-[var(--ct-border)] px-4 py-3 text-sm outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
              />
            </div>

            <div>
              <label
                for="member-role"
                class="mb-1.5 block text-xs font-semibold uppercase tracking-[0.08em] text-slate-500"
              >
                Nível de acesso
              </label>
              <select
                v-model="novoMembro.role"
                id="member-role"
                class="w-full rounded-xl border border-[var(--ct-border)] bg-white px-4 py-3 text-sm outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
              >
                <option value="colaborador">Colaborador (visualiza e edita tarefas)</option>
                <option value="gerente">Gerente (distribui clientes e gerencia a operação)</option>
                <option value="admin">Administrador (acesso completo, equipe e cobrança)</option>
              </select>
            </div>

            <div>
              <label
                for="member-password"
                class="mb-1.5 block text-xs font-semibold uppercase tracking-[0.08em] text-slate-500"
              >
                Senha temporária
              </label>

              <div class="flex gap-2">
                <input
                  v-model="novoMembro.password"
                  id="member-password"
                  autocomplete="new-password"
                  required
                  minlength="8"
                  maxlength="72"
                  type="text"
                  placeholder="Mínimo 8 caracteres"
                  class="flex-1 rounded-xl border border-[var(--ct-border)] px-4 py-3 text-sm outline-none transition focus:border-[var(--ct-primary)] focus:ring-4 focus:ring-[var(--ct-primary)]/10"
                />

                <button
                  type="button"
                  @click="gerarSenhaSugestao"
                  class="whitespace-nowrap rounded-xl bg-[var(--ct-primary-soft)] px-3 py-2 text-xs font-semibold text-[var(--ct-primary)] transition-colors hover:bg-[var(--ct-accent-soft)]"
                >
                  Gerar senha
                </button>
              </div>

              <p class="mt-1.5 text-[11px] text-[var(--ct-text-muted)]">
                Entregue esta senha ao funcionário. Ele poderá alterá-la após o primeiro login.
              </p>
            </div>
          </form>

          <div
            class="flex justify-end gap-3 border-t border-[var(--ct-border)] bg-slate-50 px-6 py-4"
          >
            <button
              @click="isModalOpen = false"
              class="rounded-xl px-4 py-2.5 text-sm font-medium text-slate-500 transition-colors hover:bg-slate-100"
            >
              Cancelar
            </button>

            <button
              type="submit"
              form="member-form"
              :disabled="isSaving"
              class="rounded-xl bg-[var(--ct-primary)] px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[var(--ct-primary-hover)]"
            >
              {{ isSaving ? 'Criando acesso...' : 'Criar acesso' }}
            </button>
          </div>
        </div>
      </div>
      <ConfirmDialog
        :open="!!memberToRemove"
        title="Remover membro"
        :message="`Deseja remover ${memberToRemove?.name || 'este membro'} da equipe?`"
        confirm-label="Remover membro"
        @close="memberToRemove = null"
        @confirm="removerMembro"
      />
    </div>
  </Layout>
</template>
