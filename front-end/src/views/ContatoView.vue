<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import PublicLayout from '@/components/PublicLayout.vue'

const route = useRoute()
const nome = ref('')
const email = ref('')
const empresa = ref('')
const assunto = ref(typeof route.query.assunto === 'string' ? route.query.assunto : '')
const mensagem = ref('')
const enviado = ref(false)

const enviarFormulario = () => {
  const corpo = [
    `Nome: ${nome.value}`,
    `E-mail: ${email.value}`,
    `Escritório: ${empresa.value || '-'}`,
    '',
    mensagem.value,
  ].join('\n')
  window.location.href = `mailto:contato@contablytask.com.br?subject=${encodeURIComponent(assunto.value)}&body=${encodeURIComponent(corpo)}`
  enviado.value = true
}
</script>

<template>
  <PublicLayout>
    <section class="border-b border-[var(--ct-border)] bg-white">
      <div class="ct-container grid gap-14 py-16 lg:grid-cols-[0.8fr_1.2fr] lg:py-24">
        <div>
          <p class="ct-eyebrow">Contato</p>
          <h1 class="ct-display mt-5">Converse com quem conhece a operação.</h1>
          <p class="ct-body-lg mt-6">
            Tire dúvidas sobre planos, implantação ou uso da plataforma. Respondemos em horário
            comercial.
          </p>
          <div class="mt-10 space-y-5 border-t border-[var(--ct-border)] pt-6 text-sm">
            <div>
              <p class="font-semibold">Comercial</p>
              <a
                href="mailto:contato@contablytask.com.br"
                class="mt-1 block text-[var(--ct-primary)]"
                >contato@contablytask.com.br</a
              >
            </div>
            <div>
              <p class="font-semibold">Suporte</p>
              <a
                href="mailto:suporte@contablytask.com.br"
                class="mt-1 block text-[var(--ct-primary)]"
                >suporte@contablytask.com.br</a
              >
            </div>
            <div>
              <p class="font-semibold">Atendimento</p>
              <p class="mt-1 text-[var(--ct-text-muted)]">Segunda a sexta, das 9h às 18h</p>
            </div>
          </div>
        </div>
        <form
          class="rounded-xl border border-[var(--ct-border)] bg-white p-6 sm:p-8"
          @submit.prevent="enviarFormulario"
        >
          <div
            v-if="enviado"
            class="mb-6 border-l-2 border-emerald-500 bg-emerald-50 px-4 py-3 text-sm text-emerald-800"
          >
            Seu aplicativo de e-mail foi aberto com a mensagem preenchida.
          </div>
          <div class="grid gap-5 sm:grid-cols-2">
            <div>
              <label for="contact-name" class="ct-label">Nome</label
              ><input
                id="contact-name"
                v-model="nome"
                class="ct-field"
                required
                autocomplete="name"
              />
            </div>
            <div>
              <label for="contact-email" class="ct-label">E-mail</label
              ><input
                id="contact-email"
                v-model="email"
                class="ct-field"
                required
                type="email"
                autocomplete="email"
              />
            </div>
            <div>
              <label for="contact-company" class="ct-label">Escritório</label
              ><input
                id="contact-company"
                v-model="empresa"
                class="ct-field"
                autocomplete="organization"
              />
            </div>
            <div>
              <label for="contact-subject" class="ct-label">Assunto</label
              ><select id="contact-subject" v-model="assunto" class="ct-field" required>
                <option value="" disabled>Selecione</option>
                <option>Dúvida sobre planos</option>
                <option>Quero conhecer a plataforma</option>
                <option>Suporte técnico</option>
                <option>Plano Business</option>
                <option>Outro assunto</option>
              </select>
            </div>
          </div>
          <div class="mt-5">
            <label for="contact-message" class="ct-label">Como podemos ajudar?</label
            ><textarea
              id="contact-message"
              v-model="mensagem"
              class="ct-field min-h-36 resize-y"
              required
            ></textarea>
          </div>
          <div
            class="mt-6 flex flex-col-reverse items-start justify-between gap-4 border-t border-[var(--ct-border)] pt-6 sm:flex-row sm:items-center"
          >
            <p class="max-w-xs text-xs leading-5 text-[var(--ct-text-muted)]">
              Ao enviar, seu aplicativo de e-mail será aberto para concluir a mensagem.
            </p>
            <button class="ct-button-primary w-full sm:w-auto" type="submit">
              Preparar mensagem
            </button>
          </div>
        </form>
      </div>
    </section>
  </PublicLayout>
</template>
