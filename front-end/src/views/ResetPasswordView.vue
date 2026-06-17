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
      class="hidden md:flex md:w-1/2 bg-[#19341a] text-white flex-col justify-center items-center p-12 relative overflow-hidden"
    >
      <!-- Efeito de luz moderna -->
      <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-[#ff8a65]/20 rounded-full filter blur-[120px]"></div>

      <div class="relative z-10 text-center">
        <h1 class="text-5xl font-extrabold tracking-tight mb-4">
          Contably<span class="text-[#ff8a65]">Task</span>.
        </h1>
        <p class="text-white/60 text-lg max-w-md mx-auto leading-relaxed">
          Crie uma nova senha segura para sua conta e proteja os dados dos seus clientes.
        </p>
      </div>
    </div>

    <!-- Lado Direito (Formulário) -->
    <div class="w-full md:w-1/2 flex flex-col justify-center items-center p-8 bg-[#f8f8f8]">
      <div class="w-full max-w-md">
        <!-- Logo para Mobile -->
        <div class="md:hidden text-center mb-8">
          <h1 class="text-4xl font-extrabold tracking-tight text-[#19341a]">
            Contably<span class="text-[#ff8a65]">Task</span>.
          </h1>
        </div>

        <h2 class="text-2xl font-extrabold text-[#19341a] mb-2 tracking-tight">Redefinir Senha</h2>
        <p class="text-gray-500 mb-8 text-[0.95rem]">
          Escolha uma nova senha para acessar o sistema.
        </p>

        <form @submit.prevent="handleUpdatePassword" class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-[#2a2a2a]/70 mb-1.5">Nova Senha</label>
            <input
              v-model="novaSenha"
              type="password"
              required
              placeholder="Mínimo 6 caracteres"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-[#ff8a65] focus:border-transparent text-sm transition-all"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-[#2a2a2a]/70 mb-1.5">Confirmar Nova Senha</label>
            <input
              v-model="confirmarSenha"
              type="password"
              required
              placeholder="Repita a senha"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-[#ff8a65] focus:border-transparent text-sm transition-all"
            />
          </div>

          <div>
            <button
              type="submit"
              :disabled="isLoading"
              class="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-md shadow-[#ff8a65]/30 text-sm font-semibold text-white bg-[#ff8a65] hover:bg-[#f07047] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#ff8a65] disabled:opacity-50 transition-all"
            >
              {{ isLoading ? 'Salvando...' : 'Salvar Nova Senha' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>