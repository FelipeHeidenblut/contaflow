import { createClient } from '@supabase/supabase-js'

// Busca as chaves que colocamos no arquivo .env
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true, // Salva a sessão no navegador (padrão é true, mas garante)
    autoRefreshToken: true, // Atualiza o token automaticamente antes de expirar
    detectSessionInUrl: true, // Necessário para o fluxo de "Esqueceu a senha" funcionar
  },
})

if (!supabaseUrl || !supabaseAnonKey) {
  console.error('Aviso: Chaves do Supabase não encontradas no arquivo .env')
}
