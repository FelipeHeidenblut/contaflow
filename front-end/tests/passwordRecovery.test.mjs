import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'
import { evaluate } from './componentHarness.mjs'

const setup = (session = { user: { id: 'invited-user' } }) => {
  const state = { session, updates: [], navigations: [], messages: [], signedOut: false }
  let mount
  const source = readFileSync(
    new URL('../src/views/ResetPasswordView.vue', import.meta.url),
    'utf8',
  )
    .split('<script setup lang="ts">')[1]
    .split('</script>')[0]
  const form = evaluate(
    source,
    'handleUpdatePassword, novaSenha, confirmarSenha, hasSession, sessionError',
    {
      vue: {
        ref: (value) => ({ value }),
        onMounted: (callback) => {
          mount = callback
        },
      },
      'vue-router': { useRouter: () => ({ push: async (path) => state.navigations.push(path) }) },
      'vue3-toastify': {
        toast: {
          error: (message) => state.messages.push(message),
          success: () => {},
        },
      },
      '../services/supabase': {
        supabase: {
          auth: {
            getSession: async () => ({ data: { session: state.session } }),
            updateUser: async (values) => {
              state.updates.push(values)
              return {}
            },
            signOut: async () => {
              state.signedOut = true
              state.session = null
            },
          },
        },
      },
    },
  )
  form.novaSenha.value = 'new-test-password'
  form.confirmarSenha.value = 'new-test-password'
  return { state, form, mount: () => mount() }
}

test('invalid invite/recovery link cannot submit a password change', async () => {
  const { form, state, mount } = setup(null)
  await mount()
  await form.handleUpdatePassword()
  assert.equal(form.hasSession.value, false)
  assert.match(form.sessionError.value, /inválido ou expirou/)
  assert.equal(state.updates.length, 0)
})

test('valid invite can define a password, then requires a fresh login', async () => {
  const { form, state, mount } = setup()
  await mount()
  await form.handleUpdatePassword()
  assert.equal(state.updates.length, 1)
  assert.equal(state.signedOut, true)
  assert.equal(state.navigations[0], '/login')
})

test('session expiring while form is open cannot change password', async () => {
  const { form, state, mount } = setup()
  await mount()
  state.session = null
  await form.handleUpdatePassword()
  assert.equal(state.updates.length, 0)
  assert.match(form.sessionError.value, /sessão expirou/)
})

test('mismatched passwords never reach the provider', async () => {
  const { form, state, mount } = setup()
  await mount()
  form.confirmarSenha.value = 'different'
  await form.handleUpdatePassword()
  assert.equal(state.updates.length, 0)
  assert.match(state.messages[0], /não coincidem/)
})
