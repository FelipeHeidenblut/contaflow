<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

const router = useRouter()
const email = ref('')

const stats = [
  { label: 'Clientes em um só lugar', value: '1 painel', desc: 'Tenha uma visão centralizada de clientes, tarefas, documentos e pendências.' },
  { label: 'Rotina organizada', value: '4 frentes', desc: 'Fiscal, contábil, departamento pessoal e demandas internas na mesma operação.' },
  { label: 'Visão da equipe', value: 'Por pessoa', desc: 'Acompanhe responsáveis, prioridades e carga de trabalho com clareza.' },
  { label: 'Prazos sob controle', value: 'Em tempo real', desc: 'Veja o que vence, está pendente ou precisa de atenção antes que vire urgência.' },
]

const capabilities = [
  {
    id: 'cap-0',
    num: '01',
    tag: 'Calendário',
    title: 'Tudo o que importa, em uma só tela',
    desc: 'Vencimentos federais, estaduais e tarefas internas em um só calendário. O dashboard mostra o que está vencendo, o que atrasou e onde a equipe está focando.',
    mockup: 'calendar',
  },
  {
    id: 'cap-1',
    num: '02',
    tag: 'Workflow',
    title: 'Processos que rodam com mais consistência',
    desc: 'Tarefas recorrentes mensais, como DAS, folha e SPED, podem ser criadas de forma organizada para reduzir trabalho manual repetitivo.',
    mockup: 'workflow',
  },
  {
    id: 'cap-2',
    num: '03',
    tag: 'Clientes',
    title: 'Dossiê do cliente em segundos',
    desc: 'Centralize dados cadastrais, tarefas em aberto, documentos e histórico de cada CNPJ. Saiba exatamente o que está pendente para cada cliente sem abrir planilhas.',
    mockup: 'client',
  },
  {
    id: 'cap-3',
    num: '04',
    tag: 'Documentos',
    title: 'Repositório vivo, não pasta morta',
    desc: 'Anexe XMLs, planilhas e comprovantes diretamente às tarefas. Organize documentos por tipo e encontre o que precisa com mais rapidez.',
    mockup: 'docs',
  },
  {
    id: 'cap-4',
    num: '05',
    tag: 'Equipe',
    title: 'Capacidade que se vê',
    desc: 'Visualize quem está sobrecarregado e quem tem disponibilidade. Distribua o trabalho com base na operação, não em achismos.',
    mockup: 'team',
  },
  {
    id: 'cap-5',
    num: '06',
    tag: 'Integração',
    title: 'Sua agenda, atualizada com menos esforço',
    desc: 'Gere um link .ics e sincronize prazos com Google Agenda e Outlook. Acompanhe obrigações também pelo celular, sem depender de planilhas.',
    mockup: 'sync',
  },
]

const steps = [
  {
    num: '01',
    title: 'Centralize',
    desc: 'Importe sua base de clientes via CSV em poucos minutos e concentre as informações essenciais da operação.',
  },
  {
    num: '02',
    title: 'Organize',
    desc: 'Crie tarefas com templates contábeis, atribua responsáveis e defina prioridades para cada demanda.',
  },
  {
    num: '03',
    title: 'Automatize',
    desc: 'Estruture tarefas recorrentes para reduzir atividades repetitivas e manter a rotina previsível.',
  },
  {
    num: '04',
    title: 'Entregue',
    desc: 'Acompanhe o progresso em tempo real e mantenha um histórico claro por cliente e por tarefa.',
  },
]

const cases = [
  {
    tag: 'Autônomo',
    title: 'Mais clareza para atender e entregar',
    desc: 'Organize a rotina de clientes, demandas e prazos sem depender de múltiplas planilhas e conversas espalhadas.',
    metric: 'Rotina centralizada',
  },
  {
    tag: 'Escritório',
    title: 'Equipe alinhada no mesmo fluxo',
    desc: 'Distribua tarefas, acompanhe responsáveis e reduza a necessidade de cobranças manuais no WhatsApp.',
    metric: 'Visão por responsável',
  },
  {
    tag: 'Crescimento',
    title: 'Uma base para crescer com processo',
    desc: 'Crie uma operação organizada antes de aumentar carteira, equipe e volume de entregas.',
    metric: 'Processos escaláveis',
  },
]

const plans = [
  {
    name: 'Free',
    price: '0',
    desc: 'Para conhecer a plataforma.',
    cta: 'Começar grátis',
    featured: false,
    features: ['Até 5 clientes', '1 usuário administrador', 'Calendário de obrigações', 'Gestão de documentos'],
  },
  {
    name: 'Básico',
    price: '79,90',
    desc: 'Para contadores autônomos.',
    cta: 'Assinar Básico',
    featured: false,
    features: ['Até 40 clientes', 'Até 5 usuários', 'Tudo do Free', 'Alertas por e-mail'],
  },
  {
    name: 'Profissional',
    price: '149,90',
    desc: 'Para escritórios em crescimento.',
    cta: 'Assinar Profissional',
    featured: true,
    features: ['Até 100 clientes', 'Até 10 usuários', 'Tudo do Básico', 'Distribuição de equipe', 'Relatórios avançados'],
  },
  {
    name: 'Business',
    price: '449',
    desc: 'Para operações maiores.',
    cta: 'Falar com vendas',
    featured: false,
    features: ['Clientes ilimitados', 'Usuários ilimitados', 'Tudo do Profissional', 'API e integrações', 'Gerente dedicado'],
  },
]

const handleCTA = () => {
  if (!email.value || !email.value.includes('@')) return

  router.push({
    path: '/cadastro',
    query: { email: email.value },
  })
}

const vFadeIn = {
  mounted(el: HTMLElement) {
    el.style.opacity = '0'
    el.style.transform = 'translateY(20px)'
    el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out'

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            el.style.opacity = '1'
            el.style.transform = 'translateY(0)'
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
  <div class="overflow-x-clip bg-[var(--ct-bg)] font-sans text-[var(--ct-ink)] antialiased">
    <!-- NAV -->
    <header class="sticky top-0 z-50 border-b border-[var(--ct-border)] bg-white/85 backdrop-blur-lg">
      <div class="mx-auto flex h-16 max-w-[1200px] items-center justify-between px-6">
        <a href="/" class="flex items-center gap-2.5">
          <div class="flex h-9 w-9 items-center justify-center rounded-[10px] bg-[var(--ct-navy)]">
            <svg viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.5" class="h-5 w-5">
              <path d="M9 11l3 3L22 4" />
              <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" />
            </svg>
          </div>
          <span class="text-lg font-extrabold tracking-tight">ContablyTask</span>
        </a>

        <nav class="hidden items-center gap-1 lg:flex">
          <a href="/sobre" class="rounded-lg px-3 py-2 text-[15px] font-medium text-[var(--ct-text-muted)] transition-colors hover:text-[var(--ct-ink)]">Sobre Nós</a>
          <a href="/contato" class="rounded-lg px-3 py-2 text-[15px] font-medium text-[var(--ct-text-muted)] transition-colors hover:text-[var(--ct-ink)]">Contato</a>
          <a href="/planos" class="rounded-lg px-3 py-2 text-[15px] font-medium text-[var(--ct-text-muted)] transition-colors hover:text-[var(--ct-ink)]">Planos</a>
          <a href="/como-funciona" class="rounded-lg px-3 py-2 text-[15px] font-medium text-[var(--ct-text-muted)] transition-colors hover:text-[var(--ct-ink)]">Como Funciona</a>
        </nav>

        <div class="flex items-center gap-2">
          <RouterLink to="/login" class="rounded-lg px-3 py-2 text-sm font-medium transition-colors hover:bg-[var(--ct-muted)]">Login</RouterLink>
          <RouterLink to="/cadastro" class="rounded-lg bg-[var(--ct-primary)] px-4 py-2 text-sm font-bold text-white transition-colors hover:bg-[var(--ct-primary-hover)]">Começar grátis</RouterLink>
        </div>
      </div>
    </header>

    <main>
      <!-- HERO -->
      <section class="relative overflow-hidden bg-[var(--ct-navy)] text-white">
        <div class="absolute inset-0 bg-[linear-gradient(to_right,#ffffff08_1px,transparent_1px),linear-gradient(to_bottom,#ffffff08_1px,transparent_1px)] bg-[size:32px_32px] opacity-40"></div>
        <div class="absolute left-1/4 top-0 h-96 w-96 rounded-full bg-[var(--ct-primary)]/25 blur-[120px]"></div>
        <div class="absolute inset-0" style="background: radial-gradient(120% 90% at 50% 30%, transparent 38%, rgba(15, 23, 42, .72) 100%)"></div>

        <div class="relative mx-auto flex max-w-[860px] flex-col items-center px-6 py-28 text-center">
          <span class="mb-6 inline-flex items-center gap-1.5 rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs font-medium backdrop-blur-sm">
            Software para escritórios contábeis
          </span>

          <h1 class="text-[clamp(40px,6vw,76px)] font-semibold leading-[1.03] tracking-[-0.04em]">
            A tecnologia que faz o seu escritório
            <span class="bg-gradient-to-r from-[#60A5FA] to-white bg-clip-text text-transparent">funcionar.</span>
          </h1>

          <p class="mt-6 max-w-[600px] text-[clamp(16px,1.4vw,19px)] leading-relaxed text-white/75">
            Gestão de tarefas, prazos e documentos construída para a rotina contábil brasileira. Centralize clientes, obrigações fiscais e equipe em um só lugar.
          </p>

          <div class="mt-9 flex flex-wrap items-center justify-center gap-3">
            <RouterLink to="/cadastro" class="inline-flex items-center gap-2 rounded-xl bg-[var(--ct-primary)] px-7 py-3.5 text-[15px] font-semibold text-white shadow-lg shadow-blue-950/30 transition-all hover:bg-[var(--ct-primary-hover)]">
              Criar conta grátis
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M13 6l6 6-6 6" /></svg>
            </RouterLink>
            <a href="#metodo" class="inline-flex items-center rounded-xl border border-white/30 px-6 py-3.5 text-[15px] font-semibold text-white transition-all hover:bg-white/10">Como funciona</a>
          </div>
        </div>
      </section>

      <!-- VISÃO DA PLATAFORMA -->
      <section class="relative border-y border-[var(--ct-border)] bg-[var(--ct-bg)]">
        <div class="mx-auto max-w-[1200px] px-6 py-24">
          <div v-fade-in class="mb-12 max-w-[680px]">
            <span class="font-mono text-xs uppercase tracking-[0.12em] text-[var(--ct-primary)]">Visão da plataforma</span>
            <h2 class="mt-3.5 text-[clamp(28px,3vw,40px)] font-bold tracking-[-0.03em] text-[var(--ct-ink)]">Controle da operação, em uma visão clara</h2>
            <p class="mt-4 text-lg text-[var(--ct-text-muted)]">Uma plataforma criada para organizar a rotina de profissionais e escritórios contábeis.</p>
          </div>

          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div v-for="s in stats" :key="s.label" v-fade-in class="relative flex h-full min-h-[220px] flex-col justify-between overflow-hidden rounded-2xl border border-[var(--ct-border)] bg-white p-7 transition-all hover:-translate-y-1 hover:shadow-lg">
              <div class="absolute inset-0 bg-[linear-gradient(to_right,#64748b0a_1px,transparent_1px),linear-gradient(to_bottom,#64748b0a_1px,transparent_1px)] bg-[size:24px_24px] opacity-50"></div>
              <div class="relative text-[34px] font-bold leading-none tracking-[-0.04em] text-[var(--ct-ink)]">{{ s.value }}</div>
              <div class="relative">
                <div class="text-sm font-semibold text-[var(--ct-ink)]">{{ s.label }}</div>
                <p class="mt-1.5 text-[13px] leading-relaxed text-[var(--ct-text-muted)]">{{ s.desc }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- CAPACIDADES -->
      <section id="capacidades" class="relative bg-white">
        <div class="mx-auto max-w-[1200px] px-6 py-24">
          <div class="grid gap-10 lg:grid-cols-[0.82fr_1.18fr] lg:gap-16">
            <div class="lg:sticky lg:top-24 lg:self-start">
              <span class="font-mono text-xs uppercase tracking-[0.12em] text-[var(--ct-primary)]">O que fazemos</span>
              <h2 class="mt-3.5 text-[clamp(28px,3vw,40px)] font-bold tracking-[-0.03em] text-[var(--ct-ink)]">Tudo o que a operação precisa, em uma casa só</h2>
              <p class="mt-4 text-lg text-[var(--ct-text-muted)]">Da importação de clientes ao acompanhamento de obrigações. Veja cada frente em ação.</p>
              
              <nav class="mt-9 hidden flex-col lg:flex">
                <a v-for="cap in capabilities" :key="cap.id" :href="`#${cap.id}`" class="flex items-center gap-3 border-l-2 border-[var(--ct-primary-soft)] py-2.5 pl-4 text-[15px] font-medium text-[var(--ct-text-muted)] transition-all hover:border-[var(--ct-primary)] hover:text-[var(--ct-ink)]">
                  <span class="font-mono text-[11px] text-[var(--ct-primary)]">{{ cap.num }}</span>
                  {{ cap.tag }}
                </a>
              </nav>
            </div>

            <div class="flex flex-col">
              <div v-for="cap in capabilities" :key="cap.id" :id="cap.id" class="flex min-h-[68vh] scroll-mt-24 flex-col justify-center border-t border-[var(--ct-border)] py-12 first:border-t-0">
                <span class="flex h-12 w-12 items-center justify-center rounded-xl bg-[var(--ct-primary-soft)] font-mono text-sm font-bold text-[var(--ct-primary)]">{{ cap.num }}</span>
                <h3 class="mt-5 text-[clamp(22px,2.2vw,30px)] font-medium tracking-[-0.025em] text-[var(--ct-ink)]">{{ cap.title }}</h3>
                <p class="mt-3 max-w-[440px] text-[15px] leading-relaxed text-[var(--ct-text-muted)]">{{ cap.desc }}</p>

                <div class="mt-7 overflow-hidden rounded-xl border border-[var(--ct-border)] bg-[var(--ct-bg)]">
                  <div class="flex items-center gap-1.5 border-b border-[var(--ct-border)] bg-white px-3 py-2">
                    <span class="h-2.5 w-2.5 rounded-full bg-red-400"></span>
                    <span class="h-2.5 w-2.5 rounded-full bg-yellow-400"></span>
                    <span class="h-2.5 w-2.5 rounded-full bg-green-400"></span>
                    <span class="ml-2 font-mono text-[9.5px] uppercase tracking-[0.1em] text-slate-400">{{ cap.tag }} · visualização</span>
                  </div>

                  <div class="p-6">
                    <!-- Calendário -->
                    <div v-if="cap.mockup === 'calendar'">
                      <div class="mb-2 grid grid-cols-7 gap-1.5 text-center text-[9px] font-bold text-slate-400">
                        <span>D</span><span>S</span><span>T</span><span>Q</span><span>Q</span><span>S</span><span>S</span>
                      </div>
                      <div class="grid grid-cols-7 gap-1.5">
                        <div v-for="n in 30" :key="n" class="flex aspect-square flex-col rounded border border-[var(--ct-border)] bg-white p-1">
                          <span class="text-[9px] text-slate-400">{{ n }}</span>
                          <div v-if="[5, 10, 15, 20, 25].includes(n)" class="mb-0.5 mt-auto h-1.5 rounded-full bg-[var(--ct-primary)]"></div>
                          <div v-if="[10, 20].includes(n)" class="h-1.5 rounded-full bg-[var(--ct-navy)]"></div>
                        </div>
                      </div>
                    </div>

                    <!-- Workflow -->
                    <div v-else-if="cap.mockup === 'workflow'" class="flex items-center gap-3 overflow-x-auto pb-1">
                      <div class="whitespace-nowrap rounded-lg border border-[var(--ct-border)] bg-white px-4 py-3">
                        <span class="font-mono text-xs text-[var(--ct-text-muted)]">DAS Maio</span>
                      </div>
                      <svg width="24" height="12" viewBox="0 0 24 12" class="min-w-6 text-[var(--ct-primary)]"><path d="M0 6h20m-4-4 4 4-4 4" stroke="currentColor" stroke-width="1.6" fill="none" /></svg>
                      <div class="whitespace-nowrap rounded-lg border border-[#BFDBFE] bg-[#EFF6FF] px-4 py-3">
                        <span class="font-mono text-xs text-[var(--ct-primary)]">✓ Concluído</span>
                      </div>
                      <svg width="24" height="12" viewBox="0 0 24 12" class="min-w-6 text-[var(--ct-primary)]"><path d="M0 6h20m-4-4 4 4-4 4" stroke="currentColor" stroke-width="1.6" fill="none" /></svg>
                      <div class="whitespace-nowrap rounded-lg bg-[var(--ct-navy)] px-4 py-3">
                        <span class="font-mono text-xs text-white">DAS Junho (recorrente)</span>
                      </div>
                    </div>

                    <!-- Cliente -->
                    <div v-else-if="cap.mockup === 'client'" class="space-y-3">
                      <div class="flex items-center gap-3 rounded-lg border border-[var(--ct-border)] bg-white p-3">
                        <div class="flex h-8 w-8 items-center justify-center rounded-full bg-[var(--ct-primary-soft)] text-xs font-bold text-[var(--ct-primary)]">JA</div>
                        <div>
                          <div class="text-sm font-medium text-[var(--ct-ink)]">João Alves ME</div>
                          <div class="font-mono text-[10px] text-slate-400">CNPJ 12.345.../0001-90</div>
                        </div>
                        <span class="ml-auto rounded bg-[var(--ct-primary-soft)] px-2 py-0.5 text-[10px] font-bold text-[var(--ct-primary)]">Simples</span>
                      </div>
                      <div class="grid grid-cols-3 gap-2">
                        <div class="rounded border border-[var(--ct-border)] bg-white p-2 text-center"><div class="text-lg font-bold text-[var(--ct-ink)]">3</div><div class="text-[9px] text-slate-400">Tarefas</div></div>
                        <div class="rounded border border-[var(--ct-border)] bg-white p-2 text-center"><div class="text-lg font-bold text-amber-600">1</div><div class="text-[9px] text-slate-400">Pendente</div></div>
                        <div class="rounded border border-[var(--ct-border)] bg-white p-2 text-center"><div class="text-lg font-bold text-[var(--ct-ink)]">5</div><div class="text-[9px] text-slate-400">Docs</div></div>
                      </div>
                    </div>

                    <!-- Documentos -->
                    <div v-else-if="cap.mockup === 'docs'" class="space-y-2">
                      <div class="flex items-center gap-3 rounded-lg border border-[var(--ct-border)] bg-white p-3">
                        <span class="text-lg">📕</span>
                        <span class="text-sm text-[var(--ct-ink)]">DAS-Maio.pdf</span>
                        <span class="ml-auto rounded bg-[#EFF6FF] px-2 py-0.5 text-[10px] font-bold text-[var(--ct-primary)]">Fiscal</span>
                      </div>
                      <div class="flex items-center gap-3 rounded-lg border border-[var(--ct-border)] bg-white p-3">
                        <span class="text-lg">📄</span>
                        <span class="text-sm text-[var(--ct-ink)]">notas.xml</span>
                        <span class="ml-auto rounded bg-[#EFF6FF] px-2 py-0.5 text-[10px] font-bold text-[var(--ct-primary)]">Fiscal</span>
                      </div>
                      <div class="flex items-center gap-3 rounded-lg border border-[var(--ct-border)] bg-white p-3">
                        <span class="text-lg">📗</span>
                        <span class="text-sm text-[var(--ct-ink)]">folha.xlsx</span>
                        <span class="ml-auto rounded bg-amber-50 px-2 py-0.5 text-[10px] font-bold text-amber-700">DP</span>
                      </div>
                    </div>

                    <!-- Equipe -->
                    <div v-else-if="cap.mockup === 'team'" class="space-y-4">
                      <div class="flex items-center gap-3">
                        <div class="flex h-8 w-8 items-center justify-center rounded-full bg-[var(--ct-navy)] text-xs font-bold text-white">AC</div>
                        <div class="flex-1">
                          <div class="mb-1 flex justify-between text-xs"><span class="text-[var(--ct-ink)]">Ana Costa</span><span class="font-bold text-[var(--ct-primary)]">7 tarefas</span></div>
                          <div class="h-2 rounded-full bg-slate-100"><div class="h-2 w-[87%] rounded-full bg-[var(--ct-primary)]"></div></div>
                        </div>
                      </div>
                      <div class="flex items-center gap-3">
                        <div class="flex h-8 w-8 items-center justify-center rounded-full bg-[var(--ct-navy)] text-xs font-bold text-white">RB</div>
                        <div class="flex-1">
                          <div class="mb-1 flex justify-between text-xs"><span class="text-[var(--ct-ink)]">Rafael B.</span><span class="font-bold text-slate-400">3 tarefas</span></div>
                          <div class="h-2 rounded-full bg-slate-100"><div class="h-2 w-[37%] rounded-full bg-[var(--ct-navy)]"></div></div>
                        </div>
                      </div>
                    </div>

                    <!-- Sync -->
                    <div v-else-if="cap.mockup === 'sync'" class="py-4 text-center">
                      <div class="inline-flex items-center gap-3 rounded-xl border border-[var(--ct-border)] bg-white px-6 py-4">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2"><path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /><path d="M12 7v5l3 3" /></svg>
                        <span class="font-mono text-sm text-[var(--ct-text-muted)]">.ics feed ativo</span>
                        <span class="rounded bg-green-50 px-2 py-0.5 font-mono text-xs text-green-700">Sincronizando</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- MÉTODO -->
      <section id="metodo" class="relative border-y border-[var(--ct-border)] bg-[var(--ct-bg)]">
        <div class="mx-auto max-w-[1200px] px-6 py-24">
          <div v-fade-in class="mb-12 max-w-[760px]">
            <span class="font-mono text-xs uppercase tracking-[0.12em] text-[var(--ct-primary)]">Como funciona</span>
            <h2 class="mt-3.5 text-[clamp(28px,3vw,40px)] font-bold tracking-[-0.03em] text-[var(--ct-ink)]">Quatro passos para mais controle</h2>
            <p class="mt-4 text-lg text-[var(--ct-text-muted)]">Do cadastro do cliente à entrega da obrigação, com uma rotina mais previsível.</p>
          </div>

          <div class="grid max-w-4xl grid-cols-1 gap-4 md:grid-cols-2">
            <div v-for="(step, i) in steps" :key="step.num" v-fade-in class="relative flex h-full flex-col overflow-hidden rounded-2xl border p-7 transition-all hover:-translate-y-1 hover:shadow-lg" :class="i === 3 ? 'border-transparent bg-[var(--ct-primary)] text-white shadow-lg shadow-blue-600/20' : 'border-[var(--ct-border)] bg-white'">
              <div class="flex items-center justify-between">
                <span class="font-mono text-xs tracking-[0.12em]" :class="i === 3 ? 'text-white/80' : 'text-[var(--ct-primary)]'">PASSO {{ step.num }}</span>
                <span class="rounded-full border px-3 py-1 font-mono text-[10px] uppercase tracking-[0.1em]" :class="i === 3 ? 'border-white/20 text-white/80' : 'border-[var(--ct-border)] text-slate-400'">fluxo do escritório</span>
              </div>
              <h3 class="mt-3 text-xl font-medium tracking-tight" :class="i === 3 ? 'text-white' : 'text-[var(--ct-ink)]'">{{ step.title }}</h3>
              <p class="mt-2 text-sm leading-relaxed" :class="i === 3 ? 'text-white/80' : 'text-[var(--ct-text-muted)]'">{{ step.desc }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- CENÁRIOS -->
      <section id="cenarios" class="relative border-y border-[var(--ct-border)] bg-white">
        <div class="mx-auto max-w-[1200px] px-6 py-24">
          <div v-fade-in class="mb-12 max-w-[760px]">
            <span class="font-mono text-xs uppercase tracking-[0.12em] text-[var(--ct-primary)]">Cenários</span>
            <h2 class="mt-3.5 text-[clamp(28px,3vw,40px)] font-bold tracking-[-0.03em] text-[var(--ct-ink)]">O que a ContablyTask ajuda a resolver</h2>
            <p class="mt-4 text-lg text-[var(--ct-text-muted)]">Uma estrutura para trazer mais visibilidade e consistência à operação contábil.</p>
          </div>

          <div class="mb-4" v-fade-in>
            <article class="relative grid overflow-hidden rounded-2xl bg-[var(--ct-navy)] lg:grid-cols-[1.15fr_0.85fr]">
              <div class="absolute inset-0 bg-[linear-gradient(to_right,#ffffff08_1px,transparent_1px),linear-gradient(to_bottom,#ffffff08_1px,transparent_1px)] bg-[size:24px_24px] opacity-30"></div>
              <div class="relative z-10 flex flex-col justify-between gap-10 p-9 lg:p-12">
                <div>
                  <span class="font-mono text-xs uppercase tracking-[0.12em] text-[#93C5FD]">Gestão operacional</span>
                  <h3 class="mt-5 text-[clamp(24px,2.6vw,36px)] font-normal leading-[1.25] tracking-[-0.02em] text-white">Menos dependência de planilhas, mensagens soltas e cobranças manuais.</h3>
                  <p class="mt-5 max-w-[560px] text-[15px] leading-relaxed text-white/70">Centralize tarefas, prazos, documentos e responsáveis para que toda a equipe possa entender o que precisa ser feito, por quem e até quando.</p>
                </div>
                <div class="flex items-center gap-3.5">
                  <div class="flex h-11 w-11 items-center justify-center rounded-full bg-white/10 text-sm font-semibold text-white">CT</div>
                  <div>
                    <div class="text-sm font-semibold text-white">ContablyTask</div>
                    <div class="text-xs text-white/60">Organização para a rotina contábil</div>
                  </div>
                </div>
              </div>
              <div class="relative flex min-h-[260px] items-center justify-center overflow-hidden bg-[#0F172A] p-9">
                <div class="grid w-full max-w-xs grid-cols-2 gap-3">
                  <div class="rounded-xl border border-white/10 bg-white/5 p-4"><div class="text-2xl font-bold text-white">Clientes</div><div class="mt-1 text-xs text-white/50">Base centralizada</div></div>
                  <div class="rounded-xl border border-white/10 bg-white/5 p-4"><div class="text-2xl font-bold text-[#93C5FD]">Prazos</div><div class="mt-1 text-xs text-white/50">Visão organizada</div></div>
                  <div class="rounded-xl border border-white/10 bg-white/5 p-4"><div class="text-2xl font-bold text-white">Equipe</div><div class="mt-1 text-xs text-white/50">Responsáveis claros</div></div>
                  <div class="rounded-xl border border-white/10 bg-white/5 p-4"><div class="text-2xl font-bold text-white">Docs</div><div class="mt-1 text-xs text-white/50">Arquivos vinculados</div></div>
                </div>
              </div>
            </article>
          </div>

          <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
            <div v-for="c in cases" :key="c.title" v-fade-in class="flex h-full flex-col rounded-2xl border border-[var(--ct-border)] bg-white p-7 transition-all hover:-translate-y-1 hover:shadow-md">
              <span class="font-mono text-[10.5px] uppercase tracking-[0.12em] text-[var(--ct-primary)]">{{ c.tag }}</span>
              <h3 class="mt-3 text-base font-medium leading-tight tracking-tight text-[var(--ct-ink)]">{{ c.title }}</h3>
              <p class="mt-2 text-[13.5px] leading-relaxed text-[var(--ct-text-muted)]">{{ c.desc }}</p>
              <div class="mt-auto border-t border-[var(--ct-border)] pt-4">
                <span class="text-sm font-medium text-[var(--ct-ink)]">{{ c.metric }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- PLANOS -->
      <section id="pricing" class="relative border-y border-[var(--ct-border)] bg-[var(--ct-bg)]">
        <div class="mx-auto max-w-[1200px] px-6 py-24">
          <div v-fade-in class="mb-16 text-center">
            <span class="font-mono text-xs uppercase tracking-[0.12em] text-[var(--ct-primary)]">Planos</span>
            <h2 class="mt-3.5 text-[clamp(28px,3vw,40px)] font-bold tracking-[-0.03em] text-[var(--ct-ink)]">Comece de graça. Evolua quando precisar.</h2>
            <p class="mt-4 text-lg text-[var(--ct-text-muted)]">Sem cartão de crédito para começar.</p>
          </div>

          <div class="grid items-stretch gap-4 md:grid-cols-4">
            <div v-for="p in plans" :key="p.name" v-fade-in class="relative flex h-full flex-col rounded-2xl border bg-white p-8 transition-all hover:shadow-lg" :class="p.featured ? 'border-[var(--ct-primary)] shadow-xl md:scale-105 z-10' : 'border-[var(--ct-border)]'">
              <div v-if="p.featured" class="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-[var(--ct-primary)] px-3 py-1 text-xs font-bold text-white">Mais popular</div>
              <h3 class="mb-3 font-mono text-xs uppercase tracking-[0.12em] text-slate-400">{{ p.name }}</h3>
              <div class="mb-1 flex items-end gap-1">
                <span class="mb-1 text-lg font-bold text-slate-400">R$</span>
                <span class="text-4xl font-extrabold tracking-tight text-[var(--ct-ink)]">{{ p.price }}</span>
              </div>
              <p class="mb-6 text-xs text-slate-400">{{ p.desc }}</p>
              <ul class="mb-8 space-y-3 border-t border-[var(--ct-border)] pt-6">
                <li v-for="f in p.features" :key="f" class="flex items-start gap-2 text-sm text-[var(--ct-text-muted)]">
                  <svg class="mt-0.5 h-4 w-4 flex-shrink-0 text-[var(--ct-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" /></svg>
                  {{ f }}
                </li>
              </ul>
              <div class="mt-auto">
                <RouterLink to="/cadastro" class="block w-full rounded-xl py-3 text-center text-sm font-bold transition-all" :class="p.featured ? 'bg-[var(--ct-primary)] text-white hover:bg-[var(--ct-primary-hover)]' : 'bg-[var(--ct-muted)] text-[var(--ct-ink)] hover:bg-[#E2E8F0]'">{{ p.cta }}</RouterLink>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- CTA FINAL -->
      <section class="bg-[var(--ct-bg)] px-3 pb-3">
        <div class="relative isolate overflow-hidden rounded-[28px] bg-[var(--ct-navy)] px-6 py-20 md:py-28">
          <div class="absolute inset-0 bg-[linear-gradient(to_right,#ffffff08_1px,transparent_1px),linear-gradient(to_bottom,#ffffff08_1px,transparent_1px)] bg-[size:32px_32px] opacity-40"></div>
          <div class="animate-float absolute -top-24 left-1/2 h-[34rem] w-[34rem] -translate-x-1/2 rounded-full bg-[var(--ct-primary)]/25 blur-[80px]"></div>
          <div class="absolute inset-0" style="background: radial-gradient(120% 80% at 50% 0%, transparent 40%, rgba(15, 23, 42, .65) 100%)"></div>

          <div class="relative mx-auto flex max-w-[820px] flex-col items-center text-center">
            <span class="font-mono text-xs uppercase tracking-[0.12em] text-[#93C5FD]">Conheça a plataforma</span>
            <h2 class="mt-5 text-[clamp(30px,4vw,52px)] font-semibold leading-[1.06] tracking-[-0.035em] text-white">
              Mais organização para uma rotina contábil
              <span class="bg-gradient-to-r from-[#93C5FD] to-white bg-clip-text text-transparent">mais previsível.</span>
            </h2>
            <p class="mt-5 max-w-[560px] text-lg leading-relaxed text-white/70">Comece pelo plano gratuito e veja como a ContablyTask pode ajudar a centralizar tarefas, prazos e documentos do seu escritório.</p>
            
            <div class="mt-9 flex flex-wrap items-center justify-center gap-3">
              <RouterLink to="/cadastro" class="inline-flex items-center gap-2 rounded-xl bg-white px-7 py-3.5 text-sm font-semibold text-[var(--ct-navy)] shadow-lg transition-all hover:bg-[#EFF6FF]">
                Criar conta grátis
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M13 6l6 6-6 6" /></svg>
              </RouterLink>
              <a href="#metodo" class="inline-flex items-center rounded-xl border border-white/25 px-6 py-3.5 text-sm font-semibold text-white transition-all hover:bg-white/10">Como funciona</a>
            </div>

            <div class="mt-10 flex flex-wrap items-center justify-center gap-x-3 gap-y-2">
              <span class="rounded-full border border-white/12 bg-white/5 px-3.5 py-1.5 font-mono text-[11px] uppercase tracking-[0.08em] text-white/65">Plano gratuito disponível</span>
              <span class="rounded-full border border-white/12 bg-white/5 px-3.5 py-1.5 font-mono text-[11px] uppercase tracking-[0.08em] text-white/65">Sem cartão de crédito</span>
              <span class="rounded-full border border-white/12 bg-white/5 px-3.5 py-1.5 font-mono text-[11px] uppercase tracking-[0.08em] text-white/65">Suporte em português</span>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- FOOTER -->
    <footer class="relative overflow-hidden bg-[var(--ct-navy)] text-white">
      <div class="absolute inset-0 bg-[linear-gradient(to_right,#ffffff08_1px,transparent_1px),linear-gradient(to_bottom,#ffffff08_1px,transparent_1px)] bg-[size:32px_32px] opacity-30"></div>
      <div class="absolute -left-40 -top-32 h-[30rem] w-[30rem] rounded-full bg-[var(--ct-primary)]/15 blur-[80px]"></div>

      <div class="relative mx-auto max-w-[1200px] px-6 pt-20">
        <div class="grid gap-12 md:grid-cols-2 lg:grid-cols-[1.5fr_1fr_1fr_1fr]">
          <div>
            <a href="/" class="inline-flex items-center gap-2.5">
              <div class="flex h-9 w-9 items-center justify-center rounded-[10px] bg-white/10">
                <svg viewBox="0 0 24 24" fill="none" stroke="#93C5FD" stroke-width="2.5" class="h-5 w-5"><path d="M9 11l3 3L22 4" /><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" /></svg>
              </div>
              <span class="text-2xl font-extrabold tracking-tight">ContablyTask</span>
            </a>
            <p class="mt-4 max-w-[300px] text-sm leading-relaxed text-white/70">Organização operacional para profissionais e escritórios contábeis. Centralize clientes, obrigações e documentos em um só lugar.</p>
          </div>

          <div>
            <h5 class="mb-4 font-mono text-xs font-medium uppercase tracking-[0.12em] text-white/50">Capacidades</h5>
            <a href="#capacidades" class="block py-1.5 text-sm text-white/75 transition-colors hover:text-white">Calendário</a>
            <a href="#capacidades" class="block py-1.5 text-sm text-white/75 transition-colors hover:text-white">Workflow</a>
            <a href="#capacidades" class="block py-1.5 text-sm text-white/75 transition-colors hover:text-white">Clientes</a>
            <a href="#capacidades" class="block py-1.5 text-sm text-white/75 transition-colors hover:text-white">Documentos</a>
            <a href="#capacidades" class="block py-1.5 text-sm text-white/75 transition-colors hover:text-white">Equipe</a>
          </div>

          <div>
            <h5 class="mb-4 font-mono text-xs font-medium uppercase tracking-[0.12em] text-white/50">Plataforma</h5>
            <a href="#metodo" class="block py-1.5 text-sm text-white/75 transition-colors hover:text-white">Como funciona</a>
            <a href="#cenarios" class="block py-1.5 text-sm text-white/75 transition-colors hover:text-white">Cenários</a>
            <a href="#pricing" class="block py-1.5 text-sm text-white/75 transition-colors hover:text-white">Planos</a>
          </div>

          <div>
            <h5 class="mb-4 font-mono text-xs font-medium uppercase tracking-[0.12em] text-white/50">Acesso</h5>
            <RouterLink to="/cadastro" class="block py-1.5 text-sm text-white/75 transition-colors hover:text-white">Criar conta</RouterLink>
            <RouterLink to="/login" class="block py-1.5 text-sm text-white/75 transition-colors hover:text-white">Login</RouterLink>
          </div>
        </div>

        <div class="pointer-events-none mt-16 select-none overflow-hidden">
          <div class="bg-gradient-to-b from-white/[0.07] to-white/0 bg-clip-text text-transparent">
            <span class="block text-[clamp(60px,14vw,180px)] font-extrabold lowercase leading-[0.82] tracking-[-0.04em]">ContablyTask</span>
          </div>
        </div>

        <div class="flex flex-wrap items-center justify-between gap-4 border-t border-white/10 py-7">
          <p class="text-xs text-white/55">© 2026 ContablyTask. Todos os direitos reservados.</p>
          <div class="flex gap-6">
            <a href="/privacidade" class="text-xs text-white/55 transition-colors hover:text-white">Privacidade</a>
            <a href="/termos" class="text-xs text-white/55 transition-colors hover:text-white">Termos de Uso</a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
:global(:root) {
  --ct-bg: #F8FAFC;
  --ct-surface: #FFFFFF;
  --ct-muted: #F1F5F9;
  --ct-border: #E2E8F0;

  --ct-ink: #0F172A;
  --ct-text-muted: #64748B;

  --ct-primary: #2563EB;
  --ct-primary-hover: #1D4ED8;
  --ct-primary-soft: #DBEAFE;
  --ct-navy: #172554;
}

:global(html) {
  scroll-behavior: smooth;
}

@keyframes float {
  0%, 100% { transform: translate(-50%, 0); }
  50% { transform: translate(-50%, -20px); }
}

.animate-float {
  animation: float 6s ease-in-out infinite;
}
</style>