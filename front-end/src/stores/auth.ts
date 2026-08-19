import { defineStore } from 'pinia'
import { ref } from 'vue'
import { supabase } from '../services/supabase'
import api from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  interface AuthProfile {
    user_id?: string
    tenant_id?: string
    role?: string
    is_superadmin?: boolean
    plan?: string
    billing_cycle?: string
    payment_status?: string
  }
  // Estados
  const isSuperAdmin = ref(false)
  const role = ref('colaborador')
  const userId = ref('')
  const tenantId = ref('')
  const userName = ref('')
  const userEmail = ref('')
  const plan = ref('free')
  const billingCycle = ref('monthly')
  const paymentStatus = ref('ativo')
  const isInitialized = ref(false)
  const hasValidProfile = ref(false)
  let initializationPromise: Promise<boolean> | null = null

  // Ações
  const setSuperAdmin = (val: boolean) => {
    isSuperAdmin.value = val
  }

  const setRole = (val: string) => {
    role.value = val
  }

  const setProfile = (profile: AuthProfile) => {
    setSuperAdmin(profile?.is_superadmin === true)
    setRole(profile?.role || 'colaborador')
    userId.value = profile?.user_id || ''
    tenantId.value = profile?.tenant_id || ''
    plan.value = profile?.plan || 'free'
    billingCycle.value = profile?.billing_cycle || 'monthly'
    paymentStatus.value = profile?.payment_status || 'ativo'
    hasValidProfile.value = true
  }

  const setIdentity = (
    user?: {
      email?: string
      user_metadata?: { name?: string; full_name?: string }
    } | null,
  ) => {
    userEmail.value = user?.email || ''
    userName.value =
      user?.user_metadata?.name || user?.user_metadata?.full_name || userEmail.value || 'Usuário'
  }

  const clearSession = () => {
    setSuperAdmin(false)
    setRole('colaborador')
    userId.value = ''
    tenantId.value = ''
    userName.value = ''
    userEmail.value = ''
    plan.value = 'free'
    billingCycle.value = 'monthly'
    paymentStatus.value = 'ativo'
    hasValidProfile.value = false
  }

  const initializeAuthenticatedSession = (
    profile: AuthProfile,
    user?: {
      email?: string
      user_metadata?: { name?: string; full_name?: string }
    } | null,
  ) => {
    setIdentity(user)
    setProfile(profile)
    isInitialized.value = true
  }

  const checkSession = async (force = false) => {
    if (!force && isInitialized.value) {
      const { data } = await supabase.auth.getSession()
      if (!data.session) clearSession()
      return !!data.session && hasValidProfile.value
    }
    if (!force && initializationPromise) return initializationPromise

    initializationPromise = (async () => {
      const { data } = await supabase.auth.getSession()
      if (!data.session) {
        clearSession()
        isInitialized.value = true
        return false
      }
      setIdentity(data.session.user)
      try {
        const response = await api.get('/api/v1/auth/me')
        setProfile(response.data)
      } catch {
        clearSession()
        isInitialized.value = true
        return false
      }
      isInitialized.value = true
      return !!data.session
    })()

    try {
      return await initializationPromise
    } finally {
      initializationPromise = null
    }
  }

  const logout = async () => {
    await supabase.auth.signOut()
    clearSession()
    isInitialized.value = true
  }

  // O RETURN ABAIXO É OBRIGATÓRIO para o Vue saber que essas variáveis existem!
  return {
    isSuperAdmin,
    role,
    userId,
    tenantId,
    userName,
    userEmail,
    plan,
    billingCycle,
    paymentStatus,
    isInitialized,
    setSuperAdmin,
    setRole,
    setProfile,
    initializeAuthenticatedSession,
    checkSession,
    logout,
  }
})
