<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import api from '../services/api'
import Layout from '../components/Layout.vue'
import { toast } from 'vue3-toastify'
import { useAuthStore } from '../stores/auth'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import EmptyState from '../components/EmptyState.vue'
import { getApiErrorMessage } from '../utils/apiError'
import PaginationControls from '../components/PaginationControls.vue'
import { fetchPage } from '../services/pagination'
import CollectionViewToggle from '../components/CollectionViewToggle.vue'

interface Membro {
  id: string
  name: string
  email: string
  role: 'admin' | 'gerente' | 'colaborador'
  open_tasks_count?: number | null
  overdue_tasks_count?: number | null
}

const membros = ref<Membro[]>([])
const isLoading = ref(true)
const currentPage = ref(1)
const totalPages = ref(0)
const totalResults = ref(0)
const pageSize = 20
const searchQuery = ref('')
const roleFilter = ref('')
const visualizacao = ref<'cards' | 'lista'>('cards')
const memberSummary = ref({ total: 0, admins: 0, gerentes: 0, colaboradores: 0 })
const isModalOpen = ref(false)
const isSaving = ref(false)
const memberToRemove = ref<Membro | null>(null)
const authStore = useAuthStore()
const route = useRoute()

const loggedUserRole = computed(() => authStore.role)
const loggedUserId = computed(() => authStore.userId)

const novoMembro = ref({
  name: '',
  email: '',
  role: 'colaborador',
})

const fetchData = async () => {
  isLoading.value = true
  try {
    const page = await fetchPage<Membro>('/api/v1/membros', currentPage.value, pageSize, {
      include_workload: true,
      search: searchQuery.value.trim() || undefined,
      role: roleFilter.value || undefined,
    })
    membros.value = page.items
    totalPages.value = page.pages
    totalResults.value = page.total
    memberSummary.value = {
      total: page.summary?.total ?? page.total,
      admins: page.summary?.admins ?? 0,
      gerentes: page.summary?.gerentes ?? 0,
      colaboradores: page.summary?.colaboradores ?? 0,
    }
  } catch {
    toast.error('Erro ao carregar a equipe.')
  } finally {
    isLoading.value = false
  }
}

const changePage = (page: number) => {
  currentPage.value = page
  fetchData()
}

let filterTimer: ReturnType<typeof setTimeout> | undefined
watch([searchQuery, roleFilter], () => {
  if (filterTimer) clearTimeout(filterTimer)
  filterTimer = setTimeout(() => {
    currentPage.value = 1
    fetchData()
  }, 300)
})

const salvarMembro = async () => {
  if (!novoMembro.value.name || !novoMembro.value.email) {
    toast.warn('Preencha nome e e-mail.')
    return
  }

  try {
    isSaving.value = true
    await api.post('/api/v1/membros', novoMembro.value)
    toast.success('Convite enviado! O funcionário definirá a própria senha pelo e-mail.')
    isModalOpen.value = false
    novoMembro.value = { name: '', email: '', role: 'colaborador' }
    currentPage.value = 1
    await fetchData()
  } catch (error: unknown) {
    toast.error(getApiErrorMessage(error, 'Erro ao enviar convite.'))
  } finally {
    isSaving.value = false
  }
}

const removerMembro = async () => {
  const membro = memberToRemove.value
  if (!membro) return
  try {
    await api.delete(`/api/v1/membros/${membro.id}`)
    if (membros.value.length === 1 && currentPage.value > 1) currentPage.value -= 1
    await fetchData()
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

onUnmounted(() => {
  if (filterTimer) clearTimeout(filterTimer)
})

onMounted(() => {
  void fetchData()
  if (route.query.novo === '1' && authStore.role === 'admin') isModalOpen.value = true
})
</script>

<template>
  <Layout title="Membros e Acessos">
    <div class="ct-directory-workspace ct-workspace space-y-4">
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
          <span>Convidar membro</span>
        </button>
      </header>

      <section class="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
        <input
          v-model="searchQuery"
          type="search"
          aria-label="Buscar membros"
          placeholder="Buscar por nome ou e-mail..."
          class="w-full rounded-lg border border-[var(--ct-border)] bg-white px-4 py-2.5 text-sm text-[var(--ct-ink)] outline-none focus:border-[var(--ct-primary)] sm:max-w-md"
        />
        <select
          v-model="roleFilter"
          aria-label="Filtrar membros por nível de acesso"
          class="w-full rounded-lg border border-[var(--ct-border)] bg-white px-4 py-2.5 text-sm text-[var(--ct-ink)] outline-none focus:border-[var(--ct-primary)] sm:w-56"
        >
          <option value="">Todos os níveis</option>
          <option value="admin">Administradores</option>
          <option value="gerente">Gerentes</option>
          <option value="colaborador">Colaboradores</option>
        </select>
        <div class="flex flex-wrap items-center gap-3">
          <span class="text-xs text-slate-500">{{ totalResults }} resultado(s)</span
          ><CollectionViewToggle v-model="visualizacao" />
        </div>
      </section>

      <!-- tabela -->
      <section
        :class="
          visualizacao === 'lista' || isLoading || !membros.length
            ? 'ct-data-panel overflow-hidden rounded-xl border border-[var(--ct-border)] bg-white'
            : ''
        "
      >
        <div v-if="isLoading" class="space-y-3 p-6">
          <div class="h-14 animate-pulse rounded-xl bg-slate-100"></div>
          <div class="h-14 animate-pulse rounded-xl bg-slate-100"></div>
          <div class="h-14 animate-pulse rounded-xl bg-slate-100"></div>
        </div>

        <EmptyState
          v-else-if="membros.length === 0"
          :title="
            memberSummary.total === 0 ? 'Nenhum membro cadastrado' : 'Nenhum membro encontrado'
          "
          :description="
            memberSummary.total === 0
              ? 'Adicione usuários para distribuir acessos e responsabilidades.'
              : 'Ajuste a busca ou o filtro de nível de acesso.'
          "
          :action-label="
            memberSummary.total === 0 && loggedUserRole === 'admin' ? 'Convidar membro' : undefined
          "
          @action="isModalOpen = true"
        />

        <div
          v-else-if="visualizacao === 'cards'"
          class="ct-directory-grid grid gap-4 sm:grid-cols-2 xl:grid-cols-3"
          aria-label="Membros da equipe"
        >
          <article
            v-for="membro in membros"
            :key="membro.id"
            class="ct-directory-card flex min-w-0 flex-col rounded-xl border border-[#e7edf5] bg-white p-5"
            :aria-label="membro.name"
          >
            <div class="mb-4 flex items-start justify-between gap-3">
              <span
                class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-blue-50 text-xs font-semibold text-blue-500"
                aria-hidden="true"
                >{{ getIniciaisMembro(membro.name) }}</span
              >
              <span
                v-if="membro.id === loggedUserId"
                class="rounded-full bg-blue-50 px-2 py-1 text-[10px] text-blue-500"
                >Você</span
              >
              <button
                v-else-if="loggedUserRole === 'admin'"
                type="button"
                :aria-label="`Remover ${membro.name}`"
                title="Remover membro"
                class="rounded px-2 py-1 text-lg leading-none text-slate-400 hover:bg-rose-50 hover:text-rose-500"
                @click="memberToRemove = membro"
              >
                ⋮
              </button>
            </div>
            <h2 class="text-sm font-semibold leading-6 text-slate-900">{{ membro.name }}</h2>
            <p class="mt-2 break-words text-xs leading-6 text-slate-500">{{ membro.email }}</p>
            <div class="mb-5 mt-3">
              <span
                class="inline-flex rounded-full border px-2.5 py-1 text-[11px] font-medium"
                :class="getRoleBadge(membro.role)"
                >{{ formatRole(membro.role) }}</span
              >
            </div>
            <div
              class="mt-auto flex flex-wrap items-center justify-between gap-3 border-t border-[#edf1f7] pt-4"
            >
              <div class="flex flex-wrap items-center gap-2 text-xs text-slate-500">
                <span v-if="membro.open_tasks_count != null"
                  >{{ membro.open_tasks_count }}
                  {{ membro.open_tasks_count === 1 ? 'tarefa aberta' : 'tarefas abertas' }}</span
                >
                <span v-else title="Atualize a página para tentar novamente"
                  >Tarefas indisponíveis</span
                >
                <span
                  v-if="membro.overdue_tasks_count"
                  class="rounded-full bg-rose-50 px-2 py-1 text-[10px] text-rose-500"
                  >{{ membro.overdue_tasks_count }} em atraso</span
                >
              </div>
              <RouterLink
                :to="{ path: '/obrigacoes', query: { responsavel: membro.id } }"
                class="text-xs font-medium text-blue-500 hover:underline"
                :aria-label="`Ver tarefas de ${membro.name}`"
                >Ver tarefas →</RouterLink
              >
            </div>
          </article>
        </div>

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
        <PaginationControls
          :class="
            visualizacao === 'cards' ? 'mt-4 rounded-xl border border-[#e7edf5] bg-white' : ''
          "
          :page="currentPage"
          :pages="totalPages"
          :total="totalResults"
          @change="changePage"
        />
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
                Convidar membro
              </h3>
              <p class="mt-1 text-xs text-[var(--ct-text-muted)]">
                O funcionário receberá um link seguro para definir a própria senha.
              </p>
            </div>

            <button
              @click="isModalOpen = false"
              aria-label="Fechar convite de membro"
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

            <p
              class="rounded-xl border border-[var(--ct-border)] bg-[var(--ct-primary-soft)] px-4 py-3 text-xs leading-5 text-[var(--ct-text-muted)]"
            >
              O convite expira conforme a configuração de segurança do Supabase. Se o link expirar,
              será necessário enviar um novo convite.
            </p>
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
              {{ isSaving ? 'Enviando convite...' : 'Enviar convite' }}
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
