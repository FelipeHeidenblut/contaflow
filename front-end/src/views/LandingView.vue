<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

const email = ref('')
const ctaMsg = ref('')

const features = [
  {
    icon: '📅',
    title: 'Calendário de obrigações',
    desc: 'Visualize todos os vencimentos fiscais em um calendário inteligente. Configure alertas automáticos por e-mail ou WhatsApp.',
  },
  {
    icon: '👥',
    title: 'Gestão por cliente',
    desc: 'Organize tarefas por cliente, sócio ou colaborador. Veja em segundos o que está pendente para cada um.',
  },
  {
    icon: '📊',
    title: 'Painel de produtividade',
    desc: 'Métricas reais do seu escritório: tarefas concluídas, tempo médio por obrigação e gargalos da equipe.',
  },
  {
    icon: '🔔',
    title: 'Alertas de prazo',
    desc: 'Nunca mais perca um prazo da Receita Federal. Receba notificações com antecedência configurável por tipo de obrigação.',
  },
  {
    icon: '📎',
    title: 'Documentos por tarefa',
    desc: 'Anexe comprovantes, XMLs e planilhas diretamente nas tarefas. Histórico completo de cada obrigação.',
  },
  {
    icon: '🤝',
    title: 'Colaboração em equipe',
    desc: 'Delegue com um clique, adicione comentários e acompanhe o status em tempo real sem precisar interromper ninguém.',
  },
]

const steps = [
  {
    title: 'Cadastre seus clientes',
    desc: 'Importe sua base de clientes em minutos. Vincule as obrigações fiscais de cada CNPJ ao responsável na sua equipe.',
  },
  {
    title: 'Organize as tarefas',
    desc: 'Use os modelos prontos para escritórios contábeis ou crie seu próprio fluxo. Atribua, priorize e defina prazos.',
  },
  {
    title: 'Entregue com confiança',
    desc: 'Acompanhe o progresso em tempo real, comprove o trabalho realizado e mantenha seu cliente sempre informado.',
  },
]

const testimonials = [
  {
    initials: 'MF',
    name: 'Marina Fonseca',
    role: 'Sócia — Fonseca & Associados, SP',
    text: 'Antes eu usava 3 planilhas para controlar os prazos. Hoje o Contably Task faz isso sozinho e minha equipe sabe exatamente o que fazer toda manhã.',
  },
  {
    initials: 'CR',
    name: 'Carlos Ribeiro',
    role: 'Contador — Escritório Ribeiro, MG',
    text: 'O dashboard de obrigações salvou meu escritório em dois meses. Zerou os atrasos que eu tinha com o eSocial dos clientes.',
  },
  {
    initials: 'AP',
    name: 'Ana Paula Torres',
    role: 'Gestora — Torres Contabilidade, RJ',
    text: 'A melhor parte é conseguir ver tudo por cliente em um só lugar. Meus colaboradores ficaram muito mais autônomos desde que implementamos.',
  },
]

const plans = [
  {
    name: 'Starter',
    price: '79',
    featured: false,
    desc: 'Para contadores autônomos.',
    cta: 'Começar grátis',
    features: [
      'Até 20 clientes',
      '2 usuários',
      'Calendário de obrigações',
      'Alertas por e-mail',
      'Suporte por chat',
    ],
  },
  {
    name: 'Básico',
    price: '149',
    featured: false,
    desc: 'Para contadores autônomos.',
    cta: 'Começar grátis',
    features: [
      'Até 40 clientes',
      '5 usuários',
      'Calendário de obrigações',
      'Alertas por e-mail',
      'Suporte por chat',
    ],
  },
  {
    name: 'Profissional',
    price: '197',
    featured: true,
    desc: 'Para escritórios em crescimento.',
    cta: 'Testar 7 dias grátis',
    features: [
      'Até 100 clientes',
      '10 usuários',
      'Tudo do Starter',
      'Painel de produtividade',
      'Alertas por WhatsApp',
      'Documentos por tarefa',
      'Relatórios por cliente',
    ],
  },
  {
    name: 'Business',
    price: '449',
    featured: false,
    desc: 'Para grandes operações.',
    cta: 'Falar com vendas',
    features: [
      'Clientes ilimitados',
      'Usuários ilimitados',
      'Tudo do Profissional',
      'API e integrações',
      'Gerente de conta dedicado',
      'Onboarding assistido',
    ],
  },
]

const scrollTo = (id: string) => {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
}

const handleCTA = () => {
  if (!email.value || !email.value.includes('@')) {
    ctaMsg.value = 'Por favor, insira um e-mail válido.'
    return
  }
  ctaMsg.value = '✅ Ótimo! Você será o primeiro a saber quando abrirmos o acesso.'
  email.value = ''
}

// Diretiva customizada para o Fade-in ao rolar (Substitui o IntersectionObserver antigo)
const vFadeIn = {
  mounted(el: HTMLElement) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            el.classList.add('visible')
            observer.unobserve(el)
          }
        })
      },
      { threshold: 0.1 },
    )
    observer.observe(el)
  },
}
</script>

<template>
  <div class="bg-[#f8f8f8] text-[#2a2a2a] antialiased font-sans">
    <!-- NAV -->
    <nav
      class="sticky top-0 z-50 bg-[#f8f8f8]/92 backdrop-blur-md border-b border-gray-200 h-16 flex items-center justify-between px-[5%]"
    >
      <div class="flex items-center gap-2.5">
        <div class="w-9 h-9 rounded-[10px] bg-[#19341a] flex items-center justify-center">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="#ff8a65"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="w-5 h-5"
          >
            <path d="M9 11l3 3L22 4" />
            <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" />
          </svg>
        </div>
        <span class="text-[1.05rem] font-bold text-[#19341a]"
          >Contably <span class="text-[#ff8a65]">Task</span></span
        >
      </div>
      <div class="hidden md:flex items-center gap-7">
        <a
          href="#features"
          class="text-[0.9rem] font-medium text-[#2a2a2a] hover:text-[#19341a] transition-colors"
          >Funcionalidades</a
        >
        <a
          href="#how"
          class="text-[0.9rem] font-medium text-[#2a2a2a] hover:text-[#19341a] transition-colors"
          >Como funciona</a
        >
        <a
          href="#pricing"
          class="text-[0.9rem] font-medium text-[#2a2a2a] hover:text-[#19341a] transition-colors"
          >Planos</a
        >
        <RouterLink
          to="/login"
          class="inline-flex items-center bg-transparent text-[#19341a] border-2 border-[#19341a]/20 rounded-lg py-2 px-5 font-semibold text-[0.88rem] cursor-pointer hover:bg-[#eaf3ea] hover:-translate-y-0 transition-all"
        >
          Login
        </RouterLink>
        <RouterLink
          to="/cadastro"
          class="inline-flex items-center bg-[#ff8a65] text-white border-none rounded-lg py-2 px-5 font-semibold text-[0.88rem] cursor-pointer hover:bg-[#f07047] hover:-translate-y-0.5 transition-all"
        >
          Começar grátis
        </RouterLink>
      </div>
    </nav>

    <!-- HERO -->
    <section
      class="max-w-[1100px] mx-auto pt-20 pb-16 px-[5%] md:grid md:grid-cols-2 md:gap-16 items-center"
    >
      <div v-fade-in class="fade-in">
        <div
          class="inline-flex items-center gap-2 bg-[#eaf3ea] text-[#19341a] rounded-full py-1.5 px-3.5 text-[0.78rem] font-semibold tracking-wider uppercase mb-5"
        >
          <span class="w-1.5 h-1.5 rounded-full bg-[#ff8a65]"></span> Feito para contadores
        </div>
        <h1 class="text-4xl lg:text-5xl font-extrabold text-[#19341a] leading-tight mb-5">
          Organize seu escritório.<br />Entregue com
          <em class="not-italic text-[#ff8a65]">precisão.</em>
        </h1>
        <p class="text-[1.05rem] text-gray-500 max-w-[440px] mb-9">
          Gerencie prazos, delegue tarefas e acompanhe obrigações fiscais em um único lugar — sem
          planilha, sem caos.
        </p>
        <div class="flex gap-3.5 flex-wrap">
          <RouterLink
            to="/cadastro"
            class="inline-flex items-center bg-[#ff8a65] text-white border-none rounded-lg py-2 px-5 font-semibold text-[0.88rem] cursor-pointer hover:bg-[#f07047] hover:-translate-y-0.5 transition-all"
          >
            Testar 7 dias grátis
          </RouterLink>
          <button
            @click="scrollTo('how')"
            class="inline-flex items-center bg-transparent text-[#19341a] border-2 border-[#19341a] rounded-lg py-2 px-5 font-semibold text-[0.88rem] cursor-pointer hover:bg-[#19341a] hover:text-white transition-colors"
          >
            Ver como funciona
          </button>
        </div>
        <div class="mt-8 flex items-center gap-2.5">
          <p class="text-[0.82rem] text-gray-500">
            <strong class="text-[#2a2a2a]">Faça parte dessa nova experiência</strong> em gestão de
            tarefas!
          </p>
        </div>
      </div>

      <!-- TASK BOARD -->
      <div
        v-fade-in
        class="fade-in bg-white rounded-2xl border border-gray-200 shadow-[0_20px_60px_rgba(25,52,26,0.10)] p-5 mt-10 md:mt-0 hidden sm:block"
      >
        <div class="flex items-center justify-between mb-4">
          <span class="text-[0.85rem] font-bold text-[#19341a]">📋 Obrigações — Junho 2025</span>
          <div class="flex gap-1.5">
            <span class="w-2.5 h-2.5 rounded-full bg-[#ff6b6b]"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-[#ffd93d]"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-[#6bcb77]"></span>
          </div>
        </div>
        <div class="grid sm:grid-cols-3 gap-2.5">
          <!-- Coluna A Fazer -->
          <div>
            <div
              class="text-[0.72rem] font-bold tracking-wider uppercase text-gray-500 mb-2.5 pb-2 border-b-2 border-gray-200"
            >
              A fazer
            </div>
            <div
              class="bg-[#f8f8f8] rounded-lg p-2.5 mb-2 border-l-[3px] border-[#19341a] hover:-translate-y-0.5 hover:shadow-sm transition-all"
            >
              <div class="text-[0.78rem] font-semibold text-[#2a2a2a] mb-1">
                SPED Fiscal — Cliente A
              </div>
              <div class="text-[0.68rem] text-gray-500">Vence 20/06</div>
              <div
                class="inline-block bg-[#eaf3ea] text-[#19341a] rounded px-1.5 py-0.5 text-[0.65rem] font-bold mt-1.5"
              >
                Fiscal
              </div>
            </div>
            <div
              class="bg-[#f8f8f8] rounded-lg p-2.5 mb-2 border-l-[3px] border-[#ff8a65] hover:-translate-y-0.5 hover:shadow-sm transition-all"
            >
              <div class="text-[0.78rem] font-semibold text-[#2a2a2a] mb-1">
                Folha de pagamento — Junho
              </div>
              <div class="text-[0.68rem] text-gray-500">Vence 18/06</div>
              <div
                class="inline-block bg-[#fff3e0] text-[#e65100] rounded px-1.5 py-0.5 text-[0.65rem] font-bold mt-1.5"
              >
                Urgente
              </div>
            </div>
            <div
              class="bg-[#f8f8f8] rounded-lg p-2.5 mb-2 border-l-[3px] border-gray-400 hover:-translate-y-0.5 hover:shadow-sm transition-all"
            >
              <div class="text-[0.78rem] font-semibold text-[#2a2a2a] mb-1">
                DAS Simples — 3 clientes
              </div>
              <div class="text-[0.68rem] text-gray-500">Vence 25/06</div>
              <div
                class="inline-block bg-[#eaf3ea] text-[#19341a] rounded px-1.5 py-0.5 text-[0.65rem] font-bold mt-1.5"
              >
                Tributário
              </div>
            </div>
          </div>
          <!-- Coluna Em andamento -->
          <div>
            <div
              class="text-[0.72rem] font-bold tracking-wider uppercase text-gray-500 mb-2.5 pb-2 border-b-2 border-gray-200"
            >
              Em andamento
            </div>
            <div
              class="bg-[#f8f8f8] rounded-lg p-2.5 mb-2 border-l-[3px] border-[#19341a] animate-pulse-border hover:-translate-y-0.5 hover:shadow-sm transition-all"
            >
              <div class="text-[0.78rem] font-semibold text-[#2a2a2a] mb-1">
                DCTF Web — Cliente B
              </div>
              <div class="text-[0.68rem] text-gray-500">Atribuído: Ana</div>
              <div
                class="inline-block bg-[#eaf3ea] text-[#19341a] rounded px-1.5 py-0.5 text-[0.65rem] font-bold mt-1.5"
              >
                eSocial
              </div>
            </div>
            <div
              class="bg-[#f8f8f8] rounded-lg p-2.5 mb-2 border-l-[3px] border-[#ff8a65] hover:-translate-y-0.5 hover:shadow-sm transition-all"
            >
              <div class="text-[0.78rem] font-semibold text-[#2a2a2a] mb-1">
                Balanço anual — Cliente C
              </div>
              <div class="text-[0.68rem] text-gray-500">85% concluído</div>
              <div
                class="inline-block bg-[#eaf3ea] text-[#19341a] rounded px-1.5 py-0.5 text-[0.65rem] font-bold mt-1.5"
              >
                Contábil
              </div>
            </div>
          </div>
          <!-- Coluna Concluído -->
          <div>
            <div
              class="text-[0.72rem] font-bold tracking-wider uppercase text-gray-500 mb-2.5 pb-2 border-b-2 border-gray-200"
            >
              Concluído
            </div>
            <div
              class="bg-[#f8f8f8] rounded-lg p-2.5 mb-2 border-l-[3px] border-gray-400 hover:-translate-y-0.5 hover:shadow-sm transition-all"
            >
              <div class="text-[0.78rem] font-semibold text-[#2a2a2a] mb-1">
                ECF 2024 — 5 clientes
              </div>
              <div class="text-[0.68rem] text-gray-500">Enviado em 12/06</div>
              <div
                class="inline-block bg-[#eaf3ea] text-[#19341a] rounded px-1.5 py-0.5 text-[0.65rem] font-bold mt-1.5"
              >
                IRPJ
              </div>
            </div>
            <div
              class="bg-[#f8f8f8] rounded-lg p-2.5 mb-2 border-l-[3px] border-gray-400 hover:-translate-y-0.5 hover:shadow-sm transition-all"
            >
              <div class="text-[0.78rem] font-semibold text-[#2a2a2a] mb-1">PGDAS-D — Maio</div>
              <div class="text-[0.68rem] text-gray-500">Enviado em 08/06</div>
              <div
                class="inline-block bg-[#eaf3ea] text-[#19341a] rounded px-1.5 py-0.5 text-[0.65rem] font-bold mt-1.5"
              >
                Simples
              </div>
            </div>
            <div
              class="bg-[#f8f8f8] rounded-lg p-2.5 mb-2 border-l-[3px] border-gray-400 hover:-translate-y-0.5 hover:shadow-sm transition-all"
            >
              <div class="text-[0.78rem] font-semibold text-[#2a2a2a] mb-1">RAIS — Cliente D</div>
              <div class="text-[0.68rem] text-gray-500">Enviado em 01/06</div>
              <div
                class="inline-block bg-[#eaf3ea] text-[#19341a] rounded px-1.5 py-0.5 text-[0.65rem] font-bold mt-1.5"
              >
                Trabalhista
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- STRIP -->
    <div class="bg-[#19341a] text-white py-3.5 px-[5%] text-center text-[0.9rem] font-medium">
      🔒 Gerencie Prazos &nbsp;·&nbsp;
      <strong class="text-[#ff8a65]">Entregas e clientes alinhados</strong>
      &nbsp;·&nbsp; Organização sem complicações
    </div>

    <!-- FEATURES -->
    <section id="features" class="max-w-[1100px] mx-auto py-20 px-[5%]">
      <div v-fade-in class="fade-in">
        <div class="text-[0.78rem] font-bold tracking-wider uppercase text-[#ff8a65] mb-2.5">
          Funcionalidades
        </div>
        <h2 class="text-3xl lg:text-4xl font-extrabold text-[#19341a] leading-tight mb-3.5">
          Tudo que seu escritório precisa,<br />sem a complexidade que não precisa.
        </h2>
        <p class="text-[1rem] text-gray-500 max-w-[520px] mb-12">
          Desenvolvido com contadores, para contadores. Cada detalhe pensado para o dia a dia real
          de um escritório contábil.
        </p>
      </div>
      <div class="grid md:grid-cols-3 gap-6">
        <div
          v-fade-in
          class="fade-in bg-white border border-gray-200 rounded-[14px] p-7 hover:shadow-[0_8px_28px_rgba(25,52,26,0.09)] hover:-translate-y-1 transition-all"
          v-for="f in features"
          :key="f.title"
        >
          <div
            class="w-11 h-11 rounded-xl bg-[#eaf3ea] flex items-center justify-center mb-4 text-xl"
          >
            {{ f.icon }}
          </div>
          <h3 class="text-[1rem] font-bold text-[#19341a] mb-2">{{ f.title }}</h3>
          <p class="text-[0.88rem] text-gray-500 leading-relaxed">{{ f.desc }}</p>
        </div>
      </div>
    </section>

    <!-- HOW IT WORKS -->
    <section id="how" class="bg-[#19341a] text-white py-20 px-[5%]">
      <div class="max-w-[1100px] mx-auto">
        <div class="text-[0.78rem] font-bold tracking-wider uppercase text-[#ff8a65] mb-2.5">
          Como funciona
        </div>
        <h2 class="text-3xl lg:text-4xl font-extrabold text-white leading-tight mb-12">
          Do cadastro à entrega<br />em três passos.
        </h2>
        <div class="grid md:grid-cols-3 gap-8">
          <div v-fade-in class="fade-in relative" v-for="(s, i) in steps" :key="s.title">
            <div class="text-5xl font-extrabold text-white/10 leading-none mb-3">0{{ i + 1 }}</div>
            <h3 class="text-[1rem] font-bold mb-2 text-white">{{ s.title }}</h3>
            <p class="text-[0.88rem] text-white/65 leading-relaxed">{{ s.desc }}</p>
            <span
              class="absolute top-6 right-[-16px] text-xl text-[#ff8a65]/50 hidden md:block"
              v-if="i < steps.length - 1"
              >→</span
            >
          </div>
        </div>
      </div>
    </section>

    <!-- TESTIMONIALS -->
    <section class="max-w-[1100px] mx-auto py-20 px-[5%]">
      <div v-fade-in class="fade-in">
        <div class="text-[0.78rem] font-bold tracking-wider uppercase text-[#ff8a65] mb-2.5">
          Depoimentos
        </div>
        <h2 class="text-3xl lg:text-4xl font-extrabold text-[#19341a] leading-tight">
          Escritórios que transformaram<br />sua rotina com o Contably Task.
        </h2>
      </div>
      <div class="grid md:grid-cols-3 gap-6 mt-12">
        <div
          v-fade-in
          class="fade-in bg-white border border-gray-200 rounded-[14px] p-7"
          v-for="t in testimonials"
          :key="t.name"
        >
          <div class="text-[#ff8a65] text-[0.9rem] mb-3.5">★★★★★</div>
          <p class="text-[0.9rem] text-[#2a2a2a] leading-relaxed mb-5">"{{ t.text }}"</p>
          <div class="flex items-center gap-2.5">
            <div
              class="w-9.5 h-9.5 rounded-full bg-[#19341a] text-white text-[0.8rem] font-bold flex items-center justify-center"
            >
              {{ t.initials }}
            </div>
            <div>
              <div class="text-[0.85rem] font-bold text-[#2a2a2a]">{{ t.name }}</div>
              <div class="text-[0.75rem] text-gray-500">{{ t.role }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- PRICING -->
    <section id="pricing" class="bg-[#eaf3ea] py-20 px-[5%]">
      <div class="max-w-[1100px] mx-auto">
        <div v-fade-in class="fade-in">
          <div class="text-[0.78rem] font-bold tracking-wider uppercase text-[#ff8a65] mb-2.5">
            Planos
          </div>
          <h2 class="text-3xl lg:text-4xl font-extrabold text-[#19341a] leading-tight mb-3.5">
            Simples, transparente,<br />sem surpresas.
          </h2>
          <p class="text-[1rem] text-gray-500 max-w-[520px]">
            Cancele quando quiser. Sem taxas escondidas.
          </p>
        </div>
        <div class="grid md:grid-cols-4 gap-6 mt-12">
          <div
            v-fade-in
            class="fade-in bg-white border border-gray-200 rounded-2xl p-8 relative"
            v-for="p in plans"
            :key="p.name"
            :class="{ 'border-[#ff8a65] shadow-[0_8px_32px_rgba(255,138,101,0.18)]': p.featured }"
          >
            <div
              v-if="p.featured"
              class="absolute top-[-12px] left-1/2 -translate-x-1/2 bg-[#ff8a65] text-white rounded-full py-1 px-4 text-[0.72rem] font-bold whitespace-nowrap"
            >
              Mais popular
            </div>
            <div class="text-[0.85rem] font-bold uppercase tracking-wider text-gray-500 mb-2">
              {{ p.name }}
            </div>
            <div class="text-4xl font-extrabold text-[#19341a] leading-none">
              R$ {{ p.price }}<sub class="text-[0.9rem] font-medium text-gray-500">/mês</sub>
            </div>
            <div class="text-[0.83rem] text-gray-500 mt-2.5 mb-6">{{ p.desc }}</div>
            <ul class="mb-7 space-y-1.5">
              <li
                class="text-[0.86rem] text-[#2a2a2a] flex items-start gap-2"
                v-for="f in p.features"
                :key="f"
              >
                <span class="text-[#ff8a65] font-bold">✓</span> {{ f }}
              </li>
            </ul>
            <button
              @click="scrollTo('cta')"
              class="w-full border-none rounded-[10px] py-3 font-bold text-[0.9rem] cursor-pointer transition-colors"
              :class="
                p.featured
                  ? 'bg-[#ff8a65] text-white hover:bg-[#f07047]'
                  : 'bg-transparent text-[#19341a] border-2 border-[#19341a] hover:bg-[#19341a] hover:text-white'
              "
            >
              {{ p.cta }}
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA FINAL -->
    <section id="cta" class="py-20 px-[5%] text-center">
      <div v-fade-in class="fade-in max-w-[640px] mx-auto">
        <div class="text-[0.78rem] font-bold tracking-wider uppercase text-[#ff8a65] mb-2.5">
          Comece agora
        </div>
        <h2 class="text-3xl lg:text-4xl font-extrabold text-[#19341a] leading-tight mb-4">
          Sua equipe merece uma gestão à altura do seu trabalho.
        </h2>
        <p class="text-gray-500 mb-9 text-[1rem]">
          Crie sua conta em menos de 2 minutos. Nenhum cartão de crédito necessário.
        </p>
        <div class="flex flex-col sm:flex-row gap-2.5 max-w-[480px] mx-auto">
          <input
            type="email"
            v-model="email"
            placeholder="seu@email.com.br"
            class="flex-1 py-3 px-4 border-[1.5px] border-gray-200 rounded-[10px] text-[0.9rem] bg-white text-[#2a2a2a] outline-none focus:border-[#ff8a65] transition-colors"
          />
          <button
            @click="handleCTA"
            class="bg-[#ff8a65] text-white border-none rounded-[10px] py-3 px-6 font-bold text-[0.95rem] cursor-pointer shadow-[0_4px_14px_rgba(255,138,101,0.35)] hover:bg-[#f07047] hover:-translate-y-0.5 transition-all"
          >
            Começar grátis
          </button>
        </div>
        <p
          class="text-[0.78rem] text-gray-500 mt-3.5"
          v-if="ctaMsg"
          style="color: #ff8a65; font-weight: 600"
        >
          {{ ctaMsg }}
        </p>
        <p class="text-[0.78rem] text-gray-500 mt-3.5" v-else>
          7 dias gratuitos · Sem cartão de crédito · Suporte em português
        </p>
      </div>
    </section>

    <!-- FOOTER -->
    <footer
      class="bg-[#19341a] text-white/60 py-8 px-[5%] flex flex-col md:flex-row items-center justify-between gap-4 flex-wrap"
    >
      <div>
        <span class="text-[0.95rem] font-bold text-white"
          >Contably <span class="text-[#ff8a65]">Task</span></span
        >
        <p class="text-[0.82rem] mt-1">© 2026 ContablyTask. Todos os direitos reservados.</p>
      </div>
      <div class="flex gap-5">
        <a
          href="./PrivacidadeView.vue"
          class="text-[0.82rem] text-white/50 hover:text-white transition-colors"
          >Privacidade</a
        >
        <a
          href="./TermosView.vue"
          class="text-[0.82rem] text-white/50 hover:text-white transition-colors"
          >Termos</a
        >
        <a href="#" class="text-[0.82rem] text-white/50 hover:text-white transition-colors"
          >Contato</a
        >
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* Animação Fade-in controlada pela Diretiva v-fade-in */
.fade-in {
  opacity: 0;
  transform: translateY(18px);
  transition:
    opacity 0.5s ease-out,
    transform 0.5s ease-out;
}
.fade-in.visible {
  opacity: 1;
  transform: translateY(0);
}

/* Animação customizada do card "DCTF Web" no Task Board */
@keyframes pulse-border {
  0%,
  100% {
    box-shadow: 0 0 0 0 rgba(255, 138, 101, 0);
  }
  50% {
    box-shadow: 0 0 0 4px rgba(255, 138, 101, 0.25);
  }
}
.animate-pulse-border {
  animation: pulse-border 2s ease-in-out infinite;
}

/* Scroll suave global para os links âncora */
html {
  scroll-behavior: smooth;
}
</style>
