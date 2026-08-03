<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { supabase } from '../services/supabase'
import { toast } from 'vue3-toastify'

const router = useRouter()
const novaSenha = ref('')
const confirmarSenha = ref('')
const isLoading = ref(false)

const handleUpdatePassword = async () => {
  if (novaSenha.value.length < 6) {
    toast.error('A senha deve ter no mínimo 6 caracteres.')
    return
  }

  if (novaSenha.value !== confirmarSenha.value) {
    toast.error('As senhas não coincidem.')
    return
  }

  isLoading.value = true

  try {
    const { error } = await supabase.auth.updateUser({ password: novaSenha.value })

    if (error) throw error

    await supabase.auth.signOut()

    toast.success('Senha atualizada com sucesso! Faça o login com a nova senha.')
    router.push('/login')
  } catch (error: any) {
    toast.error(error.message || 'Erro ao atualizar a senha. O link pode ter expirado.')
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex bg-[var(--ct-bg)] text-[var(--ct-ink)]">
    <!-- Lado Esquerdo -->
    <div
      class="relative hidden overflow-hidden md:flex md:w-1/2 flex-col justify-center items-center p-12 text-white bg-[var(--ct-navy)]"
    >
      <div
        class="absolute inset-0 bg-[linear-gradient(to_right,#ffffff08_1px,transparent_1px),linear-gradient(to_bottom,#ffffff08_1px,transparent_1px)] bg-[size:32px_32px] opacity-30"
      ></div>

      <div
        class="absolute top-1/4 left-1/4 h-72 w-72 rounded-full bg-[var(--ct-primary)]/20 blur-[120px]"
      ></div>

      <div
        class="absolute bottom-1/4 right-1/4 h-72 w-72 rounded-full bg-[#1E3A8A]/20 blur-[120px]"
      ></div>

      <div
        class="absolute inset-0"
        style="background: radial-gradient(120% 90% at 50% 30%, transparent 35%, rgba(15, 23, 42, .72) 100%)"
      ></div>

      <div class="relative z-10 text-center">
        <div class="mb-6 flex items-center justify-center gap-3">
          <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/10 backdrop-blur-sm">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="#93C5FD"
              stroke-width="2.4"
              class="h-6 w-6"
            >
              <path d="M9 11l3 3L22 4" />
              <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" />
            </svg>
          </div>

          <h1 class="text-5xl font-extrabold tracking-tight">
            Contably<span class="text-[#93C5FD]">Task</span>
          </h1>
        </div>

        <p class="mx-auto max-w-md text-lg leading-relaxed text-white/70">
          Crie uma nova senha segura para proteger o acesso à sua conta e aos dados do seu escritório.
        </p>
      </div>
    </div>

    <!-- Lado Direito -->
    <div class="w-full md:w-1/2 flex flex-col justify-center items-center p-8 bg-[var(--ct-bg)]">
      <div class="w-full max-w-md">
        <!-- Logo Mobile -->
        <div class="md:hidden text-center mb-8">
          <div class="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-[var(--ct-primary-soft)]">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="var(--ct-primary)"
              stroke-width="2.4"
              class="h-6 w-6"
            >
              <path d="M9 11l3 3L22 4" />
              <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" />
            </svg>
          </div>

          <h1 class="text-4xl font-extrabold tracking-tight text-[var(--ct-ink)]">
            Contably<span class="text-[var(--ct-primary)]">Task</span>
          </h1>
        </div>

        <div class="rounded-3xl border border-[var(--ct-border)] bg-white p-8 shadow-[0_20px_60px_rgba(15,23,42,0.08)]">
          <h2 class="mb-2 text-2xl font-extrabold tracking-tight text-[var(--ct-ink)]">
            Redefinir senha
          </h2>
          <p class="mb-8 text-[0.95rem] text-[var(--ct-text-muted)]">
            Escolha uma nova senha para acessar o sistema com segurança.
          </p>

          <form @submit.prevent="handleUpdatePassword" class="space-y-6">
            <div>
              <label class="mb-1.5 block text-sm font-medium text-[var(--ct-ink)]/80">
                Nova senha
              </label>
              <input
                v-model="novaSenha"
                type="password"
                required
                placeholder="Mínimo 6 caracteres"
                class="w-full rounded-2xl border border-[var(--ct-border)] bg-white px-4 py-3 text-sm text-[var(--ct-ink)] shadow-sm transition-all placeholder:text-slate-400 focus:border-[var(--ct-primary)] focus:outline-none focus:ring-4 focus:ring-[var(--ct-primary)]/10"
              />
            </div>

            <div>
              <label class="mb-1.5 block text-sm font-medium text-[var(--ct-ink)]/80">
                Confirmar nova senha
              </label>
              <input
                v-model="confirmarSenha"
                type="password"
                required
                placeholder="Repita a senha"
                class="w-full rounded-2xl border border-[var(--ct-border)] bg-white px-4 py-3 text-sm text-[var(--ct-ink)] shadow-sm transition-all placeholder:text-slate-400 focus:border-[var(--ct-primary)] focus:outline-none focus:ring-4 focus:ring-[var(--ct-primary)]/10"
              />
            </div>

            <div>
              <button
                type="submit"
                :disabled="isLoading"
                class="flex w-full justify-center rounded-2xl border border-transparent bg-[var(--ct-primary)] px-4 py-3 text-sm font-semibold text-white shadow-md shadow-[rgba(37,99,235,0.22)] transition-all hover:bg-[var(--ct-primary-hover)] focus:outline-none focus:ring-2 focus:ring-[var(--ct-primary)] focus:ring-offset-2 disabled:opacity-50"
              >
                {{ isLoading ? 'Salvando...' : 'Salvar nova senha' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
:global(:root) {
  --ct-bg: #F8FAFC;
  --ct-surface: #FFFFFF;
  --ct-muted: #F1F5F9;
  --ct-border: #E2E8F0;

  --ct-ink: #0F172A;
  --ct-text-muted: #64748B;

  --ct-primary: #2563EB;
  --ct-primary-hover: #1D4ED8;
  --ct-primary-soft: #DBEAFE;
  --ct-navy: #172554;
}
</style>