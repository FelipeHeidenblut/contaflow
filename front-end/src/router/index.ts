import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// As rotas privadas serão carregadas via Lazy Loading abaixo para otimizar performance.

const routes = [
  // ==========================================
  // ROTAS PÚBLICAS
  // ==========================================
  { path: '/', component: () => import('@/views/LandingView.vue') },
  { path: '/login', component: () => import('@/views/LoginView.vue'), meta: { guestOnly: true } },
  { path: '/cadastro', component: () => import('@/views/CadastroView.vue'), meta: { guestOnly: true } },
  { path: '/esqueceu-senha', component: () => import('@/views/ForgotPasswordView.vue'), meta: { guestOnly: true } },
  { path: '/redefinir-senha', component: () => import('@/views/ResetPasswordView.vue'), meta: { guestOnly: true } },
  { path: '/privacidade', component: () => import('@/views/PrivacidadeView.vue') },
  { path: '/termos', component: () => import('@/views/TermosView.vue') },

  // ==========================================
  // ROTAS PRIVADAS (Painel do Cliente SaaS)
  // ==========================================
  {
    path: '/dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/clientes',
    component: () => import('@/views/ClientsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/obrigacoes',
    component: () => import('@/views/ObrigacoesView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/documentos',
    component: () => import('@/views/DocumentosView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/membros',
    component: () => import('@/views/MembrosView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/calendario',
    component: () => import('@/views/CalendarioView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/faturamento',
    component: () => import('@/views/FaturamentoView.vue'),
    meta: { requiresAuth: true },
  },

  // ==========================================
  // ROTAS DO BACKOFFICE (SaaS Admin)
  // ==========================================
  {
    path: '/ops-login',
    component: () => import('@/views/AdminLoginView.vue'),
    meta: { guestOnly: true },
  },
  {
    path: '/admin',
    component: () => import('@/views/AdminDashboardView.vue'),
    meta: { requiresAuth: true, requiresSuperAdmin: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// ==========================================
// GUARDIÃO DE ROTAS (Shift-Left Security)
// ==========================================
router.beforeEach(async (to) => {
  // Instanciamos a store AQUI DENTRO para evitar erros de ciclo de vida do Vue/Pinia
  const authStore = useAuthStore()

  // Sincroniza o estado local com a sessão real do Supabase
  const activeSession = await authStore.checkSession()

  const requiresAuth = to.meta.requiresAuth
  const requiresSuperAdmin = to.meta.requiresSuperAdmin
  const guestOnly = to.meta.guestOnly

  // 1. Regra de Proteção Padrão: Tentar acessar área logada sem estar logado
  if (requiresAuth && !activeSession) {
    return '/login'
  }

  // 2. Regra RBAC (Role-Based Access Control): Cliente tentando acessar o painel Admin
  if (requiresSuperAdmin && !authStore.isSuperAdmin) {
    return '/dashboard'
  }

  // 3. Regra de UX: Usuário logado tentando acessar telas de Login/Cadastro
  if (guestOnly && activeSession) {
    // Se for o dono do SaaS, manda pro backoffice. Se for contador, manda pro app.
    return authStore.isSuperAdmin ? '/admin' : '/dashboard'
  }

  // Se passou por todas as barreiras, caminho livre! (return true ou apenas return vazio)
  return true
})

export default router
