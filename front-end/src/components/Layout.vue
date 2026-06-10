<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { supabase } from '../services/supabase' // Ajuste o caminho se necessário

// Definição das Props (Substitui o antigo export default)
const props = defineProps<{
  title?: string
}>()

const route = useRoute()
const router = useRouter()

// Controle do Menu Mobile
const isMobileMenuOpen = ref(false)

// Controle do Dropdown do Avatar
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

// Fecha o menu automaticamente quando o usuário troca de rota
watch(route, () => {
  closeMobileMenu()
  closeDropdown()
})

// Função de Logout
const handleLogout = async () => {
  closeDropdown()
  closeMobileMenu()
  await supabase.auth.signOut()
  router.push('/login')
}

// Links de navegação
const navLinks = [
  { name: 'Dashboard', path: '/dashboard', icon: 'home' }, // Ajuste o path se for '/' no seu router
  { name: 'Clientes', path: '/clientes', icon: 'users' },
  { name: 'Obrigações', path: '/obrigacoes', icon: 'clock' },
  { name: 'Documentos', path: '/documentos', icon: 'folder' },
]
</script>

<template>
  <div class="h-screen flex overflow-hidden bg-[#f8f8f8]">
    <!-- ========================================== -->
    <!-- OVERLAY (Fundo Escuro Mobile) -->
    <!-- ========================================== -->
    <div
      v-if="isMobileMenuOpen"
      @click="closeMobileMenu"
      class="fixed inset-0 z-40 bg-black/50 transition-opacity md:hidden"
    ></div>

    <!-- ========================================== -->
    <!-- SIDEBAR MOBILE (Desliza da esquerda) -->
    <!-- ========================================== -->
    <aside
      :class="[isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full']"
      class="fixed inset-y-0 left-0 z-50 w-64 bg-[#19341a] text-white transition-transform duration-300 ease-in-out md:hidden shadow-2xl"
    >
      <div class="flex flex-col h-full">
        <!-- Logo Mobile -->
        <div class="flex items-center justify-between h-16 px-6 border-b border-white/10">
          <span class="text-xl font-extrabold tracking-tight">
            Contably<span class="text-[#ff8a65]">Task</span>
          </span>
          <button @click="closeMobileMenu" class="text-white/50 hover:text-white transition-colors">
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

        <!-- Links Mobile -->
        <nav class="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
          <RouterLink
            v-for="link in navLinks"
            :key="link.path"
            :to="link.path"
            custom
            v-slot="{ isActive, navigate }"
          >
            <button
              @click="navigate"
              class="w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200"
              :class="
                isActive
                  ? 'bg-[#ff8a65] text-white shadow-lg shadow-[#ff8a65]/30'
                  : 'text-white/70 hover:bg-white/10 hover:text-white'
              "
            >
              <svg
                v-if="link.icon === 'home'"
                class="w-5 h-5 flex-shrink-0"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
                ></path>
              </svg>
              <svg
                v-if="link.icon === 'users'"
                class="w-5 h-5 flex-shrink-0"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
                ></path>
              </svg>
              <svg
                v-if="link.icon === 'clock'"
                class="w-5 h-5 flex-shrink-0"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                ></path>
              </svg>
              <svg
                v-if="link.icon === 'folder'"
                class="w-5 h-5 flex-shrink-0"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
                ></path>
              </svg>
              <span class="font-semibold text-sm">{{ link.name }}</span>
            </button>
          </RouterLink>
        </nav>

        <!-- Sair Mobile -->
        <div class="px-4 py-4 border-t border-white/10">
          <button
            @click="handleLogout"
            class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-white/50 hover:text-red-400 hover:bg-white/5 transition-all duration-200"
          >
            <svg
              class="w-5 h-5 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
              ></path>
            </svg>
            <span class="font-semibold text-sm">Sair do Sistema</span>
          </button>
        </div>
      </div>
    </aside>

    <!-- ================= SIDEBAR DESKTOP ================= -->
    <aside class="hidden md:flex w-64 bg-[#19341a] text-white flex-col flex-shrink-0 shadow-2xl">
      <!-- Logo Desktop -->
      <div class="h-16 flex items-center px-6 border-b border-white/10">
        <span class="text-xl font-extrabold tracking-tight">
          Contably<span class="text-[#ff8a65]">Task</span>
        </span>
      </div>

      <!-- Links Desktop -->
      <nav class="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
        <RouterLink
          v-for="link in navLinks"
          :key="link.path"
          :to="link.path"
          custom
          v-slot="{ isActive, navigate }"
        >
          <button
            @click="navigate"
            class="w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200"
            :class="
              isActive
                ? 'bg-[#ff8a65] text-white shadow-lg shadow-[#ff8a65]/30'
                : 'text-white/70 hover:bg-white/10 hover:text-white'
            "
          >
            <svg
              v-if="link.icon === 'home'"
              class="w-5 h-5 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
              ></path>
            </svg>
            <svg
              v-if="link.icon === 'users'"
              class="w-5 h-5 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
              ></path>
            </svg>
            <svg
              v-if="link.icon === 'clock'"
              class="w-5 h-5 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              ></path>
            </svg>
            <svg
              v-if="link.icon === 'folder'"
              class="w-5 h-5 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
              ></path>
            </svg>
            <span class="font-semibold text-sm">{{ link.name }}</span>
          </button>
        </RouterLink>
      </nav>

      <!-- Sair Desktop -->
      <div class="px-4 py-6 border-t border-white/10">
        <button
          @click="handleLogout"
          class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-white/50 hover:text-red-400 hover:bg-white/5 transition-all duration-200"
        >
          <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
            ></path>
          </svg>
          <span class="font-semibold text-sm">Sair do Sistema</span>
        </button>
      </div>
    </aside>

    <!-- ========================================== -->
    <!-- ÁREA PRINCIPAL (Direita) -->
    <!-- ========================================== -->
    <div class="flex flex-col flex-1 overflow-y-auto">
      <!-- Topbar -->
      <header
        class="flex items-center justify-between h-16 px-6 bg-white border-b border-gray-200/80"
      >
        <!-- Esquerda: Botão Mobile + Título -->
        <div class="flex items-center gap-4">
          <button
            @click="toggleMobileMenu"
            class="md:hidden text-[#2a2a2a]/50 hover:text-[#19341a] focus:outline-none transition-colors"
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

          <h1 class="text-lg font-bold text-[#19341a]">
            <slot name="title">{{ props.title }}</slot>
          </h1>
        </div>

        <!-- Direita: Perfil e Dropdown -->
        <div class="relative flex items-center space-x-4">
          <!-- Sino de Notificação -->
          <button class="text-[#2a2a2a]/40 hover:text-[#19341a] hidden sm:block transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
              ></path>
            </svg>
          </button>

          <!-- Botão do Avatar -->
          <div class="relative">
            <button
              @click="toggleDropdown"
              class="flex items-center text-sm border-2 border-transparent rounded-full focus:outline-none focus:border-[#ff8a65] transition-colors"
            >
              <div
                class="w-8 h-8 rounded-full bg-[#eaf3ea] flex items-center justify-center text-[#19341a] font-bold text-sm cursor-pointer hover:bg-[#d4e8d4] transition-colors"
              >
                CF
              </div>
            </button>

            <!-- Overlay invisível para fechar ao clicar fora -->
            <div
              v-if="isDropdownOpen"
              @click="closeDropdown"
              class="fixed inset-0 h-full w-full z-10"
            ></div>

            <!-- Dropdown Menu -->
            <div
              v-if="isDropdownOpen"
              class="absolute right-0 mt-2 w-48 rounded-xl shadow-lg bg-white ring-1 ring-black/5 z-20 overflow-hidden"
            >
              <div class="py-1">
                <button
                  @click="handleLogout"
                  class="w-full text-left block px-4 py-2.5 text-sm text-[#2a2a2a]/70 hover:bg-red-50 hover:text-red-600 transition-colors font-medium"
                >
                  Sair do Sistema
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- Conteúdo da Página -->
      <main class="flex-1 p-4 md:p-8 overflow-y-auto bg-[#f8f8f8]">
        <slot></slot>
      </main>
    </div>
  </div>
</template>
