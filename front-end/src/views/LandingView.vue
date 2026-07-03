<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

const email = ref('')
const ctaMsg = ref('')

const features = [
  {
    icon: '📅',
    title: 'Calendário inteligente',
    desc: 'Visualize os principais vencimentos fiscais em um só lugar. Alertas automáticos para reduzir o risco de multas.',
  },
  {
    icon: '👥',
    title: 'Gestão por cliente',
    desc: 'Centralize tarefas, documentos e histórico. Saiba exatamente o que está pendente para cada CNPJ em segundos.',
  },
  {
    icon: '📊',
    title: 'Produtividade real',
    desc: 'Métricas claras do seu escritório: gargalos da equipe, tarefas concluídas e prazos em risco.',
  },
  {
    icon: '🔔',
    title: 'Alertas de prazo',
    desc: 'Receba notificações com antecedência para obrigações-chave. Planeje sua agenda sem surpresas.',
  },
  {
    icon: '📎',
    title: 'Documentos centralizados',
    desc: 'Anexe XMLs, planilhas e comprovantes diretamente nas tarefas. Adeus pastas espalhadas no computador.',
  },
  {
    icon: '🤝',
    title: 'Colaboração em equipe',
    desc: 'Delegue obrigações com um clique. Acompanhe o status em tempo real sem precisar interromper a equipe.',
  },
]

const steps = [
  {
    title: 'Centralize seus clientes',
    desc: 'Importe sua base em minutos via CSV ou manualmente. Vincule obrigações fiscais a cada empresa.',
  },
  {
    title: 'Organize o caos',
    desc: 'Use tags de Comércio ou Serviços. Defina prioridades, atribua responsáveis e acompanhe o progresso.',
  },
  {
    title: 'Entregue com precisão',
    desc: 'Comprove o trabalho realizado, mantenha o histórico organizado e ganhe a confiança dos seus clientes.',
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
    text: 'O dashboard de obrigações salvou meu escritório. Zerou os atrasos que eu tinha com o eSocial e a Receita Federal dos meus clientes.',
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
    name: 'Free',
    price: '0',
    featured: false,
    desc: 'Para testar a plataforma.',
    cta: 'Começar Grátis',
    features: [
      'Até 5 clientes',
      '1 usuário (Admin)',
      'Calendário de obrigações',
      'Gestão de documentos',
      'Suporte por e-mail',
    ],
  },
  {
    name: 'Básico',
    price: '149',
    featured: false,
    desc: 'Para contadores autônomos.',
    cta: 'Assinar Básico',
    features: [
      'Até 40 clientes',
      'Até 5 usuários',
      'Tudo do Free',
      'Alertas por e-mail',
      'Suporte por chat',
    ],
  },
  {
    name: 'Profissional',
    price: '197',
    featured: true,
    desc: 'Para escritórios em crescimento.',
    cta: 'Assinar Profissional',
    features: [
      'Até 100 clientes',
      'Até 10 usuários',
      'Tudo do Básico',
      'Distribuição de equipe',
      'Relatórios avançados',
      'Suporte prioritário',
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

// Diretiva customizada para o Fade-in ao rolar
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
  <div class="bg-white text-[#2a2a2a] antialiased font-sans overflow-x-hidden">
    <!-- NAV (Glassmorphism moderno) -->
    <nav
      class="sticky top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-gray-100 h-16 flex items-center justify-between px-[5%] transition-shadow"
    >
      <div class="flex items-center gap-2.5">
        <div class="w-9 h-9 rounded-[10px] bg-[#19341a] flex items-center justify-center shadow-sm">
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
        <span class="text-[1.1rem] font-bold text-[#19341a] tracking-tight">
          Contably<span class="text-[#ff8a65]"> Task</span>
        </span>
      </div>
      <div class="hidden md:flex items-center gap-8">
        <a
          href="#features"
          class="text-[0.92rem] font-medium text-gray-600 hover:text-[#19341a] transition-colors"
          >Funcionalidades</a
        >
        <a
          href="#how"
          class="text-[0.92rem] font-medium text-gray-600 hover:text-[#19341a] transition-colors"
          >Como funciona</a
        >
        <a
          href="#pricing"
          class="text-[0.92rem] font-medium text-gray-600 hover:text-[#19341a] transition-colors"
          >Planos</a
        >
        <RouterLink
          to="/login"
          class="inline-flex items-center bg-transparent text-[#19341a] border border-gray-200 rounded-lg py-2 px-5 font-semibold text-[0.9rem] cursor-pointer hover:bg-gray-50 transition-all"
        >
          Login
        </RouterLink>
        <RouterLink
          to="/cadastro"
          class="inline-flex items-center bg-[#ff8a65] text-white border-none rounded-lg py-2 px-5 font-semibold text-[0.9rem] cursor-pointer hover:bg-[#f07047] hover:shadow-lg hover:shadow-[#ff8a65]/30 transition-all"
        >
          Começar grátis
        </RouterLink>
      </div>
    </nav>

    <!-- HERO -->
    <section
      class="relative max-w-[1200px] mx-auto pt-24 pb-20 px-[5%] md:grid md:grid-cols-2 md:gap-12 items-center"
    >
      <!-- Fundo Grid Sutil -->
      <div
        class="absolute inset-0 bg-[linear-gradient(to_right,#80808008_1px,transparent_1px),linear-gradient(to_bottom,#80808008_1px,transparent_1px)] bg-[size:32px_32px] z-[-1]"
      ></div>

      <div v-fade-in class="fade-in">
        <div
          class="inline-flex items-center gap-2 bg-[#eaf3ea] text-[#19341a] rounded-full py-1.5 px-4 text-[0.8rem] font-semibold tracking-wide mb-6 border border-[#19341a]/10"
        >
          <span class="w-1.5 h-1.5 rounded-full bg-[#ff8a65]"></span> Feito para escritórios
          contábeis e contadores autônomos
        </div>
        <h1
          class="text-4xl lg:text-[3.5rem] font-extrabold text-[#19341a] leading-[1.1] tracking-tight mb-6"
        >
          Organize seu escritório.<br />Entregue com
          <span class="text-[#ff8a65]">precisão.</span>
        </h1>
        <p class="text-[1.1rem] text-gray-500 max-w-[520px] mb-9 leading-relaxed">
          Gestão de tarefas e prazos para escritórios contábeis e contadores autônomos. Centralize
          clientes, obrigações fiscais e documentos. Acabe com o caos das planilhas e garanta a
          conformidade do seu escritório sem perder prazos.
        </p>
        <div class="flex gap-4 flex-wrap">
          <RouterLink
            to="/cadastro"
            class="inline-flex items-center bg-[#ff8a65] text-white border-none rounded-lg py-3 px-6 font-semibold text-[0.95rem] cursor-pointer hover:bg-[#f07047] hover:shadow-xl hover:shadow-[#ff8a65]/30 hover:-translate-y-0.5 transition-all"
          >
            Criar conta grátis
          </RouterLink>
          <button
            @click="scrollTo('how')"
            class="inline-flex items-center bg-transparent text-[#19341a] border-2 border-gray-200 rounded-lg py-3 px-6 font-semibold text-[0.95rem] cursor-pointer hover:border-[#19341a] hover:bg-white transition-colors"
          >
            Ver como funciona
          </button>
        </div>

        <!-- Selos de Confiança -->
        <div class="mt-10 flex items-center gap-6 text-gray-400">
          <div class="flex items-center gap-2 text-xs font-medium">
            <svg
              class="w-5 h-5 text-[#19341a]"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
              ></path>
            </svg>
            Criptografia em trânsito (HTTPS)
          </div>
          <div class="flex items-center gap-2 text-xs font-medium">
            <svg
              class="w-5 h-5 text-[#19341a]"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"
              ></path>
            </svg>
            Pensado para atender à LGPD
          </div>
        </div>
      </div>

      <!-- TASK BOARD (Mockup Refinado) -->
      <div
        v-fade-in
        class="fade-in bg-white rounded-2xl border border-gray-100 shadow-[0_25px_60px_-15px_rgba(25,52,26,0.15)] p-6 mt-12 md:mt-0 hidden sm:block"
      >
        <div class="flex items-center justify-between mb-5 border-b border-gray-100 pb-3">
          <span class="text-[0.9rem] font-bold text-[#19341a]">Visão Geral — Junho 2025</span>
          <div class="flex gap-1.5">
            <span class="w-2.5 h-2.5 rounded-full bg-[#ff8a65]"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-gray-200"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-gray-200"></span>
          </div>
        </div>
        <div class="grid grid-cols-3 gap-3">
          <!-- Coluna A Fazer -->
          <div class="bg-[#f8f8f8] rounded-xl p-2.5 space-y-2.5">
            <div class="text-[0.7rem] font-bold tracking-wider uppercase text-gray-400 px-1 pb-1.5">
              A fazer
            </div>
            <div class="bg-white rounded-lg p-2.5 border border-gray-100 shadow-sm">
              <div class="text-[0.75rem] font-semibold text-[#2a2a2a] mb-1">
                SPED Fiscal — Cliente A
              </div>
              <div class="text-[0.65rem] text-gray-400 mb-2">Vence 20/06</div>
              <div
                class="inline-block bg-[#eaf3ea] text-[#19341a] rounded px-1.5 py-0.5 text-[0.6rem] font-bold"
              >
                Fiscal
              </div>
            </div>
            <div
              class="bg-white rounded-lg p-2.5 border border-gray-100 shadow-sm border-l-[3px] border-l-[#ff8a65]"
            >
              <div class="text-[0.75rem] font-semibold text-[#2a2a2a] mb-1">Folha de pagamento</div>
              <div class="text-[0.65rem] text-gray-400 mb-2">Vence 18/06</div>
              <div
                class="inline-block bg-[#fff3e0] text-[#e65100] rounded px-1.5 py-0.5 text-[0.6rem] font-bold"
              >
                Urgente
              </div>
            </div>
          </div>
          <!-- Coluna Em andamento -->
          <div class="bg-[#f8f8f8] rounded-xl p-2.5 space-y-2.5">
            <div class="text-[0.7rem] font-bold tracking-wider uppercase text-gray-400 px-1 pb-1.5">
              Em andamento
            </div>
            <div
              class="bg-white rounded-lg p-2.5 border border-gray-100 shadow-sm animate-pulse-border"
            >
              <div class="text-[0.75rem] font-semibold text-[#2a2a2a] mb-1">
                DCTF Web — Cliente B
              </div>
              <div class="text-[0.65rem] text-gray-400 mb-2">Atribuído: Ana</div>
              <div
                class="inline-block bg-[#eaf3ea] text-[#19341a] rounded px-1.5 py-0.5 text-[0.6rem] font-bold"
              >
                eSocial
              </div>
            </div>
            <div class="bg-white rounded-lg p-2.5 border border-gray-100 shadow-sm">
              <div class="text-[0.75rem] font-semibold text-[#2a2a2a] mb-1">Balanço anual — C</div>
              <div class="text-[0.65rem] text-gray-400 mb-2">85% concluído</div>
              <div
                class="inline-block bg-[#eaf3ea] text-[#19341a] rounded px-1.5 py-0.5 text-[0.6rem] font-bold"
              >
                Contábil
              </div>
            </div>
          </div>
          <!-- Coluna Concluído -->
          <div class="bg-[#f8f8f8] rounded-xl p-2.5 space-y-2.5">
            <div class="text-[0.7rem] font-bold tracking-wider uppercase text-gray-400 px-1 pb-1.5">
              Concluído
            </div>
            <div class="bg-white rounded-lg p-2.5 border border-gray-100 shadow-sm opacity-60">
              <div class="text-[0.75rem] font-semibold text-[#2a2a2a] mb-1">
                ECF 2024 — 5 clientes
              </div>
              <div class="text-[0.65rem] text-gray-400 mb-2">Enviado em 12/06</div>
              <div
                class="inline-block bg-[#eaf3ea] text-[#19341a] rounded px-1.5 py-0.5 text-[0.6rem] font-bold"
              >
                IRPJ
              </div>
            </div>
            <div class="bg-white rounded-lg p-2.5 border border-gray-100 shadow-sm opacity-60">
              <div class="text-[0.75rem] font-semibold text-[#2a2a2a] mb-1">PGDAS-D — Maio</div>
              <div class="text-[0.65rem] text-gray-400 mb-2">Enviado em 08/06</div>
              <div
                class="inline-block bg-[#eaf3ea] text-[#19341a] rounded px-1.5 py-0.5 text-[0.6rem] font-bold"
              >
                Simples
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- STRIP DE SEGURANÇA -->
    <div
      class="bg-[#19341a] text-white py-4 px-[5%] text-center text-[0.9rem] font-medium flex flex-wrap justify-center items-center gap-x-6 gap-y-2"
    >
      <span class="flex items-center gap-2"
        ><svg class="w-4 h-4 text-[#ff8a65]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
          />
        </svg>
        Criptografia em trânsito (HTTPS)</span
      >
      <span class="hidden md:inline text-white/20">·</span>
      <span class="flex items-center gap-2"
        ><svg class="w-4 h-4 text-[#ff8a65]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
          />
        </svg>
        Pensado para atender à LGPD</span
      >
      <span class="hidden md:inline text-white/20">·</span>
      <span class="flex items-center gap-2"
        ><svg class="w-4 h-4 text-[#ff8a65]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M5 13l4 4L19 7"
          ></path>
        </svg>
        Infraestrutura em nuvem segura</span
      >
    </div>

    <!-- FEATURES -->
    <section id="features" class="max-w-[1200px] mx-auto py-24 px-[5%]">
      <div v-fade-in class="fade-in text-center mb-16">
        <div class="text-[0.8rem] font-bold tracking-wider uppercase text-[#ff8a65] mb-3">
          Funcionalidades
        </div>
        <h2
          class="text-3xl lg:text-[2.6rem] font-extrabold text-[#19341a] leading-tight mb-4 tracking-tight"
        >
          Tudo que seu escritório precisa.<br />Sem a complexidade que não precisa.
        </h2>
        <p class="text-[1.1rem] text-gray-500 max-w-[600px] mx-auto">
          Desenvolvido lado a lado com contadores. Cada detalhe pensado para o dia a dia real de um
          escritório contábil.
        </p>
        <p class="text-[0.95rem] text-gray-400 max-w-[600px] mx-auto mt-3">
          Feito para escritórios contábeis e contadores autônomos que querem organizar tarefas e
          prazos sem substituir o sistema fiscal atual.
        </p>
      </div>
      <div class="grid md:grid-cols-3 gap-8">
        <div
          v-fade-in
          class="fade-in bg-white border border-gray-100 rounded-2xl p-8 hover:shadow-[0_15px_40px_rgba(25,52,26,0.07)] hover:-translate-y-1.5 transition-all duration-300"
          v-for="f in features"
          :key="f.title"
        >
          <div
            class="w-12 h-12 rounded-xl bg-[#eaf3ea] flex items-center justify-center mb-5 text-2xl"
          >
            {{ f.icon }}
          </div>
          <h3 class="text-[1.15rem] font-bold text-[#19341a] mb-2.5">{{ f.title }}</h3>
          <p class="text-[0.95rem] text-gray-500 leading-relaxed">{{ f.desc }}</p>
        </div>
      </div>
    </section>

    <!-- HOW IT WORKS (Dark Section) -->
    <section id="how" class="bg-[#19341a] text-white py-24 px-[5%] relative overflow-hidden">
      <!-- Efeito de luz no fundo -->
      <div
        class="absolute top-0 left-1/4 w-96 h-96 bg-[#ff8a65]/10 rounded-full blur-[120px]"
      ></div>

      <div class="max-w-[1200px] mx-auto relative z-10">
        <div class="text-[0.8rem] font-bold tracking-wider uppercase text-[#ff8a65] mb-3">
          Como funciona
        </div>
        <h2
          class="text-3xl lg:text-[2.6rem] font-extrabold text-white leading-tight mb-6 tracking-tight"
        >
          Do cadastro à entrega<br />em três passos.
        </h2>
        <p class="text-[1rem] text-white/70 max-w-[560px] mb-10">
          Você não precisa trocar seu ERP ou sistema fiscal: o Contably Task organiza tarefas,
          prazos e documentos em torno do que você já usa.
        </p>
        <div class="grid md:grid-cols-3 gap-12">
          <div v-fade-in class="fade-in relative" v-for="(s, i) in steps" :key="s.title">
            <div
              class="text-6xl font-extrabold text-white/5 leading-none mb-4 absolute -top-8 -left-2"
            >
              0{{ i + 1 }}
            </div>
            <div class="relative z-10">
              <h3 class="text-[1.2rem] font-bold mb-3 text-white">{{ s.title }}</h3>
              <p class="text-[0.95rem] text-white/60 leading-relaxed">{{ s.desc }}</p>
            </div>
            <span
              class="absolute top-6 right-[-24px] text-2xl text-[#ff8a65]/30 hidden md:block font-light"
              v-if="i < steps.length - 1"
              >→</span
            >
          </div>
        </div>
      </div>
    </section>

    <!-- TESTIMONIALS -->
    <section class="max-w-[1200px] mx-auto py-24 px-[5%]">
      <div v-fade-in class="fade-in text-center mb-16">
        <div class="text-[0.8rem] font-bold tracking-wider uppercase text-[#ff8a65] mb-3">
          Depoimentos
        </div>
        <h2
          class="text-3xl lg:text-[2.6rem] font-extrabold text-[#19341a] leading-tight tracking-tight"
        >
          Escritórios que transformaram<br />sua rotina conosco.
        </h2>
      </div>
      <div class="grid md:grid-cols-3 gap-8">
        <div
          v-fade-in
          class="fade-in bg-[#f8f8f8] rounded-2xl p-8 border border-gray-100"
          v-for="t in testimonials"
          :key="t.name"
        >
          <svg class="w-8 h-8 text-[#ff8a65]/30 mb-4" fill="currentColor" viewBox="0 0 24 24">
            <path
              d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z"
            />
          </svg>
          <p class="text-[0.95rem] text-[#2a2a2a] leading-relaxed mb-6 italic">"{{ t.text }}"</p>
          <div class="flex items-center gap-3 pt-4 border-t border-gray-200">
            <div
              class="w-10 h-10 rounded-full bg-[#19341a] text-white text-[0.85rem] font-bold flex items-center justify-center"
            >
              {{ t.initials }}
            </div>
            <div>
              <div class="text-[0.9rem] font-bold text-[#19341a]">{{ t.name }}</div>
              <div class="text-[0.8rem] text-gray-500">{{ t.role }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- PRICING -->
    <section id="pricing" class="bg-[#f8f8f8] py-24 px-[5%] border-y border-gray-100">
      <div class="max-w-[1200px] mx-auto">
        <div v-fade-in class="fade-in text-center mb-16">
          <div class="text-[0.8rem] font-bold tracking-wider uppercase text-[#ff8a65] mb-3">
            Planos
          </div>
          <h2
            class="text-3xl lg:text-[2.6rem] font-extrabold text-[#19341a] leading-tight mb-4 tracking-tight"
          >
            Comece de graça. Evolua quando precisar.
          </h2>
          <p class="text-[1.1rem] text-gray-500 max-w-[500px] mx-auto">
            Sem cartão de crédito para começar. Cancele quando quiser.
          </p>
        </div>
        <div class="grid md:grid-cols-4 gap-6 items-start">
          <div
            v-fade-in
            class="fade-in bg-white border border-gray-100 rounded-2xl p-8 relative transition-all duration-300 hover:shadow-lg"
            v-for="p in plans"
            :key="p.name"
            :class="{
              'md:scale-110 shadow-[0_20px_50px_rgba(25,52,26,0.1)] border-[#ff8a65] z-10':
                p.featured,
            }"
          >
            <div
              v-if="p.featured"
              class="absolute top-[-14px] left-1/2 -translate-x-1/2 bg-[#ff8a65] text-white rounded-full py-1.5 px-5 text-[0.75rem] font-bold whitespace-nowrap shadow-md shadow-[#ff8a65]/40"
            >
              Mais popular
            </div>
            <div class="text-[0.85rem] font-bold uppercase tracking-wider text-gray-400 mb-3">
              {{ p.name }}
            </div>
            <div class="flex items-end gap-1 mb-1">
              <span class="text-2xl font-bold text-gray-400 mb-1">R$</span>
              <span class="text-4xl font-extrabold text-[#19341a] leading-none">{{ p.price }}</span>
            </div>
            <div class="text-[0.85rem] text-gray-400 font-medium mb-6">/mês</div>

            <div class="text-[0.85rem] text-gray-500 mt-2 mb-6 min-h-[40px]">{{ p.desc }}</div>

            <ul class="mb-8 space-y-3 border-t border-gray-100 pt-6">
              <li
                class="text-[0.9rem] text-[#2a2a2a] flex items-start gap-2.5"
                v-for="f in p.features"
                :key="f"
              >
                <svg
                  class="w-4 h-4 text-[#ff8a65] mt-0.5 flex-shrink-0"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="3"
                    d="M5 13l4 4L19 7"
                  ></path>
                </svg>
                {{ f }}
              </li>
            </ul>
            <RouterLink
              to="/cadastro"
              class="w-full inline-flex justify-center items-center rounded-xl py-3 font-bold text-[0.95rem] cursor-pointer transition-all duration-300"
              :class="
                p.featured
                  ? 'bg-[#ff8a65] text-white hover:bg-[#f07047] shadow-lg shadow-[#ff8a65]/30'
                  : 'bg-transparent text-[#19341a] border-2 border-gray-200 hover:border-[#19341a] hover:bg-white'
              "
            >
              {{ p.cta }}
            </RouterLink>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA FINAL -->
    <section id="cta" class="py-28 px-[5%] text-center relative overflow-hidden">
      <div
        class="absolute inset-0 bg-[linear-gradient(to_right,#80808008_1px,transparent_1px),linear-gradient(to_bottom,#80808008_1px,transparent_1px)] bg-[size:32px_32px] z-[-1]"
      ></div>
      <div v-fade-in class="fade-in max-w-[640px] mx-auto">
        <h2
          class="text-3xl lg:text-[2.8rem] font-extrabold text-[#19341a] leading-tight mb-5 tracking-tight"
        >
          Sua equipe merece uma gestão à altura do seu trabalho.
        </h2>
        <p class="text-gray-500 mb-10 text-[1.1rem]">
          Crie sua conta gratuita em menos de 2 minutos. Sem cartão de crédito.
        </p>
        <div class="flex flex-col sm:flex-row gap-3 max-w-[500px] mx-auto">
          <input
            type="email"
            v-model="email"
            placeholder="seu@email.com.br"
            class="flex-1 py-3.5 px-5 border border-gray-200 rounded-xl text-[0.95rem] bg-white text-[#2a2a2a] outline-none focus:border-[#ff8a65] focus:ring-2 focus:ring-[#ff8a65]/20 transition-all"
          />
          <RouterLink
            to="/cadastro"
            class="bg-[#ff8a65] text-white border-none rounded-xl py-3.5 px-7 font-bold text-[0.95rem] cursor-pointer shadow-lg shadow-[#ff8a65]/30 hover:bg-[#f07047] hover:-translate-y-0.5 transition-all whitespace-nowrap inline-flex justify-center items-center"
          >
            Criar conta grátis
          </RouterLink>
        </div>
        <p class="text-[0.85rem] mt-4 font-semibold" v-if="ctaMsg" style="color: #19341a">
          {{ ctaMsg }}
        </p>
        <p class="text-[0.85rem] text-gray-400 mt-4" v-else>
          Plano gratuito para sempre · Sem cartão de crédito · Suporte humano em português
        </p>
      </div>
    </section>

    <!-- FOOTER -->
    <footer
      class="bg-[#19341a] text-white/60 py-10 px-[5%] flex flex-col md:flex-row items-center justify-between gap-6 flex-wrap"
    >
      <div>
        <span class="text-[1.1rem] font-bold text-white tracking-tight">
          Contably<span class="text-[#ff8a65]"> Task</span>
        </span>
        <p class="text-[0.82rem] mt-2">© 2026 Contably Task. Todos os direitos reservados.</p>
      </div>
      <div class="flex gap-8">
        <a href="#" class="text-[0.85rem] text-white/50 hover:text-white transition-colors"
          >Privacidade</a
        >
        <a href="#" class="text-[0.85rem] text-white/50 hover:text-white transition-colors"
          >Termos</a
        >
        <a href="#" class="text-[0.85rem] text-white/50 hover:text-white transition-colors"
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
  transform: translateY(20px);
  transition:
    opacity 0.6s ease-out,
    transform 0.6s ease-out;
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
    box-shadow: 0 0 0 4px rgba(255, 138, 101, 0.2);
  }
}
.animate-pulse-border {
  animation: pulse-border 2.5s ease-in-out infinite;
}

/* Scroll suave global */
html {
  scroll-behavior: smooth;
}
</style>
