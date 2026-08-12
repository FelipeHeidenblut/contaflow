<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue3-toastify'
import { supabase } from '../services/supabase'
import AuthShell from '@/components/AuthShell.vue'
const router = useRouter()
const novaSenha = ref('')
const confirmarSenha = ref('')
const isLoading = ref(false)
const handleUpdatePassword = async () => {
  if (novaSenha.value.length < 8) {
    toast.error('A senha deve ter no mínimo 8 caracteres.')
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
    toast.success('Senha atualizada! Entre com a nova senha.')
    router.push('/login')
  } catch (error: unknown) {
    toast.error(
      error instanceof Error
        ? error.message
        : 'Erro ao atualizar a senha. O link pode ter expirado.',
    )
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <AuthShell
    title="Defina uma nova senha"
    description="Escolha uma senha exclusiva com pelo menos oito caracteres."
    ><form class="space-y-5" @submit.prevent="handleUpdatePassword">
      <div>
        <label for="new-password" class="ct-label">Nova senha</label
        ><input
          id="new-password"
          v-model="novaSenha"
          class="ct-field"
          type="password"
          required
          minlength="8"
          maxlength="72"
          autocomplete="new-password"
        />
      </div>
      <div>
        <label for="confirm-password" class="ct-label">Confirmar senha</label
        ><input
          id="confirm-password"
          v-model="confirmarSenha"
          class="ct-field"
          type="password"
          required
          minlength="8"
          maxlength="72"
          autocomplete="new-password"
        />
      </div>
      <button
        type="submit"
        :disabled="isLoading"
        class="ct-button-primary w-full disabled:opacity-50"
      >
        {{ isLoading ? 'Salvando…' : 'Salvar nova senha' }}
      </button>
    </form></AuthShell
  >
</template>
