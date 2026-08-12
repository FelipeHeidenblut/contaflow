<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { toast } from 'vue3-toastify'
import VueTurnstile from 'vue-turnstile'
import { supabase } from '../services/supabase'
import AuthShell from '@/components/AuthShell.vue'

const email = ref('')
const isLoading = ref(false)
const emailEnviado = ref(false)
const captchaToken = ref('')
const turnstileSiteKey = import.meta.env.VITE_TURNSTILE_SITE_KEY || ''
const handleResetPassword = async () => {
  if (!captchaToken.value) {
    toast.error('Conclua a verificação de segurança.')
    return
  }
  isLoading.value = true
  try {
    const { error } = await supabase.auth.resetPasswordForEmail(email.value, {
      redirectTo: `${window.location.origin}/redefinir-senha`,
      captchaToken: captchaToken.value,
    })
    if (error) throw error
    emailEnviado.value = true
    toast.success('Link de recuperação enviado!')
  } catch (error: unknown) {
    toast.error(error instanceof Error ? error.message : 'Erro ao enviar o e-mail.')
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <AuthShell
    title="Recupere seu acesso"
    description="Enviaremos um link seguro para o e-mail cadastrado."
  >
    <div
      v-if="emailEnviado"
      class="border-l-2 border-emerald-500 bg-emerald-50 px-4 py-4 text-sm leading-6 text-emerald-800"
    >
      <strong>E-mail enviado.</strong> Verifique sua caixa de entrada e a pasta de spam.<RouterLink
        to="/login"
        class="mt-4 block font-semibold text-[var(--ct-primary)]"
        >Voltar para o login</RouterLink
      >
    </div>
    <form v-else class="space-y-5" @submit.prevent="handleResetPassword">
      <div>
        <label for="forgot-email" class="ct-label">E-mail cadastrado</label
        ><input
          id="forgot-email"
          v-model="email"
          class="ct-field"
          required
          type="email"
          autocomplete="email"
          placeholder="seu@email.com"
        />
      </div>
      <div class="flex justify-center overflow-hidden py-1">
        <VueTurnstile
          v-model="captchaToken"
          :site-key="turnstileSiteKey || '0x4AAAAAADe4izf5gmW3H2aL'"
          theme="light"
        />
      </div>
      <button
        type="submit"
        :disabled="isLoading || !captchaToken"
        class="ct-button-primary w-full disabled:opacity-50"
      >
        {{ isLoading ? 'Enviando…' : 'Enviar link de recuperação' }}</button
      ><RouterLink
        to="/login"
        class="block text-center text-sm font-semibold text-[var(--ct-primary)]"
        >Voltar para o login</RouterLink
      >
    </form>
  </AuthShell>
</template>
