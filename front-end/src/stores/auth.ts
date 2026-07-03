import { defineStore } from 'pinia'
import { ref } from 'vue'
import { supabase } from '../services/supabase'

export const useAuthStore = defineStore('auth', () => {
  // Estados
  const isSuperAdmin = ref(localStorage.getItem('is_superadmin') === 'true')
  const role = ref(localStorage.getItem('user_role') || 'colaborador')

  // Ações
  const setSuperAdmin = (val: boolean) => {
    isSuperAdmin.value = val
    localStorage.setItem('is_superadmin', val ? 'true' : 'false')
  }

  const setRole = (val: string) => {
    role.value = val
    localStorage.setItem('user_role', val)
  }

  const checkSession = async () => {
    const { data } = await supabase.auth.getSession()
    if (!data.session) {
      setSuperAdmin(false)
      setRole('colaborador')
    }
    return !!data.session
  }

  const logout = async () => {
    await supabase.auth.signOut()
    setSuperAdmin(false)
    setRole('colaborador')
  }

  // O RETURN ABAIXO É OBRIGATÓRIO para o Vue saber que essas variáveis existem!
  return {
    isSuperAdmin,
    role,
    setSuperAdmin,
    setRole,
    checkSession,
    logout,
  }
})
