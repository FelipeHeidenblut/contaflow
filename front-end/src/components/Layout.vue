<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import AppNavIcon from './AppNavIcon.vue'
import BrandMark from './BrandMark.vue'
import { useAuthStore } from '../stores/auth'

defineOptions({ name: 'AppLayout' })

defineProps<{ title?: string }>()

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()
const isMobileMenuOpen = ref(false)
const isAccountOpen = ref(false)

const allNavLinks = [
  { name: 'Dashboard', path: '/dashboard', icon: 'home' },
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
  <div class="ct-app-shell flex h-dvh overflow-hidden bg-[#f7f9fc] text-[var(--ct-ink)]">
    <div
      v-if="isMobileMenuOpen"
      class="fixed inset-0 z-40 bg-slate-950/35 backdrop-blur-[2px] md:hidden"
      @click="isMobileMenuOpen = false"
    ></div>

    <aside
      class="fixed inset-y-0 left-0 z-50 flex w-[246px] flex-col border-r border-[#e6eaf1] bg-white transition-transform duration-300 md:relative md:translate-x-0"
      :class="isMobileMenuOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full'"
    >
      <div class="flex h-[78px] shrink-0 items-center justify-between px-6">
        <RouterLink to="/dashboard" aria-label="Ir para o dashboard"><BrandMark /></RouterLink>
        <button
          class="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-700 md:hidden"
          type="button"
          aria-label="Fechar menu"
          @click="isMobileMenuOpen = false"
        >
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-width="2" d="m6 6 12 12M18 6 6 18" />
          </svg>
        </button>
      </div>

      <nav
        class="flex-1 space-y-1.5 overflow-y-auto px-3 py-5"
        aria-label="Navegação do escritório"
      >
        <RouterLink
          v-for="link in navLinks"
          :key="link.path"
          :to="link.path"
          class="flex min-h-11 items-center gap-3 rounded-xl px-4 text-[14px] font-medium transition-colors"
          active-class="bg-[#eef4ff] text-[var(--ct-primary)]"
          exact-active-class="bg-[#eaf2ff] text-[var(--ct-primary)]"
          :class="
            route.path !== link.path
              ? 'text-[#52617a] hover:bg-slate-50 hover:text-[var(--ct-ink)]'
              : ''
          "
        >
          <AppNavIcon :name="link.icon" />
          <span class="flex-1">{{ link.name }}</span>
          <span
            v-if="link.paidOnly && !hasReportsAccess"
            class="rounded-md bg-amber-50 px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-wide text-amber-700"
            >Pro</span
          >
        </RouterLink>
      </nav>

      <div class="relative border-t border-[#edf0f5] p-3">
        <button
          class="flex w-full items-center gap-3 rounded-xl border border-[#e7ebf2] bg-[#fbfcfe] p-3 text-left transition-colors hover:bg-slate-50"
          type="button"
          aria-label="Abrir opções da conta"
          :aria-expanded="isAccountOpen"
          @click="isAccountOpen = !isAccountOpen"
        >
          <span
            class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[var(--ct-primary-soft)] text-xs font-bold text-[var(--ct-primary)]"
          >
            {{ initials }}
          </span>
          <span class="min-w-0 flex-1">
            <span class="block truncate text-xs font-semibold text-[var(--ct-ink)]">
              {{ authStore.userName || 'Usuário' }}
            </span>
            <span class="mt-0.5 block truncate text-[11px] text-[var(--ct-text-muted)]">
              {{ roleLabel }}
            </span>
          </span>
          <svg class="h-4 w-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="m8 10 4 4 4-4"
            />
          </svg>
        </button>

        <div
          v-if="isAccountOpen"
          class="absolute bottom-[76px] left-3 right-3 z-20 overflow-hidden rounded-xl border border-[var(--ct-border)] bg-white p-1.5 shadow-xl"
        >
          <div class="border-b border-[var(--ct-border)] px-3 py-2.5">
            <p class="truncate text-xs font-medium text-[var(--ct-text-muted)]">
              {{ authStore.userEmail }}
            </p>
          </div>
          <button
            class="mt-1 flex w-full items-center gap-2 rounded-lg px-3 py-2.5 text-left text-sm font-medium text-red-600 hover:bg-red-50"
            type="button"
            @click="handleLogout"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="m16 17 5-5-5-5m5 5H9m4 5v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v1"
              />
            </svg>
            Sair do sistema
          </button>
        </div>
      </div>
    </aside>

    <div class="flex min-w-0 flex-1 flex-col overflow-hidden">
      <header
        class="flex h-16 shrink-0 items-center justify-between border-b border-[#e6eaf1] bg-white px-4 md:hidden"
      >
        <button
          class="rounded-lg p-2 text-slate-600 hover:bg-slate-100"
          type="button"
          aria-label="Abrir menu"
          @click="isMobileMenuOpen = true"
        >
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <BrandMark compact />
        <span
          class="flex h-9 w-9 items-center justify-center rounded-full bg-[var(--ct-primary-soft)] text-xs font-bold text-[var(--ct-primary)]"
        >
          {{ initials }}
        </span>
      </header>

      <main class="flex-1 overflow-y-auto px-4 py-5 sm:px-6 md:px-7 md:py-6 xl:px-9">
        <div class="mx-auto w-full max-w-[1580px]"><slot /></div>
      </main>
    </div>
  </div>
</template>
