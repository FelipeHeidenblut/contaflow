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
    // 1. Atualiza a senha
    const { error } = await supabase.auth.updateUser({ password: novaSenha.value })

    if (error) throw error

    // 2. FORÇA O LOGOUT: Destrói a sessão temporária do link de recuperação
    await supabase.auth.signOut()

    // 3. Avisa e manda para o login
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
  <div class="min-h-screen flex">
    <!-- Lado Esquerdo (Escuro) -->
    <div
      class="hidden md:flex md:w-1/2 bg-slate-900 text-white flex-col justify-center items-center p-12 relative overflow-hidden"
    >
      <div class="absolute inset-0 opacity-10">
        <div
          class="absolute bottom-1/4 right-1/4 w-64 h-64 bg-indigo-500 rounded-full filter blur-3xl"
        ></div>
      </div>
      <div class="relative z-10 text-center">
        <h1 class="text-5xl font-black tracking-tight mb-4">
          Conta<span class="text-indigo-400">Flow</span>.
        </h1>
        <p class="text-slate-300 text-lg max-w-md mx-auto">
          Crie uma nova senha segura para sua conta.
        </p>
      </div>
    </div>

    <!-- Lado Direito (Formulário) -->
    <div class="w-full md:w-1/2 flex flex-col justify-center items-center p-8 bg-gray-50">
      <div class="w-full max-w-md">
        <div class="md:hidden text-center mb-8">
          <h1 class="text-4xl font-black tracking-tight text-gray-900">
            Conta<span class="text-indigo-600">Flow</span>.
          </h1>
        </div>

        <h2 class="text-2xl font-bold text-gray-900 mb-2">Redefinir Senha</h2>
        <p class="text-gray-500 mb-8">Escolha uma nova senha para acessar o sistema.</p>

        <form @submit.prevent="handleUpdatePassword" class="space-y-5">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nova Senha</label>
            <input
              v-model="novaSenha"
              type="password"
              required
              placeholder="Mínimo 6 caracteres"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Confirmar Nova Senha</label>
            <input
              v-model="confirmarSenha"
              type="password"
              required
              placeholder="Repita a senha"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
            />
          </div>

          <div>
            <button
              type="submit"
              :disabled="isLoading"
              class="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {{ isLoading ? 'Salvando...' : 'Salvar Nova Senha' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
