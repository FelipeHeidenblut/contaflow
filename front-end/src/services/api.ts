import axios from 'axios'
import { supabase } from '../services/supabase' // Ajuste o caminho se necessário (ex: ../services/supabase)

// Cria a instância base do Axios apontando para o FastAPI
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
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

// 🚨 2. INTERCEPTOR DE RESPOSTA (NOVO!)
// Fica de olho nas respostas do Backend
api.interceptors.response.use(
  (response) => {
    // Se a resposta for de sucesso (status 2xx), apenas retorna os dados normalmente
    return response
  },
  async (error) => {
    // Se der erro, entramos aqui
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
      console.warn('Sessão expirada ou acesso negado. Deslogando...')

      // 1. Desloga o usuário do Supabase localmente (limpa o cookie/localStorage)
      await supabase.auth.signOut()

      // 2. Redireciona para a tela de Login
      // Usamos window.location.href em vez do router.push para forçar um "hard reload",
      // limpando qualquer estado bugado do Pinia/Vue na memória.
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }

    // Repassa o erro para o bloco catch da função que fez a chamada original
    return Promise.reject(error)
  },
)

export default api
