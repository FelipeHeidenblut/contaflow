import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import CadastroView from '../views/CadastroView.vue'
import DashboardView from '../views/DashboardView.vue'
import ClientsView from '@/views/ClientsView.vue'
import ObrigacoesView from '@/views/ObrigacoesView.vue'
import DocumentosView from '@/views/DocumentosView.vue'
import ForgotPasswordView from '../views/ForgotPasswordView.vue'
import ResetPasswordView from '../views/ResetPasswordView.vue'
import LandingView from '../views/LandingView.vue'
import PrivacidadeView from '../views/PrivacidadeView.vue'
import TermosView from '../views/TermosView.vue'

import { supabase } from '../services/supabase'

const routes = [
  // Rotas Públicas
  { path: '/', component: LandingView },
  { path: '/login', component: LoginView }, // ROTA ADICIONADA AQUI!
  { path: '/cadastro', component: CadastroView },
  { path: '/esqueceu-senha', component: ForgotPasswordView },
  { path: '/redefinir-senha', component: ResetPasswordView },
  { path: '/privacidade', component: PrivacidadeView },
  { path: '/termos', component: TermosView },

  // Rotas Privadas (Blindadas)
  {
    path: '/dashboard',
    component: DashboardView,
    meta: { requiresAuth: true },
  },
  {
    path: '/clientes',
    component: ClientsView,
    meta: { requiresAuth: true },
  },
  {
    path: '/obrigacoes',
    component: ObrigacoesView,
    meta: { requiresAuth: true },
  },
  {
    path: '/documentos',
    component: DocumentosView,
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// O Leão de Chácara (Route Guard)
router.beforeEach(async (to, from) => {
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (to.meta.requiresAuth && !session) {
    return '/login'
  }

  // BÔNUS: Se o usuário já estiver logado e tentar acessar o login, manda pro dashboard
  if ((to.path === '/login' || to.path === '/cadastro') && session) {
    return '/dashboard'
  }
})

export default router
