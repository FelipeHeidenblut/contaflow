<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import VueTurnstile from 'vue-turnstile'
import PublicLayout from '@/components/PublicLayout.vue'
import PublicPageHero from '@/components/PublicPageHero.vue'
import { appConfig } from '@/config/env'

const route = useRoute()
const allowedSubjects = [
  'Dúvida sobre planos',
  'Quero conhecer a plataforma',
  'Suporte técnico',
  'Alterar plano',
  'Plano Empresarial',
  'Outro assunto',
]
const querySubject =
  route.query.assunto === 'Plano Business' ? 'Plano Empresarial' : route.query.assunto
const nome = ref('')
const email = ref('')
const empresa = ref('')
const assunto = ref(
  typeof querySubject === 'string' && allowedSubjects.includes(querySubject) ? querySubject : '',
)
const mensagem = ref('')
const captchaToken = ref('')
const isSending = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
const turnstileSiteKey = appConfig.turnstileSiteKey
const apiBaseUrl = appConfig.apiBaseUrl

const captchaMedia = window.matchMedia('(max-width: 380px)')
const compactCaptcha = ref(captchaMedia.matches)
const updateCaptchaLayout = () => {
  compactCaptcha.value = captchaMedia.matches
  captchaToken.value = ''
}
onMounted(() => captchaMedia.addEventListener('change', updateCaptchaLayout))
onUnmounted(() => captchaMedia.removeEventListener('change', updateCaptchaLayout))

const getResponseError = (detail: unknown) => {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => (typeof item?.msg === 'string' ? item.msg : ''))
      .filter(Boolean)
    if (messages.length) return messages.join(' ')
  }
  return 'Não foi possível enviar a mensagem.'
}

const enviarFormulario = async () => {
  if (!captchaToken.value) {
    errorMessage.value = 'Aguarde a verificação de segurança antes de enviar.'
    return
  }
  isSending.value = true
  errorMessage.value = ''
  successMessage.value = ''
  try {
    const response = await fetch(`${apiBaseUrl}/api/v1/contact`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        nome: nome.value,
        email: email.value,
        empresa: empresa.value,
        assunto: assunto.value,
        mensagem: mensagem.value,
        captcha_token: captchaToken.value,
      }),
    })
    const result = await response.json().catch(() => ({}))
    if (!response.ok) throw new Error(getResponseError(result.detail))

    successMessage.value = result.message
    nome.value = ''
    email.value = ''
    empresa.value = ''
    assunto.value = ''
    mensagem.value = ''
    captchaToken.value = ''
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : 'Não foi possível enviar a mensagem.'
    captchaToken.value = ''
  } finally {
    isSending.value = false
  }
}
</script>
<template>
  <PublicLayout>
    <div class="ct-clarity-page">
      <PublicPageHero
        eyebrow="Fale com a gente"
        title="Vamos conversar sobre o seu escritório?"
        description="Tire dúvidas sobre planos, conheça a plataforma ou conte como podemos ajudar na organização da sua rotina."
        align-start
      >
        <template #actions>
          <div class="w-full max-w-md space-y-3">
            <a href="mailto:contato@contablytask.com.br" class="ct-public-contact-channel"
              ><span class="ct-public-icon"
                ><svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.8"
                  aria-hidden="true"
                >
                  <path d="M4 6h16v12H4V6Zm0 1 8 6 8-6" /></svg
              ></span>
              <div class="min-w-0">
                <p class="text-sm font-semibold">Planos e plataforma</p>
                <p class="mt-1 text-xs text-slate-500">contato@contablytask.com.br</p>
              </div></a
            >
            <a href="mailto:suporte@contablytask.com.br" class="ct-public-contact-channel"
              ><span class="ct-public-icon"
                ><svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.8"
                  aria-hidden="true"
                >
                  <path d="M4 13a8 8 0 0 1 16 0v5h-4v-5h4M4 13v5h4v-5H4Zm4 7h5" /></svg
              ></span>
              <div class="min-w-0">
                <p class="text-sm font-semibold">Ajuda com sua conta</p>
                <p class="mt-1 text-xs text-slate-500">suporte@contablytask.com.br</p>
              </div></a
            >
          </div>
        </template>
        <template #note>Sua mensagem será respondida pelo e-mail informado.</template>
        <form class="ct-public-form" @submit.prevent="enviarFormulario">
          <h2 class="text-2xl font-semibold tracking-tight">Como podemos ajudar?</h2>
          <p class="mb-6 mt-2 text-sm leading-6 text-slate-500">
            Preencha os dados e conte um pouco sobre o que você precisa.
          </p>
          <div
            v-if="successMessage"
            role="status"
            class="mb-5 rounded-lg border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm text-emerald-700"
          >
            {{ successMessage }}
          </div>
          <div
            v-if="errorMessage"
            role="alert"
            class="mb-5 rounded-lg border border-rose-100 bg-rose-50 px-4 py-3 text-sm text-rose-600"
          >
            {{ errorMessage }}
          </div>
          <div class="grid gap-5 sm:grid-cols-2">
            <div>
              <label for="contact-name" class="ct-label">Nome</label
              ><input
                id="contact-name"
                v-model="nome"
                class="ct-field"
                required
                minlength="2"
                maxlength="120"
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
                maxlength="150"
                autocomplete="organization"
              />
            </div>
            <div>
              <label for="contact-subject" class="ct-label">Assunto</label
              ><select id="contact-subject" v-model="assunto" class="ct-field" required>
                <option value="" disabled>Selecione</option>
                <option v-for="option in allowedSubjects" :key="option">{{ option }}</option>
              </select>
            </div>
          </div>
          <div class="mt-5">
            <label for="contact-message" class="ct-label">Mensagem</label
            ><textarea
              id="contact-message"
              v-model="mensagem"
              class="ct-field min-h-36 resize-y"
              required
              minlength="10"
              maxlength="4000"
            ></textarea>
            <p class="ct-help text-right">{{ mensagem.length }}/4000</p>
          </div>
          <div
            class="mt-5 flex min-w-0 justify-center overflow-hidden rounded-lg border border-slate-100 bg-[#f8fbff] py-3"
          >
            <VueTurnstile
              :key="compactCaptcha ? 'compact' : 'normal'"
              :size="compactCaptcha ? 'compact' : 'normal'"
              v-model="captchaToken"
              :site-key="turnstileSiteKey || '0x4AAAAAADe4izf5gmW3H2aL'"
              theme="light"
            />
          </div>
          <button
            class="ct-button-primary mt-5 w-full disabled:cursor-not-allowed disabled:opacity-50"
            type="submit"
            :disabled="isSending || !captchaToken"
          >
            {{ isSending ? 'Enviando…' : 'Enviar mensagem' }} <span aria-hidden="true">→</span>
          </button>
          <p class="mt-4 text-xs leading-6 text-slate-500">
            Seus dados serão usados para responder a esta solicitação. Consulte nossa
            <RouterLink to="/privacidade" class="text-blue-600 underline"
              >Política de Privacidade</RouterLink
            >.
          </p>
        </form>
      </PublicPageHero>
      <section class="ct-public-section">
        <div class="ct-container grid gap-5 md:grid-cols-2">
          <div class="ct-public-card">
            <h3>Quer conhecer a plataforma?</h3>
            <p class="mt-3">
              Veja como clientes, tarefas, prazos e documentos se conectam na rotina do escritório.
            </p>
            <RouterLink to="/como-funciona" class="ct-public-link mt-5"
              >Veja como funciona <span aria-hidden="true">→</span></RouterLink
            >
          </div>
          <div class="ct-public-card">
            <h3>Está escolhendo um plano?</h3>
            <p class="mt-3">
              Compare os limites de clientes e equipe e encontre a capacidade certa para sua
              operação.
            </p>
            <RouterLink to="/planos" class="ct-public-link mt-5"
              >Conheça os planos <span aria-hidden="true">→</span></RouterLink
            >
          </div>
        </div>
      </section>
    </div>
  </PublicLayout>
</template>
