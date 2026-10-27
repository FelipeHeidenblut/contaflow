<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import { toast } from 'vue3-toastify'

const auth = useAuthStore()
const exporting = ref(false)
const exportData = async () => {
  exporting.value = true
  try {
    const { data } = await api.get('/api/v1/auth/exportar-escritorio', { responseType: 'blob' })
    const url = URL.createObjectURL(data)
    const link = document.createElement('a')
    link.href = url
    link.download = 'contablytask-dados.json'
    link.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  } catch {
    toast.error('Não foi possível exportar os dados. Tente novamente.')
  } finally {
    exporting.value = false
  }
}
const visible = computed(() => ['active', 'expired'].includes(auth.trial?.status || ''))
const endDate = computed(() =>
  auth.trial?.ends_at ? new Date(auth.trial.ends_at).toLocaleString('pt-BR') : '',
)
let timer: ReturnType<typeof setInterval> | undefined
const refresh = async () => {
  try {
    const { data } = await api.get('/api/v1/auth/me')
    auth.setProfile(data)
  } catch {
    /* Keep the last known state; the API still enforces access. */
  }
}
onMounted(() => {
  void refresh()
  timer = setInterval(() => {
    void refresh()
  }, 60000)
})
onBeforeUnmount(() => clearInterval(timer))
</script>

<template>
  <section
    v-if="visible"
    class="mb-5 rounded-xl border border-blue-200 bg-blue-50 p-4 text-sm text-slate-700"
    aria-label="Teste do plano Profissional"
  >
    <template v-if="auth.trial?.status === 'active'">
      <strong>Profissional grátis: {{ auth.trial.days_remaining }} dia(s) restante(s).</strong>
      <p>Seu teste termina em {{ endDate }}. Sem cobrança automática.</p>
      <p v-if="auth.trial.days_remaining <= 3" class="mt-2 font-semibold">
        Seu teste está chegando ao fim. Escolha um plano para continuar com os recursos do
        Profissional.
      </p>
      <RouterLink v-if="auth.role === 'admin'" to="/dashboard" class="mt-3 inline-block underline"
        >Acompanhar os primeiros passos no dashboard</RouterLink
      >
    </template>
    <template v-else>
      <strong>Seu teste de 14 dias terminou. Você está no plano Gratuito.</strong>
      <p>Seus dados foram preservados. O Gratuito permite 5 clientes ativos e 1 membro.</p>
      <p v-if="auth.trialReadOnly">
        O escritório está acima desses limites e disponível para consulta. O administrador pode
        desativar clientes e remover membros ou contratar um plano para retomar as operações.
      </p>
    </template>
    <div v-if="auth.role === 'admin'" class="mt-3">
      <button type="button" class="underline" :disabled="exporting" @click="exportData">
        {{ exporting ? 'Exportando...' : 'Exportar cadastros e histórico (JSON)' }}
      </button>
      <p class="text-xs">Os arquivos anexados podem ser baixados na tela Documentos.</p>
    </div>
    <RouterLink
      v-if="auth.role === 'admin'"
      to="/faturamento"
      class="mt-3 inline-block font-semibold text-blue-700 underline"
      >Conhecer planos e contratar</RouterLink
    >
  </section>
</template>
