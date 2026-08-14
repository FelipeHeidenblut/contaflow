import { createRouter, createWebHistory } from 'vue-router'

// As rotas privadas serão carregadas via Lazy Loading abaixo para otimizar performance.

const routes = [
  // ==========================================
  // ROTAS PÚBLICAS
  // ==========================================
  {
    path: '/',
    component: () => import('@/views/LandingView.vue'),
    meta: { title: 'Gestão contábil' },
  },
  {
    path: '/login',
    component: () => import('@/views/LoginView.vue'),
    meta: { guestOnly: true, authenticatedRedirect: '/dashboard', title: 'Entrar' },
  },
  {
    path: '/cadastro',
    component: () => import('@/views/CadastroView.vue'),
    meta: { guestOnly: true, title: 'Criar conta' },
  },
  {
    path: '/esqueceu-senha',
    component: () => import('@/views/ForgotPasswordView.vue'),
    meta: { guestOnly: true, title: 'Recuperar senha' },
  },
  {
    path: '/redefinir-senha',
    component: () => import('@/views/ResetPasswordView.vue'),
    meta: { guestOnly: true, title: 'Redefinir senha' },
  },
  {
    path: '/privacidade',
    component: () => import('@/views/PrivacidadeView.vue'),
    meta: { title: 'Privacidade' },
  },
  {
    path: '/termos',
    component: () => import('@/views/TermosView.vue'),
    meta: { title: 'Termos de uso' },
  },
  {
    path: '/sobre',
    component: () => import('@/views/SobreNosView.vue'),
    meta: { title: 'Sobre nós' },
  },
  {
    path: '/contato',
    component: () => import('@/views/ContatoView.vue'),
    meta: { title: 'Contato' },
  },
  { path: '/planos', component: () => import('@/views/PlanosView.vue'), meta: { title: 'Planos' } },
  {
    path: '/como-funciona',
    component: () => import('@/views/ComoFuncionaView.vue'),
    meta: { title: 'Como funciona' },
  },

  // ==========================================
  // ROTAS PRIVADAS (Painel do Cliente SaaS)
  // ==========================================
  {
    path: '/dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true, title: 'Dashboard' },
  },
  {
    path: '/clientes',
    component: () => import('@/views/ClientsView.vue'),
    meta: { requiresAuth: true, title: 'Clientes' },
  },
  {
    path: '/obrigacoes',
    component: () => import('@/views/ObrigacoesView.vue'),
    meta: { requiresAuth: true, title: 'Obrigações' },
  },
  {
    path: '/documentos',
    component: () => import('@/views/DocumentosView.vue'),
    meta: { requiresAuth: true, title: 'Documentos' },
  },
  {
    path: '/membros',
    component: () => import('@/views/MembrosView.vue'),
    meta: { requiresAuth: true, allowedRoles: ['admin', 'gerente'], title: 'Membros' },
  },
  {
    path: '/calendario',
    component: () => import('@/views/CalendarioView.vue'),
    meta: { requiresAuth: true, title: 'Calendário' },
  },
  {
    path: '/relatorios',
    component: () => import('@/views/RelatoriosView.vue'),
    meta: { requiresAuth: true, title: 'Relatórios' },
  },
  {
    path: '/faturamento',
    component: () => import('@/views/FaturamentoView.vue'),
    meta: { requiresAuth: true, allowedRoles: ['admin'], title: 'Planos e faturamento' },
  },

  // ==========================================
  // ROTAS DO BACKOFFICE (SaaS Admin)
  // ==========================================
  {
    path: '/ops-login',
    component: () => import('@/views/AdminLoginView.vue'),
    meta: { guestOnly: true, authenticatedRedirect: '/admin', title: 'Acesso ao backoffice' },
  },
  {
    path: '/admin',
    component: () => import('@/views/AdminDashboardView.vue'),
    meta: { requiresAuth: true, requiresSuperAdmin: true, title: 'Backoffice' },
  },
  {
    path: '/:pathMatch(.*)*',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { title: 'Página não encontrada' },
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
  const requiresAuth = to.meta.requiresAuth
  const requiresSuperAdmin = to.meta.requiresSuperAdmin
  const guestOnly = to.meta.guestOnly

  // Páginas institucionais não precisam baixar nem inicializar o cliente de autenticação.
  if (!requiresAuth && !requiresSuperAdmin && !guestOnly) return true

  // A store e o Supabase só entram no bundle quando a rota depende de uma sessão.
  const { useAuthStore } = await import('../stores/auth')
  const authStore = useAuthStore()
  const activeSession = await authStore.checkSession()

  // 1. Regra de Proteção Padrão: Tentar acessar área logada sem estar logado
  if (requiresAuth && !activeSession) {
    return '/login'
  }

  // 2. Regra RBAC (Role-Based Access Control): Cliente tentando acessar o painel Admin
  if (requiresSuperAdmin && !authStore.isSuperAdmin) {
    return '/dashboard'
  }

  const allowedRoles = Array.isArray(to.meta.allowedRoles) ? to.meta.allowedRoles : null
  if (requiresAuth && allowedRoles && !allowedRoles.includes(authStore.role)) {
    return '/dashboard'
  }

  // 3. Regra de UX: Usuário logado tentando acessar telas de Login/Cadastro
  if (guestOnly && activeSession) {
    // Os dois logins são fluxos distintos: o login comum nunca abre o backoffice.
    if (to.meta.authenticatedRedirect === '/admin') {
      return authStore.isSuperAdmin ? '/admin' : '/dashboard'
    }
    const requestedPlan =
      typeof to.query.plano === 'string' &&
      ['basico', 'profissional', 'business'].includes(to.query.plano)
        ? to.query.plano
        : null
    if (requestedPlan) return { path: '/faturamento', query: { plano: requestedPlan } }
    return '/dashboard'
  }

  // Se passou por todas as barreiras, caminho livre! (return true ou apenas return vazio)
  return true
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${String(to.meta.title)} · ContablyTask` : 'ContablyTask'
})

export default router
