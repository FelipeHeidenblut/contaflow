<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, RouterLink, useRoute } from 'vue-router'
import { supabase } from '../services/supabase'

defineProps<{
  title?: string
}>()

const router = useRouter()
const route = useRoute()
const isSidebarOpen = ref(false)

const handleLogout = async () => {
  await supabase.auth.signOut()
  router.push('/login')
}

// Menu exclusivo do Super Admin
const adminMenu = [
  {
    name: 'Dashboard Global',
    path: '/admin',
    icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
  },
  {
    name: 'Escritórios (Tenants)',
    path: '/admin/escritorios',
    icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
  },
  {
    name: 'Faturamento Asaas',
    path: '/admin/financeiro',
    icon: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
  },
]
</script>

<template>
  <div class="min-h-screen bg-[#f4f7f6] flex">
    <!-- Sidebar Super Admin (Estilo Escuro/Diferenciado para "God Mode") -->
    <aside
      class="w-64 bg-[#0a192f] text-white flex-col fixed h-full z-20 transition-transform duration-300 md:flex"
      :class="isSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'"
    >
      <div class="p-6 flex items-center justify-between border-b border-white/10">
        <div>
          <h2 class="text-2xl font-extrabold tracking-tight">
            ContaFlow<span class="text-[#ff8a65]">Admin</span>
          </h2>
          <span
            class="text-xs font-medium bg-red-500/20 text-red-400 px-2 py-0.5 rounded-full mt-1 inline-block border border-red-500/30"
          >
            Super Acesso
          </span>
        </div>
        <button @click="isSidebarOpen = false" class="md:hidden text-gray-400 hover:text-white">
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
              ? 'bg-[#ff8a65] text-white shadow-md'
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

      <div class="p-4 border-t border-white/10">
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
          <button @click="isSidebarOpen = true" class="md:hidden text-gray-500 hover:text-gray-700">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16"
              ></path>
            </svg>
          </button>
          <h1 v-if="title" class="text-xl font-bold text-[#19341a]">{{ title }}</h1>
        </div>
      </header>

      <!-- Slot para o conteúdo da página -->
      <div class="p-6 md:p-8 flex-1 overflow-x-hidden">
        <div class="max-w-7xl mx-auto">
          <slot />
        </div>
      </div>
    </main>
  </div>
</template>
