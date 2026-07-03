import { defineStore } from 'pinia'
import { ref } from 'vue'
import { supabase } from '../services/supabase'

export const useAuthStore = defineStore('auth', () => {
  const isSuperAdmin = ref(false)
  const session = ref<any>(null)

  const checkSession = async () => {
    const { data } = await supabase.auth.getSession()
    session.value = data.session
    return data.session
  }

  const setSuperAdmin = (status: boolean) => {
    isSuperAdmin.value = status
  }

  const logout = async () => {
    await supabase.auth.signOut()
    session.value = null
    isSuperAdmin.value = false
  }

  return { session, isSuperAdmin, checkSession, setSuperAdmin, logout }
})
