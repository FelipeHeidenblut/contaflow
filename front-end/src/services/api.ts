import axios from 'axios'
import { supabase } from '../services/supabase' // Ajuste o caminho se necessário (ex: ../services/supabase)
import { appConfig } from '@/config/env'

// Cria a instância base do Axios apontando para o FastAPI
const api = axios.create({
  baseURL: appConfig.apiBaseUrl,
  timeout: 10000,
})

// 🛡️ 1. INTERCEPTOR DE REQUISIÇÃO (O que já tínhamos)
// Injeta o token do Supabao antes de enviar qualquer pedido
api.interceptors.request.use(
  async (config) => {
    try {
      const {
        data: { session },
      } = await supabase.auth.getSession()

      if (session?.access_token) {
        config.headers.Authorization = `Bearer ${session.access_token}`
      }
    } catch (error) {
      console.error('Erro ao buscar token do Supabase:', error)
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// 🚨 2. INTERCEPTOR DE RESPOSTA (CORRIGIDO)
// Fica de olho nas respostas do Backend
api.interceptors.response.use(
  (response) => {
    // Se a resposta for de sucesso (status 2xx), apenas retorna os dados normalmente
    return response
  },
  async (error) => {
    // Só desloga se for 401 (Token expirado/inválido)
    if (error.response && error.response.status === 401) {
      console.warn('Sessão expirada. Deslogando...')

      // 1. Desloga o usuário do Supabase localmente
      await supabase.auth.signOut()

      // 2. Redireciona para a tela de Login
      const loginPath =
        window.location.pathname.startsWith('/admin') || window.location.pathname === '/ops-login'
          ? '/ops-login'
          : '/login'
      if (window.location.pathname !== loginPath) {
        window.location.href = loginPath
      }
    }

    // Se for 403 (Acesso negado / Limite de plano), NÃO desloga!
    // Apenas repassa o erro para o bloco 'catch' da função original,
    // para que o Toast vermelho apareça na tela com a mensagem do backend.
    return Promise.reject(error)
  },
)

export default api
