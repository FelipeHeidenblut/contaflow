<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { supabase } from '../services/supabase' // Ajuste o caminho se necessário

const route = useRoute()
const router = useRouter()

// Controle do Menu Mobile
const isMobileMenuOpen = ref(false)

// Controle do Dropdown do Avatar (NOVO)
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

// Fecha o menu automaticamente quando o usuário troca de rota (clica em um link)
watch(route, () => {
  closeMobileMenu()
})

// Para destacar o link ativo no menu
const currentPath = computed(() => route.path)

// Função de Logout
const handleLogout = async () => {
  closeDropdown() // Fecha o dropdown
  closeMobileMenu() // Fecha o menu mobile se estiver aberto
  await supabase.auth.signOut()
  router.push('/login')
}

// Links de navegação
const navLinks = [
  { name: 'Dashboard', path: '/dashboard', icon: 'home' },
  { name: 'Clientes', path: '/clientes', icon: 'users' },
  { name: 'Obrigações', path: '/obrigacoes', icon: 'clock' },
  { name: 'Documentos', path: '/documentos', icon: 'folder' },
]
</script>

<template>
  <div class="h-screen flex overflow-hidden bg-gray-50">
    <!-- ========================================== -->
    <!-- OVERLAY (Fundo Escuro Mobile) -->
    <!-- ========================================== -->
    <div
      v-if="isMobileMenuOpen"
      @click="closeMobileMenu"
      class="fixed inset-0 z-40 bg-black bg-opacity-50 transition-opacity md:hidden"
    ></div>

    <!-- ========================================== -->
    <!-- SIDEBAR MOBILE (Desliza da esquerda) -->
    <!-- ========================================== -->
    <aside
      :class="[isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full']"
      class="fixed inset-y-0 left-0 z-50 w-64 bg-slate-900 text-white transition-transform duration-300 ease-in-out md:hidden"
    >
      <!-- Conteúdo do Sidebar Mobile (Igual ao Desktop) -->
      <div class="flex flex-col h-full">
        <div class="flex items-center justify-between h-16 px-6 border-b border-slate-800">
          <span class="text-2xl font-bold tracking-tight"
            >Conta<span class="text-indigo-400">Flow</span>.</span
          >
          <button @click="closeMobileMenu" class="text-slate-400 hover:text-white">
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

        <nav class="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
          <RouterLink
            v-for="link in navLinks"
            :key="link.path"
            :to="link.path"
            class="flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors"
            :class="
              currentPath === link.path
                ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/30'
                : 'text-slate-300 hover:bg-slate-800 hover:text-white'
            "
          >
            <svg
              v-if="link.icon === 'home'"
              class="w-5 h-5 mr-3"
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
              class="w-5 h-5 mr-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
              ></path>
            </svg>
            <svg
              v-if="link.icon === 'clock'"
              class="w-5 h-5 mr-3"
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
              class="w-5 h-5 mr-3"
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
            {{ link.name }}
          </RouterLink>
        </nav>

        <div class="px-4 py-4 border-t border-slate-800">
          <button
            @click="handleLogout"
            class="flex items-center w-full px-4 py-2.5 text-sm font-medium text-slate-300 rounded-lg hover:bg-red-600 hover:text-white transition-colors"
          >
            <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
              ></path>
            </svg>
            Sair do Sistema
          </button>
        </div>
      </div>
    </aside>

    <!-- ========================================== -->
    <!-- SIDEBAR DESKTOP (Fixo) -->
    <!-- ========================================== -->
    <aside class="hidden md:flex md:flex-shrink-0">
      <div class="flex flex-col w-64 bg-slate-900 text-white">
        <div class="flex items-center h-16 px-6 border-b border-slate-800">
          <span class="text-2xl font-bold tracking-tight"
            >Conta<span class="text-indigo-400">Flow</span>.</span
          >
        </div>
        <nav class="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
          <RouterLink
            v-for="link in navLinks"
            :key="link.path"
            :to="link.path"
            class="flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors"
            :class="
              currentPath === link.path
                ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/30'
                : 'text-slate-300 hover:bg-slate-800 hover:text-white'
            "
          >
            <svg
              v-if="link.icon === 'home'"
              class="w-5 h-5 mr-3"
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
              class="w-5 h-5 mr-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
              ></path>
            </svg>
            <svg
              v-if="link.icon === 'clock'"
              class="w-5 h-5 mr-3"
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
              class="w-5 h-5 mr-3"
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
            {{ link.name }}
          </RouterLink>
        </nav>
        <div class="px-4 py-4 border-t border-slate-800">
          <button
            @click="handleLogout"
            class="flex items-center w-full px-4 py-2.5 text-sm font-medium text-slate-300 rounded-lg hover:bg-red-600 hover:text-white transition-colors"
          >
            <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
              ></path>
            </svg>
            Sair do Sistema
          </button>
        </div>
      </div>
    </aside>

    <!-- ========================================== -->
    <!-- ÁREA PRINCIPAL (Direita) -->
    <!-- ========================================== -->
    <div class="flex flex-col flex-1 overflow-y-auto">
      <!-- Topbar -->
      <header class="flex items-center justify-between h-16 px-6 bg-white border-b border-gray-200">
        <!-- Esquerda: Botão Mobile + Título -->
        <div class="flex items-center gap-4">
          <!-- BOTÃO HAMBÚRGUER (Visível só no Mobile) -->
          <button
            @click="toggleMobileMenu"
            class="md:hidden text-gray-500 hover:text-gray-700 focus:outline-none"
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

          <h1 class="text-lg font-semibold text-gray-800">
            <slot name="title">{{ $props.title }}</slot>
          </h1>
        </div>

        <!-- Direita: Perfil e Dropdown -->
        <div class="relative flex items-center space-x-4">
          <button class="text-gray-400 hover:text-gray-600 hidden sm:block">
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
              class="flex items-center text-sm border-2 border-transparent rounded-full focus:outline-none focus:border-indigo-300 transition-colors"
            >
              <div
                class="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-bold text-sm cursor-pointer hover:bg-indigo-200"
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
              class="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-20 overflow-hidden"
            >
              <div class="py-1">
                <!-- No futuro, podemos colocar "Meu Perfil" aqui -->
                <!-- <a href="#" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Meu Perfil</a> -->

                <button
                  @click="handleLogout"
                  class="w-full text-left block px-4 py-2 text-sm text-gray-700 hover:bg-red-50 hover:text-red-600 transition-colors font-medium"
                >
                  Sair do Sistema
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- Conteúdo da Página -->
      <main class="flex-1 p-4 md:p-6 overflow-y-auto bg-gray-50">
        <slot></slot>
      </main>
    </div>
  </div>
</template>

<script lang="ts">
export default {
  props: {
    title: String,
  },
}
</script>
