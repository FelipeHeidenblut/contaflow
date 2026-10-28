<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import AppNavIcon from './AppNavIcon.vue'
import TrialNotice from './TrialNotice.vue'
import BrandMark from './BrandMark.vue'
import { useAuthStore } from '../stores/auth'

defineOptions({ name: 'AppLayout' })

defineProps<{ title?: string }>()

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()
const isMobileMenuOpen = ref(false)
const isAccountOpen = ref(false)
const search = ref('')
const searchTasks = () => {
  if (search.value.trim())
    void router.push({ path: '/obrigacoes', query: { busca: search.value.trim() } })
}

const allNavLinks = [
  { name: 'Início', path: '/dashboard', icon: 'home' },
  { name: 'Clientes', path: '/clientes', icon: 'users' },
  { name: 'Obrigações', path: '/obrigacoes', icon: 'clock' },
  { name: 'Calendário', path: '/calendario', icon: 'calendar' },
  { name: 'Documentos', path: '/documentos', icon: 'folder' },
  { name: 'Relatórios', path: '/relatorios', icon: 'reports', paidOnly: true },
  { name: 'Membros', path: '/membros', icon: 'team', managerOnly: true },
  { name: 'Planos', path: '/faturamento', icon: 'card', adminOnly: true },
]

const navLinks = computed(() => {
  if (authStore.role === 'admin') return allNavLinks
  if (authStore.role === 'gerente') return allNavLinks.filter((link) => !link.adminOnly)
  return allNavLinks.filter((link) => !link.adminOnly && !link.managerOnly)
})

const initials = computed(() => {
  const parts = (authStore.userName || authStore.userEmail || 'U').trim().split(/\s+/)
  return `${parts[0]?.[0] || ''}${parts.length > 1 ? parts.at(-1)?.[0] || '' : ''}`.toUpperCase()
})

const roleLabel = computed(() => {
  if (authStore.role === 'admin') return 'Administrador'
  if (authStore.role === 'gerente') return 'Gerente'
  return 'Colaborador'
})
const hasReportsAccess = computed(
  () => authStore.plan !== 'free' && authStore.paymentStatus === 'ativo',
)

const closeMenus = () => {
  isMobileMenuOpen.value = false
  isAccountOpen.value = false
}

const handleLogout = async () => {
  closeMenus()
  await authStore.logout()
  router.push('/login')
}

const closeOnEscape = (event: KeyboardEvent) => {
  if (event.key === 'Escape') closeMenus()
}

watch(route, closeMenus)
onMounted(() => document.addEventListener('keydown', closeOnEscape))
onBeforeUnmount(() => document.removeEventListener('keydown', closeOnEscape))
</script>

<template>
  <div class="ct-app-shell flex h-dvh overflow-hidden bg-[#f5f7fc] text-[var(--ct-ink)]">
    <button
      v-if="isMobileMenuOpen"
      type="button"
      aria-label="Fechar navegação"
      class="fixed inset-0 z-40 bg-slate-950/30 md:hidden"
      @click="closeMenus"
    />
    <aside
      class="fixed inset-y-0 left-0 z-50 flex w-[232px] shrink-0 flex-col border-r border-[#e7edf5] bg-gradient-to-br from-[#fbfcfe] to-[#f5f8fc] transition-transform md:relative md:translate-x-0"
      :class="isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <div class="flex h-[73px] shrink-0 items-center justify-between px-5">
        <RouterLink to="/dashboard" aria-label="Ir para o início"><BrandMark /></RouterLink
        ><button type="button" class="p-2 md:hidden" aria-label="Fechar menu" @click="closeMenus">
          ×
        </button>
      </div>
      <nav
        class="flex-1 space-y-[7px] overflow-y-auto px-[15px] py-5"
        aria-label="Navegação do escritório"
      >
        <RouterLink
          v-for="link in navLinks"
          :key="link.path"
          :to="link.path"
          class="flex min-h-[47px] items-center gap-[18px] rounded-[10px] px-4 text-sm font-medium transition-colors"
          :class="
            route.path === link.path
              ? 'bg-[#e7f0ff] text-blue-600'
              : 'text-[#536582] hover:bg-blue-50'
          "
        >
          <AppNavIcon :name="link.icon" /><span class="flex-1">{{ link.name }}</span
          ><span
            v-if="link.paidOnly && !hasReportsAccess"
            class="rounded bg-blue-50 px-1.5 py-0.5 text-[10px] text-blue-600"
            >Pro</span
          >
        </RouterLink>
      </nav>
      <div class="space-y-2 border-t border-slate-100 p-4">
        <RouterLink
          to="/contato"
          class="flex items-center gap-3 rounded-lg px-2 py-2 text-sm text-slate-500"
          ><span aria-hidden="true">?</span> Ajuda e contato</RouterLink
        >
        <p class="px-2 text-[11px] text-slate-400">ContablyTask · Seu escritório organizado</p>
      </div>
    </aside>
    <div class="flex min-w-0 flex-1 flex-col overflow-hidden">
      <header
        class="flex h-[73px] shrink-0 items-center justify-between gap-3 border-b border-[#e7edf5] bg-white px-4 sm:px-6"
      >
        <button
          class="shrink-0 rounded-lg p-2 text-slate-600 md:hidden"
          type="button"
          aria-label="Abrir menu"
          :aria-expanded="isMobileMenuOpen"
          @click="isMobileMenuOpen = true"
        >
          <AppNavIcon name="home" />
        </button>
        <form
          class="flex min-w-0 flex-1 max-w-[580px] items-center gap-2 rounded-lg bg-[#f2f5fa] px-3"
          role="search"
          @submit.prevent="searchTasks"
        >
          <label for="workspace-search" class="sr-only">Buscar obrigações pelo título</label
          ><svg
            class="h-4 w-4 shrink-0 text-slate-500"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <circle cx="10" cy="10" r="6" />
            <path d="m15 15 5 5" /></svg
          ><input
            id="workspace-search"
            v-model="search"
            type="search"
            maxlength="120"
            placeholder="Buscar obrigações…"
            class="min-w-0 flex-1 bg-transparent py-2.5 text-sm outline-none"
          /><button type="submit" class="rounded px-2 py-1 text-xs text-blue-600">Buscar</button>
        </form>
        <div class="relative shrink-0">
          <button
            type="button"
            class="flex items-center gap-3 rounded-xl p-1.5 text-left"
            aria-label="Opções da conta"
            :aria-expanded="isAccountOpen"
            @click="isAccountOpen = !isAccountOpen"
          >
            <span
              class="flex h-9 w-9 items-center justify-center rounded-full bg-violet-100 text-xs font-semibold text-violet-600"
              >{{ initials }}</span
            ><span class="hidden sm:block"
              ><span class="block max-w-40 truncate text-sm font-semibold">{{
                authStore.userName || 'Usuário'
              }}</span
              ><span class="block text-xs text-slate-500">{{ roleLabel }}</span></span
            ><span class="hidden text-slate-400 sm:block">⌄</span>
          </button>
          <div
            v-if="isAccountOpen"
            class="absolute right-0 top-full z-30 mt-2 w-64 rounded-xl border border-slate-100 bg-white p-3 shadow-lg"
          >
            <p class="truncate border-b border-slate-100 pb-3 text-xs text-slate-500">
              {{ authStore.userEmail }}
            </p>
            <RouterLink
              v-if="authStore.role === 'admin'"
              to="/faturamento"
              class="block rounded-lg px-2 py-3 text-sm hover:bg-blue-50"
              >Planos e faturamento</RouterLink
            ><button
              class="w-full rounded-lg px-2 py-3 text-left text-sm text-red-600 hover:bg-red-50"
              type="button"
              @click="handleLogout"
            >
              Sair do sistema
            </button>
          </div>
        </div>
      </header>
      <main class="flex-1 overflow-y-auto px-4 py-5 sm:px-6 lg:px-7">
        <div class="mx-auto w-full max-w-none"><TrialNotice /><slot /></div>
      </main>
    </div>
  </div>
</template>
