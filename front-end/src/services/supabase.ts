import { createClient } from '@supabase/supabase-js'
import { appConfig } from '@/config/env'

export const supabase = createClient(appConfig.supabaseUrl, appConfig.supabaseAnonKey, {
  auth: {
    persistSession: true, // Salva a sessão no navegador (padrão é true, mas garante)
    autoRefreshToken: true, // Atualiza o token automaticamente antes de expirar
    detectSessionInUrl: true, // Necessário para o fluxo de "Esqueceu a senha" funcionar
  },
})
