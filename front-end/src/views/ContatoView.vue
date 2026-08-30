<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import VueTurnstile from 'vue-turnstile'
import PublicLayout from '@/components/PublicLayout.vue'
import { useScrollReveal } from '@/composables/useScrollReveal'
import { appConfig } from '@/config/env'

const page = ref<HTMLElement | null>(null)
useScrollReveal(page)

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
    <div ref="page" class="ct-modern-landing overflow-hidden">
      <section class="relative border-b border-slate-200 bg-white">
        <div class="ct-engineering-grid pointer-events-none absolute inset-0 opacity-60"></div>
        <div
          class="ct-container relative grid items-center gap-14 py-16 lg:grid-cols-[0.85fr_1.15fr] lg:py-24"
        >
          <div data-reveal>
            <p class="ct-technical-label">Contato · conversa direta</p>
            <h1 class="ct-modern-display mt-6">
              Converse com quem entende
              <span class="ct-gradient-text">a rotina do escritório.</span>
            </h1>
            <p class="mt-6 max-w-xl text-[17px] leading-7 text-slate-600">
              Tire dúvidas sobre planos, implantação ou uso da plataforma. Explique o contexto e
              nossa equipe responde sem roteiro genérico.
            </p>
            <div
              class="mt-8 flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
            >
              <span class="h-2.5 w-2.5 rounded-full bg-emerald-500 ring-4 ring-emerald-50"></span>
              <div>
                <p class="text-xs font-semibold text-[#26344f]">Atendimento em horário comercial</p>
                <p class="mt-1 font-mono text-[9px] uppercase tracking-wider text-slate-400">
                  segunda a sexta · normalmente em até 1 dia útil
                </p>
              </div>
            </div>
          </div>

          <div data-reveal style="--reveal-delay: 120ms" class="grid gap-3 sm:grid-cols-2">
            <a
              href="mailto:contato@contablytask.com.br"
              class="ct-capability-card group flex min-h-[190px] flex-col"
              ><span
                class="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-600"
                ><svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="1.8"
                    d="M4 6h16v12H4V6Zm0 1 8 6 8-6"
                  /></svg
              ></span>
              <p class="mt-6 font-mono text-[9px] uppercase tracking-wider text-blue-600">
                Comercial
              </p>
              <p class="mt-2 text-sm font-semibold text-[#101a38]">contato@contablytask.com.br</p>
              <span class="mt-auto pt-4 text-xs text-slate-400 group-hover:text-blue-600"
                >Planos e plataforma →</span
              ></a
            >
            <a
              href="mailto:suporte@contablytask.com.br"
              class="ct-capability-card group flex min-h-[190px] flex-col"
              ><span
                class="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-600"
                ><svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="1.8"
                    d="M4 13a8 8 0 0 1 16 0v5h-4v-5h4M4 13v5h4v-5H4Zm4 7h5"
                  /></svg
              ></span>
              <p class="mt-6 font-mono text-[9px] uppercase tracking-wider text-blue-600">
                Suporte
              </p>
              <p class="mt-2 text-sm font-semibold text-[#101a38]">suporte@contablytask.com.br</p>
              <span class="mt-auto pt-4 text-xs text-slate-400 group-hover:text-blue-600"
                >Ajuda com sua conta →</span
              ></a
            >
            <div
              class="rounded-2xl border border-blue-950 bg-[var(--ct-navy)] p-6 text-white sm:col-span-2"
            >
              <div class="flex items-center justify-between">
                <p class="font-mono text-[9px] uppercase tracking-wider text-blue-300">
                  Como respondemos
                </p>
                <span class="h-2 w-2 rounded-full bg-emerald-400"></span>
              </div>
              <div class="mt-6 grid gap-5 sm:grid-cols-3">
                <div>
                  <p class="text-lg font-semibold">Contexto primeiro</p>
                  <p class="mt-2 text-xs leading-5 text-white/45">
                    Entendemos a necessidade antes de indicar um plano.
                  </p>
                </div>
                <div>
                  <p class="text-lg font-semibold">Resposta objetiva</p>
                  <p class="mt-2 text-xs leading-5 text-white/45">
                    Sem esconder limitações ou próximos passos.
                  </p>
                </div>
                <div>
                  <p class="text-lg font-semibold">Canal humano</p>
                  <p class="mt-2 text-xs leading-5 text-white/45">
                    Sua mensagem chega à equipe responsável.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="bg-[#f8fafc] py-20 lg:py-28">
        <div class="ct-container grid gap-12 lg:grid-cols-[0.62fr_1.38fr]">
          <div data-reveal class="lg:sticky lg:top-28 lg:self-start">
            <p class="ct-technical-label">Envie sua mensagem</p>
            <h2 class="ct-modern-section-title mt-5">Conte onde a operação precisa avançar.</h2>
            <p class="mt-5 max-w-sm text-sm leading-7 text-slate-600">
              Quanto mais contexto você enviar, mais direta pode ser a nossa resposta.
            </p>
            <div class="mt-8 space-y-4 border-t border-slate-200 pt-6">
              <div class="flex gap-3">
                <span class="font-mono text-[10px] text-blue-600">01</span>
                <p class="text-sm text-slate-600">Identifique o escritório e o assunto.</p>
              </div>
              <div class="flex gap-3">
                <span class="font-mono text-[10px] text-blue-600">02</span>
                <p class="text-sm text-slate-600">Explique a dúvida ou cenário.</p>
              </div>
              <div class="flex gap-3">
                <span class="font-mono text-[10px] text-blue-600">03</span>
                <p class="text-sm text-slate-600">Receba a orientação pelo e-mail informado.</p>
              </div>
            </div>
          </div>

          <form
            data-reveal
            class="rounded-2xl border border-slate-200 bg-white p-6 shadow-[0_16px_45px_rgba(15,23,42,0.06)] sm:p-8"
            @submit.prevent="enviarFormulario"
          >
            <div class="mb-7 flex items-center justify-between border-b border-slate-100 pb-5">
              <div>
                <p class="text-sm font-semibold text-[#101a38]">Formulário de contato</p>
                <p class="mt-1 font-mono text-[9px] uppercase tracking-wider text-slate-400">
                  campos seguros · resposta por e-mail
                </p>
              </div>
              <span
                class="rounded-full bg-blue-50 px-2.5 py-1 text-[9px] font-semibold text-blue-700"
                >Contato</span
              >
            </div>
            <div
              v-if="successMessage"
              role="status"
              class="mb-6 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800"
            >
              {{ successMessage }}
            </div>
            <div
              v-if="errorMessage"
              role="alert"
              class="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
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
              <label for="contact-message" class="ct-label">Como podemos ajudar?</label
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
              class="mt-5 flex justify-center overflow-hidden rounded-xl border border-slate-100 bg-slate-50 py-3"
            >
              <VueTurnstile
                v-model="captchaToken"
                :site-key="turnstileSiteKey || '0x4AAAAAADe4izf5gmW3H2aL'"
                theme="light"
              />
            </div>
            <div
              class="mt-6 flex flex-col-reverse items-start justify-between gap-4 border-t border-slate-100 pt-6 sm:flex-row sm:items-center"
            >
              <p class="max-w-xs text-xs leading-5 text-slate-500">
                Seus dados serão usados somente para responder a esta solicitação.
              </p>
              <button
                class="ct-button-primary ct-landing-primary w-full disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto"
                type="submit"
                :disabled="isSending || !captchaToken"
              >
                {{ isSending ? 'Enviando…' : 'Enviar mensagem' }} <span>→</span>
              </button>
            </div>
          </form>
        </div>
      </section>
    </div>
  </PublicLayout>
</template>
