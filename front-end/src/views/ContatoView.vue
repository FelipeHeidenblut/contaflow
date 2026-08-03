<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

const nome = ref('')
const email = ref('')
const empresa = ref('')
const assunto = ref('')
const mensagem = ref('')
const enviado = ref(false)

const contatos = [
  {
    titulo: 'E-mail comercial',
    valor: 'contato@contablytask.com.br',
    descricao: 'Para dúvidas sobre planos, contratação e apresentação da plataforma.',
    icon: 'M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z',
    link: 'mailto:contato@contablytask.com.br'
  },
  {
    titulo: 'Suporte',
    valor: 'suporte@contablytask.com.br',
    descricao: 'Para ajuda com uso da plataforma, orientações operacionais e atendimento.',
    icon: 'M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z',
    link: 'mailto:suporte@contablytask.com.br'
  },
  {
    titulo: 'Horário de atendimento',
    valor: 'Segunda a sexta, das 9h às 18h',
    descricao: 'Atendimento em horário comercial, com retorno priorizado para solicitações recebidas pelo formulário.',
    icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
    link: null
  },
]

const etapas = [
  'Você envia sua mensagem com o contexto principal.',
  'Nosso time analisa o assunto e direciona internamente.',
  'Respondemos com orientação, próximos passos ou encaminhamento comercial.',
]

const faq = [
  {
    pergunta: 'Em quanto tempo vocês respondem?',
    resposta:
      'Nosso objetivo é responder contatos comerciais e institucionais em até 1 dia útil, sempre que possível.',
  },
  {
    pergunta: 'Posso falar sobre planos pela página de contato?',
    resposta:
      'Sim. Você pode usar este canal para tirar dúvidas sobre contratação, funcionamento da plataforma e melhor plano para o seu escritório.',
  },
  {
    pergunta: 'Posso pedir ajuda técnica por aqui?',
    resposta:
      'Pode. Se a solicitação for de suporte, nossa equipe direciona a mensagem para o atendimento mais adequado.',
  },
]

const openFaq = ref<number | null>(0)
const toggleFaq = (index: number) => {
  openFaq.value = openFaq.value === index ? null : index
}

const enviarFormulario = () => {
  enviado.value = true

  nome.value = ''
  email.value = ''
  empresa.value = ''
  assunto.value = ''
  mensagem.value = ''

  setTimeout(() => {
    enviado.value = false
  }, 5000)
}
</script>

<template>
  <div class="min-h-screen overflow-x-hidden bg-[#F8FAFC] text-slate-900">
    <!-- Header -->
    <header class="sticky top-0 z-50 border-b border-slate-200/80 bg-white/85 backdrop-blur-xl">
      <div class="mx-auto flex h-[72px] max-w-7xl items-center justify-between px-5 sm:px-6 lg:px-8">
        <RouterLink to="/" class="group flex items-center gap-3" aria-label="Ir para a página inicial">
          <span class="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 transition-colors group-hover:bg-blue-100">
            <svg class="h-5 w-5 text-blue-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true">
              <path d="M9 11l3 3L22 4" />
              <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
            </svg>
          </span>
          <span class="text-lg font-bold tracking-tight text-slate-950">
            Contably<span class="text-blue-600">Task</span>
          </span>
        </RouterLink>

        <nav class="hidden items-center gap-7 md:flex" aria-label="Navegação principal">
          <RouterLink to="/" class="text-sm font-medium text-slate-500 transition-colors hover:text-slate-950">Início</RouterLink>
          <RouterLink to="/sobre" class="text-sm font-medium text-slate-500 transition-colors hover:text-slate-950">Sobre nós</RouterLink>
          <RouterLink to="/planos" class="text-sm font-medium text-slate-500 transition-colors hover:text-slate-950">Planos</RouterLink>
          <RouterLink to="/como-funciona" class="text-sm font-medium text-slate-500 transition-colors hover:text-slate-950">Como Funciona</RouterLink>
          <RouterLink to="/contato" class="text-sm font-semibold text-slate-950">Contato</RouterLink>
        </nav>

        <RouterLink to="/cadastro" class="hidden min-h-[44px] items-center justify-center rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-blue-700 md:inline-flex">
          Criar escritório
        </RouterLink>
      </div>
    </header>

    <main>
      <!-- Hero e Formulário -->
      <section class="relative overflow-hidden border-b border-slate-200 bg-white">
        <div class="relative mx-auto max-w-7xl px-5 py-16 sm:px-6 lg:px-8 lg:py-20">
          <div class="grid gap-12 lg:grid-cols-[0.88fr_1.12fr] lg:items-start lg:gap-16">
            <div class="max-w-xl">
              <p class="text-sm font-semibold uppercase tracking-[0.16em] text-blue-600">Fale com a ContablyTask</p>
              <h1 class="mt-4 text-4xl font-semibold tracking-[-0.045em] text-slate-950 sm:text-5xl lg:text-6xl">
                Um bom contato começa com contexto claro e resposta objetiva.
              </h1>
              <p class="mt-6 max-w-2xl text-base leading-8 text-slate-600 sm:text-lg">
                Se você quer conhecer melhor a plataforma, entender planos ou tirar dúvidas sobre a rotina do seu escritório, envie sua mensagem. Nosso objetivo é tornar esse primeiro contato simples, humano e útil.
              </p>

              <div class="mt-8 grid gap-4 sm:grid-cols-2">
                <div class="rounded-2xl border border-slate-200 bg-slate-50 p-5 transition-colors hover:border-blue-200 hover:bg-blue-50/50">
                  <p class="text-sm font-semibold text-slate-950">Retorno em até 1 dia útil</p>
                  <p class="mt-2 text-sm leading-7 text-slate-600">Mensagens comerciais e institucionais recebem resposta com prioridade.</p>
                </div>
                <div class="rounded-2xl border border-slate-200 bg-slate-50 p-5 transition-colors hover:border-blue-200 hover:bg-blue-50/50">
                  <p class="text-sm font-semibold text-slate-950">Canal direto e objetivo</p>
                  <p class="mt-2 text-sm leading-7 text-slate-600">Você escreve o contexto principal e nós orientamos o próximo passo.</p>
                </div>
              </div>

              <div class="mt-8 flex items-center gap-3 text-sm text-slate-500">
                <span class="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-50 text-emerald-600">
                  <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="m5 12 4 4L19 6" /></svg>
                </span>
                Seus dados são usados apenas para responder seu contato.
              </div>
            </div>

            <!-- Formulário -->
            <div class="relative">
              <div class="relative rounded-[1.5rem] border border-slate-200 bg-white p-6 shadow-[0_30px_80px_rgba(15,23,42,0.08)] sm:p-8">
                <div class="mb-6">
                  <p class="text-sm font-semibold uppercase tracking-[0.14em] text-blue-600">Enviar mensagem</p>
                  <h2 class="mt-3 text-2xl font-semibold tracking-tight text-slate-950">Conte brevemente o que você precisa</h2>
                  <p class="mt-3 text-sm leading-7 text-slate-600">Quanto mais claro o contexto, melhor conseguimos orientar você.</p>
                </div>

                <div v-if="enviado" class="mb-6 flex items-center gap-3 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">
                  <svg class="h-5 w-5 flex-shrink-0 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                  Mensagem enviada com sucesso. Em breve entraremos em contato.
                </div>

                <form @submit.prevent="enviarFormulario" class="space-y-5">
                  <div class="grid gap-5 sm:grid-cols-2">
                    <div>
                      <label for="nome" class="mb-2 block text-sm font-medium text-slate-700">Nome</label>
                      <input id="nome" v-model="nome" type="text" required placeholder="Seu nome" class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100" />
                    </div>
                    <div>
                      <label for="email" class="mb-2 block text-sm font-medium text-slate-700">E-mail</label>
                      <input id="email" v-model="email" type="email" required placeholder="voce@empresa.com" class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100" />
                    </div>
                  </div>

                  <div class="grid gap-5 sm:grid-cols-2">
                    <div>
                      <label for="empresa" class="mb-2 block text-sm font-medium text-slate-700">Escritório ou empresa</label>
                      <input id="empresa" v-model="empresa" type="text" placeholder="Nome do escritório" class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100" />
                    </div>
                    <div>
                      <label for="assunto" class="mb-2 block text-sm font-medium text-slate-700">Assunto</label>
                      <input id="assunto" v-model="assunto" type="text" required placeholder="Ex.: dúvida sobre planos" class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100" />
                    </div>
                  </div>

                  <div>
                    <label for="mensagem" class="mb-2 block text-sm font-medium text-slate-700">Mensagem</label>
                    <textarea id="mensagem" v-model="mensagem" rows="6" required placeholder="Escreva aqui sua dúvida, contexto ou necessidade." class="w-full resize-none rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"></textarea>
                  </div>

                  <div class="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
                    Ao enviar, você concorda que possamos usar seus dados para responder este contato de forma comercial ou institucional.
                  </div>

                  <button type="submit" class="inline-flex min-h-[48px] w-full items-center justify-center rounded-xl bg-blue-600 px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-100">
                    Enviar mensagem
                    <svg class="ml-2 h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                      <path d="M5 12h14" />
                      <path d="m13 6 6 6-6 6" />
                    </svg>
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Formas de contato -->
      <section class="mx-auto max-w-7xl px-5 py-20 sm:px-6 lg:px-8 lg:py-24">
        <div class="grid gap-12 lg:grid-cols-[0.78fr_1.22fr] lg:gap-20">
          <div>
            <p class="text-sm font-semibold uppercase tracking-[0.16em] text-blue-600">Outros caminhos</p>
            <h2 class="mt-4 text-3xl font-semibold tracking-[-0.04em] text-slate-950 sm:text-4xl">
              Nem todo contato começa por um formulário.
            </h2>
            <p class="mt-6 text-base leading-8 text-slate-600">
              Se preferir, você também pode falar com a ContablyTask por canais diretos. O importante é facilitar o acesso e reduzir a fricção no primeiro contato. Oferecer múltiplas opções de contato costuma melhorar a experiência e aumentar a confiança do visitante.
            </p>
          </div>

          <div class="grid gap-6 md:grid-cols-3">
            <component 
              :is="item.link ? 'a' : 'div'" 
              v-for="item in contatos" 
              :key="item.titulo" 
              :href="item.link ? item.link : undefined" 
              class="group flex h-full flex-col rounded-3xl border border-slate-200 bg-white p-7 shadow-sm transition-all hover:-translate-y-1 hover:shadow-lg hover:border-blue-200"
            >
              <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-600 transition-colors group-hover:bg-blue-600 group-hover:text-white">
                <svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" :d="item.icon" /></svg>
              </div>
              <p class="mt-5 text-sm font-semibold uppercase tracking-[0.12em] text-slate-500">{{ item.titulo }}</p>
              <h3 class="mt-2 text-lg font-semibold tracking-tight text-slate-950 break-words">{{ item.valor }}</h3>
              <p class="mt-4 text-sm leading-7 text-slate-600">{{ item.descricao }}</p>
            </component>
          </div>
        </div>
      </section>

      <!-- O que acontece depois -->
      <section class="border-y border-slate-200 bg-white">
        <div class="mx-auto max-w-7xl px-5 py-20 sm:px-6 lg:px-8 lg:py-24">
          <div class="grid gap-8 lg:grid-cols-[0.95fr_1.05fr] lg:items-stretch">
            <div class="flex flex-col justify-center">
              <p class="text-sm font-semibold uppercase tracking-[0.16em] text-blue-600">Depois do envio</p>
              <h2 class="mt-4 text-3xl font-semibold tracking-[-0.04em] text-slate-950 sm:text-4xl">
                Transparência também faz parte do contato.
              </h2>
              <p class="mt-6 text-base leading-8 text-slate-600">
                Explicar o que acontece após o envio reduz insegurança e mostra que existe alguém do outro lado da mensagem. Páginas de contato tendem a gerar mais confiança quando deixam claro prazo de resposta e próximos passos.
              </p>
            </div>

            <div class="flex flex-col rounded-3xl bg-[#172554] p-7 text-white shadow-xl sm:p-8">
              <p class="text-sm font-semibold uppercase tracking-[0.14em] text-blue-200">Como funciona</p>
              <div class="mt-8 flex-1 space-y-5">
                <div v-for="(etapa, index) in etapas" :key="etapa" class="flex items-start gap-4 rounded-2xl border border-white/10 bg-white/[0.06] p-4 transition-colors hover:bg-white/[0.12]">
                  <span class="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-white text-sm font-semibold text-[#172554]">
                    {{ index + 1 }}
                  </span>
                  <p class="text-sm leading-7 text-white/80">{{ etapa }}</p>
                </div>
              </div>
              <div class="mt-8 flex items-center gap-3 rounded-2xl border border-blue-300/20 bg-blue-400/10 p-4 text-sm text-blue-100">
                <svg class="h-5 w-5 flex-shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                Nosso objetivo é responder com clareza, sem deixar você sem direção.
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- FAQ -->
      <section class="mx-auto max-w-7xl px-5 py-20 sm:px-6 lg:px-8 lg:py-24">
        <div class="grid gap-10 lg:grid-cols-[0.82fr_1.18fr]">
          <div>
            <p class="text-sm font-semibold uppercase tracking-[0.16em] text-blue-600">Dúvidas frequentes</p>
            <h2 class="mt-4 text-3xl font-semibold tracking-[-0.04em] text-slate-950 sm:text-4xl">
              O contato deve ser simples também para quem está avaliando a plataforma.
            </h2>
          </div>

          <div class="space-y-3">
            <div v-for="(item, index) in faq" :key="item.pergunta" class="overflow-hidden rounded-2xl border border-slate-200 bg-white transition-all hover:border-blue-300 hover:shadow-sm">
              <button 
                @click="toggleFaq(index)" 
                class="flex w-full items-center justify-between gap-4 p-6 text-left"
                :class="openFaq === index ? 'bg-slate-50' : 'bg-white'"
              >
                <h3 class="text-base font-semibold tracking-tight text-slate-950">
                  {{ item.pergunta }}
                </h3>
                <span class="flex-shrink-0 text-blue-600 transition-transform duration-300" :class="openFaq === index ? 'rotate-45' : 'rotate-0'">
                  <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
                </span>
              </button>
              <div 
                v-show="openFaq === index" 
                class="grid transition-all duration-300 ease-in-out"
                :class="openFaq === index ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'"
              >
                <div class="overflow-hidden">
                  <p class="px-6 pb-6 text-sm leading-7 text-slate-600">{{ item.resposta }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- CTA final -->
      <section class="mx-auto max-w-7xl px-5 py-20 sm:px-6 lg:px-8 lg:py-24">
        <div class="relative overflow-hidden rounded-[2rem] bg-[#172554] px-7 py-12 sm:px-10 lg:px-14 lg:py-16">
          <div class="relative grid items-center gap-10 lg:grid-cols-[1fr_0.82fr]">
            <div>
              <p class="text-sm font-semibold uppercase tracking-[0.16em] text-blue-200">Vamos conversar</p>
              <h2 class="mt-4 max-w-2xl text-3xl font-semibold tracking-[-0.04em] text-white sm:text-4xl">
                Se a sua operação precisa de mais clareza, esse é um bom ponto de partida.
              </h2>
              <p class="mt-5 max-w-xl text-base leading-8 text-white/70">
                Conheça melhor a ContablyTask, tire suas dúvidas e entenda como a plataforma pode se encaixar na rotina do seu escritório.
              </p>

              <div class="mt-8 flex flex-col gap-3 sm:flex-row">
                <RouterLink to="/cadastro" class="inline-flex min-h-[48px] items-center justify-center rounded-xl bg-white px-6 py-3 text-sm font-semibold text-[#172554] transition-colors hover:bg-blue-50">
                  Criar meu escritório
                </RouterLink>
                <RouterLink to="/planos" class="inline-flex min-h-[48px] items-center justify-center rounded-xl border border-white/15 px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-white/[0.06]">
                  Ver planos
                </RouterLink>
              </div>
            </div>

            <div class="hidden rounded-2xl border border-white/10 bg-white/[0.08] p-5 lg:block">
              <div class="rounded-xl bg-white p-5">
                <p class="text-xs font-semibold uppercase tracking-[0.14em] text-blue-600">Contato com contexto</p>
                <div class="mt-5 space-y-3">
                  <div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
                    <p class="text-sm font-medium text-slate-950">Dúvida sobre contratação</p>
                    <p class="mt-2 text-xs leading-6 text-slate-500">Entender qual plano faz mais sentido para meu escritório.</p>
                  </div>
                  <div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
                    <p class="text-sm font-medium text-slate-950">Necessidade operacional</p>
                    <p class="mt-2 text-xs leading-6 text-slate-500">Quero melhorar o controle de tarefas, documentos e responsáveis.</p>
                  </div>
                  <div class="rounded-xl border border-blue-200 bg-blue-50 p-4">
                    <p class="text-sm font-medium text-slate-950">Resposta orientada</p>
                    <p class="mt-2 text-xs leading-6 text-slate-500">Nosso time retorna com direcionamento mais claro e próximo passo.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>

    <footer class="border-t border-slate-200 bg-white">
      <div class="mx-auto flex max-w-7xl flex-col gap-5 px-5 py-8 text-sm text-slate-500 sm:px-6 md:flex-row md:items-center md:justify-between lg:px-8">
        <RouterLink to="/" class="font-semibold text-slate-800">
          Contably<span class="text-blue-600">Task</span>
        </RouterLink>
        <p>© {{ new Date().getFullYear() }} ContablyTask. Todos os direitos reservados.</p>
        <div class="flex flex-wrap gap-5">
          <RouterLink to="/sobre" class="transition-colors hover:text-slate-950">Sobre nós</RouterLink>
          <RouterLink to="/planos" class="transition-colors hover:text-slate-950">Planos</RouterLink>
          <RouterLink to="/contato" class="transition-colors hover:text-slate-950">Contato</RouterLink>
        </div>
      </div>
    </footer>
  </div>
</template>