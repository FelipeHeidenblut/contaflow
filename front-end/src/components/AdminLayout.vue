<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, RouterLink, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import BrandMark from './BrandMark.vue'

defineProps<{
  title?: string
}>()

const router = useRouter()
const authStore = useAuthStore()
const route = useRoute()
const isSidebarOpen = ref(false)

const handleLogout = async () => {
  await authStore.logout()
  router.push('/ops-login')
}

// Menu exclusivo do Super Admin
const adminMenu = [
  {
    name: 'Visão geral',
    path: '/admin',
    icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
  },
]

watch(route, () => {
  isSidebarOpen.value = false
})
const closeOnEscape = (event: KeyboardEvent) => {
  if (event.key === 'Escape') isSidebarOpen.value = false
}
onMounted(() => document.addEventListener('keydown', closeOnEscape))
onBeforeUnmount(() => document.removeEventListener('keydown', closeOnEscape))
</script>

<template>
  <div class="ct-app-shell flex min-h-screen bg-[var(--ct-bg)]">
    <aside
      class="fixed z-20 flex h-full w-64 flex-col bg-[var(--ct-navy)] text-white transition-transform duration-300"
      :class="isSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'"
    >
      <div class="flex h-16 items-center justify-between border-b border-white/10 px-5">
        <div>
          <BrandMark inverse />
          <span
            class="mt-1 inline-flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-[0.12em] text-blue-200"
          >
            <span class="h-1.5 w-1.5 rounded-full bg-blue-400"></span>
            Administração
          </span>
        </div>
        <button
          aria-label="Fechar menu"
          @click="isSidebarOpen = false"
          class="text-gray-400 hover:text-white md:hidden"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            ></path>
          </svg>
        </button>
      </div>

      <nav class="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
        <RouterLink
          v-for="item in adminMenu"
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium transition-colors"
          :class="
            route.path === item.path
              ? 'bg-white/10 text-white'
              : 'text-gray-400 hover:bg-white/5 hover:text-white'
          "
        >
          <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              :d="item.icon"
            ></path>
          </svg>
          {{ item.name }}
        </RouterLink>
      </nav>

      <div class="border-t border-white/10 p-4">
        <div class="mb-3 rounded-xl border border-white/10 bg-white/[0.04] px-3 py-3">
          <p class="truncate text-xs font-medium text-white">
            {{ authStore.userName || 'Superadmin' }}
          </p>
          <p class="mt-0.5 truncate text-[10px] text-slate-400">{{ authStore.userEmail }}</p>
        </div>
        <button
          @click="handleLogout"
          class="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg font-medium text-gray-400 hover:bg-red-500/10 hover:text-red-400 transition-colors"
        >
          <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
            ></path>
          </svg>
          Sair do Backoffice
        </button>
      </div>
    </aside>

    <!-- Overlay Mobile -->
    <div
      v-if="isSidebarOpen"
      role="button"
      aria-label="Fechar menu"
      @click="isSidebarOpen = false"
      class="fixed inset-0 bg-black/50 z-10 md:hidden"
    ></div>

    <!-- Main Content -->
    <main class="flex-1 md:ml-64 flex flex-col min-w-0">
      <!-- Topbar Header -->
      <header
        class="bg-white h-16 border-b flex items-center justify-between px-4 sm:px-6 sticky top-0 z-10"
      >
        <div class="flex items-center gap-4">
          <button
            aria-label="Abrir menu"
            @click="isSidebarOpen = true"
            class="text-gray-500 hover:text-gray-700 md:hidden"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16"
              ></path>
            </svg>
          </button>
          <p
            v-if="title"
            class="text-xs font-semibold uppercase tracking-[0.1em] text-[var(--ct-text-muted)]"
          >
            {{ title }}
          </p>
        </div>
        <div class="hidden items-center gap-2 text-xs font-medium text-emerald-700 sm:flex">
          <span class="h-2 w-2 rounded-full bg-emerald-500"></span>
          Ambiente operacional
        </div>
      </header>

      <!-- Slot para o conteúdo da página -->
      <div class="flex-1 overflow-x-hidden p-4 md:p-6">
        <div class="mx-auto max-w-[1600px]">
          <slot />
        </div>
      </div>
    </main>
  </div>
</template>
