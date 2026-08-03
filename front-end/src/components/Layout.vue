<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { supabase } from '../services/supabase'
import { useAuthStore } from '../stores/auth'
import api from '../services/api'

const authStore = useAuthStore()

const props = defineProps<{
  title?: string
}>()

const route = useRoute()
const router = useRouter()

const isMobileMenuOpen = ref(false)
const isDropdownOpen = ref(false)

const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
}

const closeDropdown = () => {
  isDropdownOpen.value = false
}

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

const closeMobileMenu = () => {
  isMobileMenuOpen.value = false
}

watch(route, () => {
  closeMobileMenu()
  closeDropdown()
})

const handleLogout = async () => {
  closeDropdown()
  closeMobileMenu()
  await supabase.auth.signOut()
  router.push('/login')
}

const allNavLinks = [
  { name: 'Dashboard', path: '/dashboard', icon: 'home' },
  { name: 'Clientes', path: '/clientes', icon: 'users' },
  { name: 'Obrigações', path: '/obrigacoes', icon: 'clock' },
  { name: 'Calendário', path: '/calendario', icon: 'calendar' },
  { name: 'Documentos', path: '/documentos', icon: 'folder' },
  { name: 'Membros', path: '/membros', icon: 'team', adminOnly: true },
  { name: 'Planos', path: '/faturamento', icon: 'card', adminOnly: true },
]

const navLinks = computed(() => {
  if (authStore.role === 'admin') return allNavLinks
  return allNavLinks.filter((link) => !link.adminOnly)
})

const loggedUser = ref({
  name: 'Carregando...',
  email: '',
  initials: '...',
})

const gerarIniciais = (nome: string): string => {
  if (!nome) return '?'
  const partes = nome.trim().split(' ').filter((p) => p)
  if (partes.length === 0) return '?'
  if (partes.length === 1) return (partes[0]?.charAt(0) || '?').toUpperCase()
  const primeiraLetra = partes[0]?.charAt(0) || ''
  const ultimaLetra = partes[partes.length - 1]?.charAt(0) || ''
  return (primeiraLetra + ultimaLetra).toUpperCase() || '?'
}

onMounted(async () => {
  const { data } = await supabase.auth.getUser()

  if (data?.user) {
    const nomeReal =
      data.user.user_metadata?.name ||
      data.user.user_metadata?.full_name ||
      data.user.email ||
      'Usuário'

    loggedUser.value = {
      name: nomeReal,
      email: data.user.email || '',
      initials: gerarIniciais(nomeReal),
    }
  }

  try {
    const res = await api.get('/api/v1/auth/me')
    authStore.setRole(res.data.role)
  } catch (e) {
    console.error('Erro ao buscar permissões:', e)
  }
})
</script>

<template>
  <div class="flex h-screen overflow-hidden bg-[var(--ct-bg)] text-[var(--ct-ink)]">
    <!-- Overlay mobile -->
    <div
      v-if="isMobileMenuOpen"
      @click="closeMobileMenu"
      class="fixed inset-0 z-40 bg-slate-950/40 backdrop-blur-[2px] md:hidden"
    ></div>

    <!-- Sidebar mobile -->
    <aside
      :class="[isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full']"
      class="fixed inset-y-4 left-4 z-50 flex w-[272px] flex-col overflow-hidden rounded-2xl border border-white/10 bg-[var(--ct-navy)] text-white shadow-2xl transition-transform duration-300 ease-out md:hidden"
    >
      <div class="flex h-16 items-center justify-between border-b border-white/10 px-5">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-2xl bg-white/10">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="#93C5FD"
              stroke-width="2.2"
              class="h-5 w-5"
            >
              <path d="M9 11l3 3L22 4" />
              <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" />
            </svg>
          </div>
          <span class="text-lg font-semibold tracking-tight">
            Contably<span class="text-[#93C5FD]">Task</span>
          </span>
        </div>

        <button
          @click="closeMobileMenu"
          class="rounded-lg p-1 text-white/60 transition-colors hover:bg-white/5 hover:text-white"
        >
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <nav class="flex-1 space-y-1 overflow-y-auto px-3 py-4">
        <RouterLink
          v-for="link in navLinks"
          :key="link.path"
          :to="link.path"
          custom
          v-slot="{ isActive, navigate }"
        >
          <button
            @click="navigate"
            class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-medium transition-all duration-200"
            :class="
              isActive
                ? 'bg-white text-[var(--ct-navy)] shadow-sm'
                : 'text-white/65 hover:bg-white/5 hover:text-white'
            "
          >
            <svg v-if="link.icon === 'home'" class="h-5 w-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
            </svg>
            <svg v-if="link.icon === 'users'" class="h-5 w-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/>
            </svg>
            <svg v-if="link.icon === 'clock'" class="h-5 w-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0"/>
            </svg>
            <svg v-if="link.icon === 'calendar'" class="h-5 w-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
            <svg v-if="link.icon === 'folder'" class="h-5 w-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
            </svg>
            <svg v-if="link.icon === 'team'" class="h-5 w-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
            </svg>
            <svg v-if="link.icon === 'card'" class="h-5 w-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"/>
            </svg>
            <span>{{ link.name }}</span>
          </button>
        </RouterLink>
      </nav>

      <div class="border-t border-white/10 p-3">
        <div class="mb-3 rounded-xl bg-white/5 p-3">
          <p class="truncate text-sm font-medium text-white">{{ loggedUser.name }}</p>
          <p class="truncate text-xs text-white/50">{{ loggedUser.email }}</p>
        </div>

        <button
          @click="handleLogout"
          class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-white/60 transition-all hover:bg-white/5 hover:text-red-300"
        >
          <svg class="h-5 w-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
          </svg>
          <span>Sair do sistema</span>
        </button>
      </div>
    </aside>

    <!-- Sidebar desktop -->
    <aside
      class="m-4 mr-2 hidden w-[272px] flex-shrink-0 flex-col overflow-hidden rounded-2xl border border-white/10 bg-[var(--ct-navy)] text-white shadow-xl md:flex"
    >
      <div class="flex h-16 items-center gap-3 border-b border-white/10 px-5">
        <div class="flex h-10 w-10 items-center justify-center rounded-2xl bg-white/10">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="#93C5FD"
            stroke-width="2.2"
            class="h-5 w-5"
          >
            <path d="M9 11l3 3L22 4" />
            <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" />
          </svg>
        </div>
        <span class="text-lg font-semibold tracking-tight">
          Contably<span class="text-[#93C5FD]">Task</span>
        </span>
      </div>

      <nav class="flex-1 space-y-1 overflow-y-auto px-3 py-4">
        <RouterLink
          v-for="link in navLinks"
          :key="link.path"
          :to="link.path"
          custom
          v-slot="{ isActive, navigate }"
        >
          <button
            @click="navigate"
            class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-medium transition-all duration-200"
            :class="
              isActive
                ? 'bg-white text-[var(--ct-navy)] shadow-sm'
                : 'text-white/65 hover:bg-white/5 hover:text-white'
            "
          >
            <svg v-if="link.icon === 'home'" class="h-5 w-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
            </svg>
            <svg v-if="link.icon === 'users'" class="h-5 w-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/>
            </svg>
            <svg v-if="link.icon === 'clock'" class="h-5 w-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0"/>
            </svg>
            <svg v-if="link.icon === 'calendar'" class="h-5 w-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
            <svg v-if="link.icon === 'folder'" class="h-5 w-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
            </svg>
            <svg v-if="link.icon === 'team'" class="h-5 w-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
            </svg>
            <svg v-if="link.icon === 'card'" class="h-5 w-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"/>
            </svg>
            <span>{{ link.name }}</span>
          </button>
        </RouterLink>
      </nav>

      <div class="border-t border-white/10 p-3">
        <button
          @click="handleLogout"
          class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-white/60 transition-all hover:bg-white/5 hover:text-red-300"
        >
          <svg class="h-5 w-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
          </svg>
          <span>Sair do sistema</span>
        </button>
      </div>
    </aside>

    <!-- Área principal -->
    <div class="flex min-w-0 flex-1 flex-col overflow-hidden">
      <!-- Topbar -->
      <header
        class="z-10 mx-2 my-4 flex h-16 items-center justify-between rounded-2xl border border-[var(--ct-border)] bg-white px-4 shadow-sm md:mx-4 md:px-6"
      >
        <div class="flex min-w-0 items-center gap-3">
          <button
            @click="toggleMobileMenu"
            class="rounded-lg p-2 text-[var(--ct-text-muted)] transition-colors hover:bg-slate-50 hover:text-[var(--ct-ink)] md:hidden"
          >
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <div class="min-w-0">
            <h1 class="truncate text-base font-semibold tracking-tight text-[var(--ct-ink)] md:text-lg">
              <slot name="title">{{ props.title }}</slot>
            </h1>
            <p class="hidden text-xs text-[var(--ct-text-muted)] sm:block">
              Painel de gestão do escritório
            </p>
          </div>
        </div>

        <div class="relative flex items-center gap-3 sm:gap-4">
          <button
            class="relative hidden rounded-full p-2 text-[var(--ct-text-muted)] transition-colors hover:bg-slate-50 hover:text-[var(--ct-ink)] sm:block"
          >
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
              />
            </svg>
            <span class="absolute right-2 top-2 h-2 w-2 rounded-full bg-[var(--ct-primary)]"></span>
          </button>

          <div class="relative">
            <button
              @click="toggleDropdown"
              class="flex items-center gap-3 rounded-full border border-transparent p-1 transition-colors focus:outline-none focus:ring-2 focus:ring-[var(--ct-primary)]/20"
            >
              <div class="hidden text-right md:block">
                <p class="text-[13px] font-semibold leading-tight text-[var(--ct-ink)]">
                  {{ loggedUser.name }}
                </p>
                <p class="text-[11px] leading-tight text-[var(--ct-text-muted)]">
                  {{ loggedUser.email }}
                </p>
              </div>

              <div
                class="flex h-10 w-10 items-center justify-center rounded-full bg-[var(--ct-primary-soft)] text-sm font-semibold text-[var(--ct-primary)]"
              >
                {{ loggedUser.initials }}
              </div>
            </button>

            <div
              v-if="isDropdownOpen"
              @click="closeDropdown"
              class="fixed inset-0 z-10 h-full w-full cursor-default"
            ></div>

            <div
              v-if="isDropdownOpen"
              class="absolute right-0 z-20 mt-2 w-60 overflow-hidden rounded-2xl border border-[var(--ct-border)] bg-white shadow-xl"
            >
              <div class="border-b border-[var(--ct-border)] px-4 py-3">
                <p class="text-sm font-semibold text-[var(--ct-ink)]">{{ loggedUser.name }}</p>
                <p class="truncate text-xs text-[var(--ct-text-muted)]">{{ loggedUser.email }}</p>
              </div>

              <div class="p-1.5">
                <button
                  @click="handleLogout"
                  class="flex w-full items-center gap-2 rounded-xl px-3 py-2.5 text-left text-sm font-medium text-red-600 transition-colors hover:bg-red-50"
                >
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
                  </svg>
                  Sair do sistema
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- Conteúdo -->
      <main
        class="mx-2 mb-4 flex-1 overflow-y-auto rounded-2xl border border-[var(--ct-border)] bg-white p-5 shadow-sm md:mx-4 md:p-6"
      >
        <slot></slot>
      </main>
    </div>
  </div>
</template>

<style scoped>
:global(:root) {
  --ct-bg: #F8FAFC;
  --ct-surface: #FFFFFF;
  --ct-muted: #F1F5F9;
  --ct-border: #E2E8F0;

  --ct-ink: #0F172A;
  --ct-text-muted: #64748B;

  --ct-primary: #2563EB;
  --ct-primary-hover: #1D4ED8;
  --ct-primary-soft: #DBEAFE;
  --ct-navy: #172554;
}
</style>