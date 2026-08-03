<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

const planos = [
  {
    nome: 'Free',
    rotulo: 'Comece grátis',
    descricao: 'Para conhecer a plataforma.',
    price: 'Grátis',
    destaque: false,
    cta: 'Começar grátis',
    recursos: [
      'Até 5 clientes',
      '1 usuário administrador',
      'Calendário de obrigações',
      'Gestão de documentos',
    ],
  },
  {
    nome: 'Básico',
    rotulo: 'Autônomos',
    descricao: 'Para contadores autônomos.',
    price: '79,90',
    destaque: false,
    cta: 'Assinar Básico',
    recursos: [
      'Até 40 clientes',
      'Até 5 usuários',
      'Tudo do Free',
      'Alertas por e-mail',
    ],
  },
  {
    nome: 'Profissional',
    rotulo: 'Mais escolhido',
    descricao: 'Para escritórios em crescimento.',
    price: '149,90',
    destaque: true,
    cta: 'Assinar Profissional',
    recursos: [
      'Até 100 clientes',
      'Até 10 usuários',
      'Tudo do Básico',
      'Distribuição de equipe',
      'Relatórios avançados',
    ],
  },
  {
    nome: 'Business',
    rotulo: 'Operação avançada',
    descricao: 'Para operações maiores.',
    price: '449',
    destaque: false,
    cta: 'Falar com vendas',
    recursos: [
      'Clientes ilimitados',
      'Usuários ilimitados',
      'Tudo do Profissional',
      'API e integrações',
      'Gerente dedicado',
    ],
  },
]

const comparativo = [
  {
    item: 'Gestão de tarefas por cliente',
    free: true,
    basico: true,
    profissional: true,
    business: true,
  },
  {
    item: 'Definição de responsáveis e prazos',
    free: true,
    basico: true,
    profissional: true,
    business: true,
  },
  {
    item: 'Visão operacional centralizada',
    free: true,
    basico: true,
    profissional: true,
    business: true,
  },
  {
    item: 'Mais capacidade de usuários',
    free: false,
    basico: true,
    profissional: true,
    business: true,
  },
  {
    item: 'Mais capacidade de clientes',
    free: false,
    basico: true,
    profissional: true,
    business: true,
  },
  {
    item: 'Condição personalizada',
    free: false,
    basico: false,
    profissional: false,
    business: true,
  },
]

const faq = [
  {
    pergunta: 'Existe teste grátis?',
    resposta:
      'Sim! O plano Free foi criado justamente para isso. Você pode se cadastrar gratuitamente, testar as funcionalidades principais da plataforma e, quando sentir necessidade de mais capacidade, evoluir para um plano pago.',
  },
  {
    pergunta: 'Posso mudar de plano depois?',
    resposta:
      'Sim. A ideia da estrutura por plano é permitir que o escritório avance conforme cresce em equipe e número de clientes. Você pode fazer upgrade a qualquer momento.',
  },
  {
    pergunta: 'O valor é por usuário ou por escritório?',
    resposta:
      'O modelo foi pensado por escritório, com limites de usuários e clientes dentro de cada plano. O valor cobrado engloba toda a operação naquela faixa.',
  },
  {
    pergunta: 'O que acontece quando eu atinjo os limites?',
    resposta:
      'Quando o escritório se aproxima do limite ideal de uso, o próximo passo natural é migrar para um plano com maior capacidade, garantindo que a operação continue fluindo bem.',
  },
]

const beneficios = [
  'Preço claro, sem depender de contato para entender a base da oferta',
  'Planos pensados para diferentes estágios de maturidade do escritório',
  'Estrutura de upgrade alinhada ao crescimento operacional',
]

// Lógica do Acordeão da FAQ
const openFaq = ref<number | null>(0) // Inicia com a primeira pergunta aberta

const toggleFaq = (index: number) => {
  openFaq.value = openFaq.value === index ? null : index
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
          <RouterLink to="/planos" class="text-sm font-semibold text-slate-950">Planos</RouterLink>
          <RouterLink to="/como-funciona" class="text-sm font-medium text-slate-500 transition-colors hover:text-slate-950">Como Funciona</RouterLink>
          <RouterLink to="/contato" class="text-sm font-medium text-slate-500 transition-colors hover:text-slate-950">Contato</RouterLink>
        </nav>

        <RouterLink to="/cadastro" class="hidden min-h-[44px] items-center justify-center rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-blue-700 md:inline-flex">
          Criar escritório
        </RouterLink>
      </div>
    </header>

    <main>
      <!-- Hero -->
      <section class="relative overflow-hidden border-b border-slate-200 bg-white">
        <div class="relative mx-auto max-w-7xl px-5 py-16 sm:px-6 lg:px-8 lg:py-20">
          <div class="grid gap-12 lg:grid-cols-[0.9fr_1.1fr] lg:items-start lg:gap-16">
            <div class="max-w-xl">
              <p class="text-sm font-semibold uppercase tracking-[0.16em] text-blue-600">Planos ContablyTask</p>
              <h1 class="mt-4 text-4xl font-semibold tracking-[-0.045em] text-slate-950 sm:text-5xl lg:text-6xl">
                Planos pensados para o momento operacional do seu escritório.
              </h1>
              <p class="mt-6 max-w-2xl text-base leading-8 text-slate-600 sm:text-lg">
                A ContablyTask foi estruturada para acompanhar desde escritórios que estão organizando o básico até operações em fase de crescimento. Escolha o plano ideal sem se perder em excesso de opções.
              </p>

              <div class="mt-6 flex items-center gap-3 text-sm text-slate-500">
                <span class="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-50 text-emerald-600">
                  <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="m5 12 4 4L19 6" /></svg>
                </span>
                Estrutura clara, com transparência sobre capacidade e crescimento.
              </div>
            </div>

            <!-- Card de Benefícios Limpo -->
            <div class="relative">
              <div class="relative rounded-[1.5rem] border border-slate-200 bg-white p-6 shadow-[0_30px_80px_rgba(15,23,42,0.08)] sm:p-8">
                <div class="flex items-start justify-between gap-6">
                  <div>
                    <p class="text-sm font-semibold uppercase tracking-[0.14em] text-blue-600">Estrutura comercial</p>
                    <h2 class="mt-3 text-2xl font-semibold tracking-tight text-slate-950">Escolha com mais clareza</h2>
                  </div>
                  <span class="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">Modelo por escritório</span>
                </div>

                <div class="mt-8 space-y-4">
                  <div v-for="item in beneficios" :key="item" class="flex items-start gap-3 rounded-2xl border border-slate-200 bg-slate-50 p-4 transition-colors hover:bg-slate-100">
                    <span class="mt-1 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-blue-100 text-blue-600">
                      <svg class="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8" aria-hidden="true"><path d="m5 12 4 4L19 6" /></svg>
                    </span>
                    <p class="text-sm leading-7 text-slate-600">{{ item }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Cards de planos -->
      <section class="mx-auto max-w-7xl px-5 py-20 sm:px-6 lg:px-8 lg:py-24">
        <div class="grid items-stretch gap-6 md:grid-cols-2 xl:grid-cols-4">
          <article
            v-for="plano in planos"
            :key="plano.nome"
            :class="[
              'relative flex h-full flex-col rounded-[1.75rem] border p-6 transition-all hover:-translate-y-1 hover:shadow-xl sm:p-7',
              plano.destaque ? 'border-blue-600 bg-white shadow-xl ring-1 ring-blue-600 xl:scale-105 xl:z-10' : 'border-slate-200 bg-white shadow-sm'
            ]"
          >
            <div v-if="plano.destaque" class="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-blue-600 px-4 py-1 text-xs font-bold text-white shadow-md">
              Recomendado
            </div>

            <div class="flex items-start justify-between gap-4">
              <div>
                <p :class="['text-xs font-semibold uppercase tracking-[0.14em]', plano.destaque ? 'text-blue-600' : 'text-slate-500']">
                  {{ plano.rotulo }}
                </p>
                <h2 class="mt-2 text-2xl font-semibold tracking-tight text-slate-950">{{ plano.nome }}</h2>
              </div>
            </div>

            <p class="mt-3 text-sm leading-6 text-slate-600">{{ plano.descricao }}</p>

            <div class="mt-6 border-t border-slate-200 pt-6">
              <div class="flex items-end gap-2">
                <span v-if="plano.price !== 'Grátis'" class="pb-1 text-sm font-bold text-slate-500">R$</span>
                <span class="text-4xl font-semibold tracking-tight text-slate-950">{{ plano.price }}</span>
                <span v-if="plano.price !== 'Grátis'" class="pb-1 text-sm text-slate-500">/mês</span>
              </div>
            </div>

            <ul class="mt-6 flex-1 space-y-3">
              <li v-for="recurso in plano.recursos" :key="recurso" class="flex items-start gap-3 text-sm leading-6 text-slate-600">
                <span class="mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-blue-100 text-blue-600">
                  <svg class="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8" aria-hidden="true"><path d="m5 12 4 4L19 6" /></svg>
                </span>
                {{ recurso }}
              </li>
            </ul>

            <div class="mt-8">
              <RouterLink
                :to="plano.nome === 'Business' ? '/contato' : '/cadastro'"
                :class="[
                  'inline-flex min-h-[48px] w-full items-center justify-center rounded-xl px-6 py-3 text-sm font-semibold transition-colors',
                  plano.destaque ? 'bg-blue-600 text-white hover:bg-blue-700' : 'border border-slate-200 bg-white text-slate-900 hover:border-blue-300 hover:text-blue-700'
                ]"
              >
                {{ plano.cta }}
              </RouterLink>
            </div>
          </article>
        </div>
      </section>

      <!-- Bloco de apoio -->
      <section class="border-y border-slate-200 bg-white">
        <div class="mx-auto max-w-7xl px-5 py-20 sm:px-6 lg:px-8 lg:py-24">
          <div class="grid gap-8 lg:grid-cols-[0.95fr_1.05fr] lg:items-start">
            <div>
              <p class="text-sm font-semibold uppercase tracking-[0.16em] text-blue-600">Como pensar na escolha</p>
              <h2 class="mt-4 text-3xl font-semibold tracking-[-0.04em] text-slate-950 sm:text-4xl">
                O melhor plano é o que acompanha o estágio atual da sua operação.
              </h2>
              <p class="mt-6 text-base leading-8 text-slate-600">
                Entender rapidamente “qual plano é para mim” é muito mais eficiente do que listar recursos de forma genérica. Clareza converte mais do que excesso de informação.
              </p>
            </div>

            <div class="rounded-3xl bg-[#172554] p-7 text-white sm:p-8">
              <p class="text-sm font-semibold uppercase tracking-[0.14em] text-blue-200">Regra prática</p>
              <div class="mt-8 space-y-5">
                <div class="rounded-2xl border border-white/10 bg-white/[0.06] p-4 transition-colors hover:bg-white/[0.12]">
                  <p class="text-sm font-semibold text-white">Free e Básico</p>
                  <p class="mt-2 text-sm leading-7 text-white/75">Para quem está saindo do improviso e quer começar a organizar o operacional com uma estrutura mais clara.</p>
                </div>
                <div class="rounded-2xl border border-white/10 bg-white/[0.06] p-4 transition-colors hover:bg-white/[0.12]">
                  <p class="text-sm font-semibold text-white">Profissional</p>
                  <p class="mt-2 text-sm leading-7 text-white/75">Para escritórios que já precisam coordenar melhor pessoas, volume de tarefas e carteira de clientes.</p>
                </div>
                <div class="rounded-2xl border border-white/10 bg-white/[0.06] p-4 transition-colors hover:bg-white/[0.12]">
                  <p class="text-sm font-semibold text-white">Business</p>
                  <p class="mt-2 text-sm leading-7 text-white/75">Para operações mais robustas, que pedem configuração comercial e capacidade ajustada ao porte.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Comparativo -->
      <section class="mx-auto max-w-7xl px-5 py-20 sm:px-6 lg:px-8 lg:py-24">
        <div class="max-w-3xl">
          <p class="text-sm font-semibold uppercase tracking-[0.16em] text-blue-600">Comparação rápida</p>
          <h2 class="mt-4 text-3xl font-semibold tracking-[-0.04em] text-slate-950 sm:text-4xl">
            Veja o que muda entre os planos sem precisar ler tudo em detalhe.
          </h2>
          <p class="mt-5 text-base leading-8 text-slate-600">
            Uma tabela comparativa ajuda a remover dúvidas e melhora a leitura para quem já chegou à página com intenção de compra.
          </p>
        </div>

        <div class="mt-10 overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
          <div class="overflow-x-auto">
            <table class="min-w-full text-left">
              <thead class="border-b border-slate-200 bg-slate-50">
                <tr>
                  <th class="px-6 py-5 text-sm font-semibold text-slate-950">Recurso</th>
                  <th class="px-6 py-5 text-center text-sm font-semibold text-slate-950">Free</th>
                  <th class="px-6 py-5 text-center text-sm font-semibold text-slate-950">Básico</th>
                  <th class="px-6 py-5 text-center text-sm font-semibold text-blue-700 bg-blue-50/50">Profissional</th>
                  <th class="px-6 py-5 text-center text-sm font-semibold text-slate-950">Business</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="linha in comparativo" :key="linha.item" class="border-b border-slate-100 last:border-b-0 transition-colors hover:bg-slate-50">
                  <td class="px-6 py-5 text-sm font-medium text-slate-900">{{ linha.item }}</td>
                  <td class="px-6 py-5 text-center">
                    <svg v-if="linha.free" class="mx-auto h-5 w-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" /></svg>
                    <span v-else class="text-slate-300">—</span>
                  </td>
                  <td class="px-6 py-5 text-center">
                    <svg v-if="linha.basico" class="mx-auto h-5 w-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" /></svg>
                    <span v-else class="text-slate-300">—</span>
                  </td>
                  <td class="px-6 py-5 text-center bg-blue-50/30">
                    <svg v-if="linha.profissional" class="mx-auto h-5 w-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" /></svg>
                    <span v-else class="text-slate-300">—</span>
                  </td>
                  <td class="px-6 py-5 text-center">
                    <svg v-if="linha.business" class="mx-auto h-5 w-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" /></svg>
                    <span v-else class="text-slate-300">—</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- FAQ (Acordeão) -->
      <section class="border-y border-slate-200 bg-white">
        <div class="mx-auto max-w-7xl px-5 py-20 sm:px-6 lg:px-8 lg:py-24">
          <div class="grid gap-10 lg:grid-cols-[0.82fr_1.18fr]">
            <div>
              <p class="text-sm font-semibold uppercase tracking-[0.16em] text-blue-600">Perguntas frequentes</p>
              <h2 class="mt-4 text-3xl font-semibold tracking-[-0.04em] text-slate-950 sm:text-4xl">
                As dúvidas mais comuns precisam estar respondidas na própria página.
              </h2>
              <p class="mt-6 text-base leading-8 text-slate-600">
                Uma FAQ curta, transparente e objetiva ajuda a reduzir objeções na etapa de decisão.
              </p>
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
        </div>
      </section>

      <!-- CTA final -->
      <section class="mx-auto max-w-7xl px-5 py-20 sm:px-6 lg:px-8 lg:py-24">
        <div class="relative overflow-hidden rounded-[2rem] bg-[#172554] px-7 py-12 sm:px-10 lg:px-14 lg:py-16">
          <div class="relative grid items-center gap-10 lg:grid-cols-[1fr_0.82fr]">
            <div>
              <p class="text-sm font-semibold uppercase tracking-[0.16em] text-blue-200">Próximo passo</p>
              <h2 class="mt-4 max-w-2xl text-3xl font-semibold tracking-[-0.04em] text-white sm:text-4xl">
                Escolha um plano que acompanhe o momento do seu escritório hoje — e o crescimento de amanhã.
              </h2>
              <p class="mt-5 max-w-xl text-base leading-8 text-white/70">
                Se você já sabe o que precisa, pode começar agora. Se ainda tiver dúvidas sobre o melhor enquadramento, fale com a gente.
              </p>

              <div class="mt-8 flex flex-col gap-3 sm:flex-row">
                <RouterLink to="/cadastro" class="inline-flex min-h-[48px] items-center justify-center rounded-xl bg-white px-6 py-3 text-sm font-semibold text-[#172554] transition-colors hover:bg-blue-50">
                  Criar meu escritório
                </RouterLink>
                <RouterLink to="/contato" class="inline-flex min-h-[48px] items-center justify-center rounded-xl border border-white/15 px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-white/[0.06]">
                  Falar com comercial
                </RouterLink>
              </div>
            </div>

            <div class="hidden rounded-2xl border border-white/10 bg-white/[0.08] p-5 lg:block">
              <div class="rounded-xl bg-white p-5">
                <p class="text-xs font-semibold uppercase tracking-[0.14em] text-blue-600">Escolha orientada</p>
                <div class="mt-5 space-y-3">
                  <div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
                    <p class="text-sm font-medium text-slate-950">Quero começar a estruturar</p>
                    <p class="mt-2 text-xs leading-6 text-slate-500">Comece no Free e evolua para o Básico.</p>
                  </div>
                  <div class="rounded-xl border border-blue-200 bg-blue-50 p-4">
                    <p class="text-sm font-medium text-slate-950">Preciso coordenar melhor a operação</p>
                    <p class="mt-2 text-xs leading-6 text-slate-500">Plano Profissional para fase de crescimento.</p>
                  </div>
                  <div class="rounded-xl border border-slate-200 bg-slate-50 p-4">
                    <p class="text-sm font-medium text-slate-950">Tenho uma operação maior</p>
                    <p class="mt-2 text-xs leading-6 text-slate-500">Fale com comercial para o plano Business.</p>
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