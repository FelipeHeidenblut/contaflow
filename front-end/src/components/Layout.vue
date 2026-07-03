<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { supabase } from '../services/supabase'

// Definição das Props
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
  { name: 'Dashboard', path: '/dashboard', icon: 'home' },
  { name: 'Clientes', path: '/clientes', icon: 'users' },
  { name: 'Obrigações', path: '/obrigacoes', icon: 'clock' },
  { name: 'Calendário', path: '/calendario', icon: 'calendar' },
  { name: 'Documentos', path: '/documentos', icon: 'folder' },
  { name: 'Membros', path: '/membros', icon: 'team' },
  { name: 'Planos', path: '/faturamento', icon: 'card' },
]

// ==========================================
// DADOS DO USUÁRIO LOGADO (Dinâmico)
// ==========================================
const loggedUser = ref({
  name: 'Carregando...',
  email: '',
  initials: '...',
})

// Função auxiliar para gerar as iniciais
const gerarIniciais = (nome: string): string => {
  if (!nome) return '?'
  const partes = nome
    .trim()
    .split(' ')
    .filter((p) => p)
  if (partes.length === 0) return '?'
  if (partes.length === 1) return (partes[0]?.charAt(0) || '?').toUpperCase()
  const primeiraLetra = partes[0]?.charAt(0) || ''
  const ultimaLetra = partes[partes.length - 1]?.charAt(0) || ''
  return (primeiraLetra + ultimaLetra).toUpperCase() || '?'
}

// Busca os dados reais do Supabase
onMounted(async () => {
  const { data } = await supabase.auth.getUser()
  if (data?.user) {
    const nomeReal = data.user.user_metadata?.name || data.user.email || 'Usuário'
    loggedUser.value = {
      name: nomeReal,
      email: data.user.email || '',
      initials: gerarIniciais(nomeReal),
    }
  }
})
</script>

<template>
  <div class="h-screen flex overflow-hidden bg-[#f8f8f8]">
    <!-- OVERLAY (Fundo Escuro Mobile) -->
    <div
      v-if="isMobileMenuOpen"
      @click="closeMobileMenu"
      class="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm transition-opacity md:hidden"
    ></div>

    <!-- SIDEBAR MOBILE -->
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
        <nav class="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
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
                  ? 'bg-[#ff8a65] text-white shadow-lg shadow-[#ff8a65]/20'
                  : 'text-white/60 hover:bg-white/5 hover:text-white'
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
                v-if="link.icon === 'calendar'"
                class="w-5 h-5 flex-shrink-0"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
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
              <svg
                v-if="link.icon === 'team'"
                class="w-5 h-5 flex-shrink-0"
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

              <!-- ÍCONE DE CARTÃO CORRIGIDO AQUI -->
              <svg
                v-if="link.icon === 'card'"
                class="w-5 h-5 flex-shrink-0"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
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

    <!-- SIDEBAR DESKTOP -->
    <aside class="hidden md:flex w-64 bg-[#19341a] text-white flex-col flex-shrink-0 shadow-xl">
      <!-- Logo Desktop -->
      <div class="h-16 flex items-center px-6 border-b border-white/10">
        <span class="text-xl font-extrabold tracking-tight">
          Contably<span class="text-[#ff8a65]">Task</span>
        </span>
      </div>

      <!-- Links Desktop -->
      <nav class="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
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
                ? 'bg-[#ff8a65] text-white shadow-lg shadow-[#ff8a65]/20'
                : 'text-white/60 hover:bg-white/5 hover:text-white'
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
              v-if="link.icon === 'calendar'"
              class="w-5 h-5 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
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
            <svg
              v-if="link.icon === 'team'"
              class="w-5 h-5 flex-shrink-0"
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

            <!-- ÍCONE DE CARTÃO CORRIGIDO AQUI -->
            <svg
              v-if="link.icon === 'card'"
              class="w-5 h-5 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
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

    <!-- ÁREA PRINCIPAL (Direita) -->
    <div class="flex flex-col flex-1 overflow-y-auto">
      <!-- Topbar -->
      <header
        class="flex items-center justify-between h-16 px-6 bg-white/80 backdrop-blur-md border-b border-gray-200/80 z-10"
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
          <h1 class="text-lg font-bold text-[#19341a] tracking-tight">
            <slot name="title">{{ props.title }}</slot>
          </h1>
        </div>

        <!-- Direita: Perfil e Dropdown -->
        <div class="relative flex items-center space-x-5">
          <!-- Sino de Notificação -->
          <button
            class="text-[#2a2a2a]/40 hover:text-[#19341a] hidden sm:block transition-colors relative"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
              ></path>
            </svg>
            <span class="absolute top-0 right-0 w-2 h-2 bg-[#ff8a65] rounded-full"></span>
          </button>

          <!-- Botão do Avatar e Nome -->
          <div class="relative">
            <button
              @click="toggleDropdown"
              class="flex items-center gap-3 text-sm border-2 border-transparent rounded-full focus:outline-none focus:border-[#ff8a65] transition-colors"
            >
              <div class="hidden md:block text-right">
                <p class="font-bold text-[#19341a] text-[0.85rem] leading-tight">
                  {{ loggedUser.name }}
                </p>
                <p class="text-[0.75rem] text-gray-400 leading-tight">{{ loggedUser.email }}</p>
              </div>
              <div
                class="w-9 h-9 rounded-full bg-[#19341a] text-white flex items-center justify-center font-bold text-sm cursor-pointer shadow-sm"
              >
                {{ loggedUser.initials }}
              </div>
            </button>

            <!-- Overlay invisível para fechar ao clicar fora -->
            <div
              v-if="isDropdownOpen"
              @click="closeDropdown"
              class="fixed inset-0 h-full w-full z-10 cursor-default"
            ></div>

            <!-- Dropdown Menu -->
            <div
              v-if="isDropdownOpen"
              class="absolute right-0 mt-2 w-56 rounded-xl shadow-xl bg-white ring-1 ring-black/5 z-20 overflow-hidden"
            >
              <div class="px-4 py-3 border-b border-gray-100">
                <p class="text-sm font-bold text-[#19341a]">{{ loggedUser.name }}</p>
                <p class="text-xs text-gray-400 truncate">{{ loggedUser.email }}</p>
              </div>
              <div class="py-1">
                <button
                  @click="handleLogout"
                  class="w-full text-left flex items-center gap-2 px-4 py-2.5 text-sm text-red-500 hover:bg-red-50 transition-colors font-semibold"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
