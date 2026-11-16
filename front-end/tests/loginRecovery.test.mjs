import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'
import { evaluate } from './componentHarness.mjs'
import * as recovery from '../src/services/sessionRecovery.ts'

const setup = () => {
  const session = { user: { id: 'user', email: 'test@example.invalid', user_metadata: {} } }
  const state = { session, signIns: 0, profiles: 0, navigations: [], error: null, options: [] }
  const supabase = {
    auth: {
      getSession: async () => ({ data: { session: state.session } }),
      signInWithPassword: async () => {
        state.signIns++
        return { data: { session: state.session } }
      },
      signOut: async () => {
        state.session = null
      },
    },
  }
  const api = {
    get: async (_path, options) => {
      state.options.push(options)
      if (state.error) throw state.error
      return { data: { user_id: 'user', tenant_id: 'office', role: 'admin' } }
    },
  }
  const vue = { ref: (value) => ({ value }), onMounted: () => {} }
  const dependencies = {
    vue,
    'vue-router': {
      useRoute: () => ({ query: {} }),
      useRouter: () => ({ push: async (to) => state.navigations.push(to) }),
    },
    '../services/supabase': { supabase },
    '../services/api': api,
    '../services/sessionRecovery': recovery,
    '../stores/auth': {
      useAuthStore: () => ({
        initializeAuthenticatedSession: () => {
          state.profiles++
        },
      }),
    },
    '@/constants/plans': { getPlan: () => null, isBillingCycle: () => false },
    '@/config/env': { appConfig: {} },
  }
  const source = readFileSync(new URL('../src/views/LoginView.vue', import.meta.url), 'utf8')
    .split('<script setup lang="ts">')[1]
    .split('</script>')[0]
  const login = evaluate(
    source,
    'handleLogin, captchaToken, senha, hasAuthenticatedSession, erroMensagem',
    dependencies,
  )
  login.captchaToken.value = 'test-captcha'
  login.senha.value = 'test-password'
  return { state, login, dependencies }
}

test('timeout preserves authentication and retries profile without repeating password login', async () => {
  const { state, login } = setup()
  state.error = { code: 'ECONNABORTED', message: 'timeout' }
  await login.handleLogin()
  assert.equal(state.signIns, 1)
  assert.equal(state.profiles, 0)
  assert.equal(state.navigations.length, 0)
  assert.equal(login.hasAuthenticatedSession.value, true)
  assert.equal(login.senha.value, '')
  assert.match(login.erroMensagem.value, /não é necessário informar sua senha/)
  assert.equal(state.options[0].timeout, 90_000)

  state.error = null
  await login.handleLogin()
  assert.equal(state.signIns, 1)
  assert.equal(state.profiles, 1)
  assert.equal(state.navigations[0], '/dashboard')
})

test('expired session during retry requires credentials and never opens dashboard', async () => {
  const { state, login } = setup()
  login.hasAuthenticatedSession.value = true
  state.session = null
  await login.handleLogin()
  assert.equal(login.hasAuthenticatedSession.value, false)
  assert.equal(state.options.length, 0)
  assert.equal(state.navigations.length, 0)
  assert.match(login.erroMensagem.value, /sessão expirou/)
})

test('fresh login still requires the security verification', async () => {
  const { state, login } = setup()
  login.captchaToken.value = ''
  await login.handleLogin()
  assert.equal(state.signIns, 0)
  assert.equal(state.navigations.length, 0)
})

test('route session validation can recover after temporary API failure', async () => {
  const { state, dependencies } = setup()
  const source = readFileSync(new URL('../src/stores/auth.ts', import.meta.url), 'utf8')
  const { useAuthStore } = evaluate(source, '', {
    ...dependencies,
    pinia: { defineStore: (_name, factory) => factory },
  })
  const store = useAuthStore()
  state.error = { code: 'ERR_NETWORK' }
  assert.equal(await store.checkSession(), false)
  assert.equal(store.isInitialized.value, false)
  state.error = null
  assert.equal(await store.checkSession(), true)
  assert.equal(store.tenantId.value, 'office')
  assert.equal(state.options.length, 2)
})
