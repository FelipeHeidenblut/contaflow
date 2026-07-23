<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

const router = useRouter()
const email = ref('')

const stats = [
  { label: 'MRR Estimado', value: 'R$ 2,4K', desc: 'Receita recorrente ativa dos escritórios na plataforma.' },
  { label: 'Escritórios', value: '3', desc: 'Ativos e gerenciando suas obrigações no sistema.' },
  { label: 'Clientes Finais', value: '15', desc: 'Empresas gerenciadas pelos escritórios na plataforma.' },
  { label: 'Tarefas', value: '47', desc: 'Obrigações fiscais e tarefas criadas e controladas.' },
]

const capabilities = [
  {
    id: 'cap-0', num: '01', tag: 'Calendário',
    title: 'Tudo o que importa, numa tela',
    desc: 'Vencimentos federais, estaduais e tarefas internas em um só calendário. O dashboard mostra o que está vencendo, o que atrasou e onde a equipe está focando.',
    mockup: 'calendar'
  },
  {
    id: 'cap-1', num: '02', tag: 'Workflow',
    title: 'Processos que rodam sozinhos',
    desc: 'Tarefas recorrentes mensais (DAS, Folha, SPED) são criadas automaticamente todo mês no dia útil correto. O que era trabalho manual repetido vira fluxo automático.',
    mockup: 'workflow'
  },
  {
    id: 'cap-2', num: '03', tag: 'Clientes',
    title: 'Dossiê do cliente em segundos',
    desc: 'Centralize dados cadastrais, tarefas em aberto, documentos e histórico de cada CNPJ. Saiba exatamente o que está pendente para cada cliente sem abrir planilhas.',
    mockup: 'client'
  },
  {
    id: 'cap-3', num: '04', tag: 'Documentos',
    title: 'Repositório vivo, não pasta morta',
    desc: 'XMLs, planilhas e comprovantes anexados diretamente nas tarefas. Categorizados por tipo (Fiscal, Contábil, DP) e com ícones dinâmicos por extensão.',
    mockup: 'docs'
  },
  {
    id: 'cap-4', num: '05', tag: 'Equipe',
    title: 'Capacidade que se vê',
    desc: 'Barras de progresso mostram quem está sobrecarregado e quem tem respiro. Distribua o trabalho com base em dado, não em achismo.',
    mockup: 'team'
  },
  {
    id: 'cap-5', num: '06', tag: 'Integração',
    title: 'Sua agenda, atualizada sozinha',
    desc: 'Gere um link .ics e sincronize todos os prazos com Google Agenda e Outlook. O contador vê as obrigações no celular, sem abrir o sistema.',
    mockup: 'sync'
  },
]

const steps = [
  { num: '01', title: 'Centralize', desc: 'Importe sua base de clientes via CSV em minutos. O sistema reconhece Comércio, Serviços e regime tributário.' },
  { num: '02', title: 'Organização', desc: 'Crie tarefas com templates contábeis prontos (DAS, SPED, DCTFWeb). Atribua responsáveis e defina prioridades.' },
  { num: '03', title: 'Automação', desc: 'Tarefas recorrentes mensais são criadas automaticamente no dia útil correto, sem trabalho manual.' },
  { num: '04', title: 'Entrega', desc: 'Acompanhe o progresso em tempo real e comprove o trabalho com histórico completo por cliente.' },
]

const cases = [
  { tag: 'Autônomo', title: 'Contador organizou 20 clientes em 1 dia', desc: 'Migrou do Excel para o ContablyTask e zerou os atrasos de DAS no primeiro mês.', metric: '20 clientes ativos' },
  { tag: 'Escritório', title: 'Equipe de 5 pessoas alinhada sem WhatsApp', desc: 'Distribuição de tarefas e capacidade visual reduziram reuniões em 60%.', metric: '5 usuários' },
  { tag: 'Crescimento', title: 'Escalou de 40 para 100 clientes sem caos', desc: 'Automação de recorrência e dossiê do cliente permitiram crescer sem contratar.', metric: '100 clientes' },
]

const plans = [
  { name: 'Free', price: '0', desc: 'Para testar a plataforma.', cta: 'Começar Grátis', featured: false, features: ['Até 5 clientes', '1 usuário (Admin)', 'Calendário de obrigações', 'Gestão de documentos'] },
  { name: 'Básico', price: '79,90', desc: 'Para contadores autônomos.', cta: 'Assinar Básico', featured: false, features: ['Até 40 clientes', 'Até 5 usuários', 'Tudo do Free', 'Alertas por e-mail'] },
  { name: 'Profissional', price: '149,90', desc: 'Para escritórios em crescimento.', cta: 'Assinar Profissional', featured: true, features: ['Até 100 clientes', 'Até 10 usuários', 'Tudo do Básico', 'Distribuição de equipe', 'Relatórios avançados'] },
  { name: 'Business', price: '449', desc: 'Para grandes operações.', cta: 'Falar com vendas', featured: false, features: ['Clientes ilimitados', 'Usuários ilimitados', 'Tudo do Profissional', 'API e integrações', 'Gerente dedicado'] },
]

const handleCTA = () => {
  if (!email.value || !email.value.includes('@')) return
  router.push({ path: '/cadastro', query: { email: email.value } })
}

const vFadeIn = {
  mounted(el: HTMLElement) {
    el.style.opacity = '0'
    el.style.transform = 'translateY(20px)'
    el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out'
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) { el.style.opacity = '1'; el.style.transform = 'translateY(0)'; observer.unobserve(el) }
      })
    }, { threshold: 0.1 })
    observer.observe(el)
  },
}
</script>

<template>
  <div class="bg-white text-[#19341a] antialiased font-sans overflow-x-clip">

    <!-- NAV -->
    <header class="sticky top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-gray-100">
      <div class="mx-auto flex h-16 max-w-[1200px] items-center justify-between px-6">
        <a href="/" class="flex items-center gap-2.5">
          <div class="w-9 h-9 rounded-[10px] bg-[#19341a] flex items-center justify-center">
            <svg viewBox="0 0 24 24" fill="none" stroke="#ff8a65" stroke-width="2.5" class="w-5 h-5"><path d="M9 11l3 3L22 4" /><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" /></svg>
          </div>
          <span class="font-extrabold text-lg tracking-tight">ContablyTask</span>
        </a>
        <nav class="hidden lg:flex items-center gap-1">
          <a href="#capacidades" class="px-3 py-2 text-[15px] font-medium text-gray-500 hover:text-[#19341a] rounded-lg transition-colors">Capacidades</a>
          <a href="#metodo" class="px-3 py-2 text-[15px] font-medium text-gray-500 hover:text-[#19341a] rounded-lg transition-colors">Como funciona</a>
          <a href="#casos" class="px-3 py-2 text-[15px] font-medium text-gray-500 hover:text-[#19341a] rounded-lg transition-colors">Casos</a>
          <a href="#pricing" class="px-3 py-2 text-[15px] font-medium text-gray-500 hover:text-[#19341a] rounded-lg transition-colors">Planos</a>
        </nav>
        <div class="flex items-center gap-2">
          <RouterLink to="/login" class="text-sm font-medium px-3 py-2 hover:bg-gray-100 rounded-lg transition-colors">Login</RouterLink>
          <RouterLink to="/cadastro" class="text-sm font-bold text-white bg-[#19341a] px-4 py-2 rounded-lg hover:bg-[#0f2010] transition-colors">Começar grátis</RouterLink>
        </div>
      </div>
    </header>

    <main>
      <!-- HERO (Tela cheia, fundo escuro) -->
      <section class="relative bg-[#19341a] text-white overflow-hidden">
        <div class="absolute inset-0 bg-[linear-gradient(to_right,#ffffff08_1px,transparent_1px),linear-gradient(to_bottom,#ffffff08_1px,transparent_1px)] bg-[size:32px_32px] opacity-40"></div>
        <div class="absolute top-0 left-1/4 w-96 h-96 bg-[#ff8a65]/20 rounded-full blur-[120px]"></div>
        <div class="absolute inset-0" style="background:radial-gradient(120% 90% at 50% 30%, transparent 38%, rgba(25,52,26,.65) 100%)"></div>
        
        <div class="relative mx-auto flex max-w-[860px] flex-col items-center px-6 py-28 text-center">
          <span class="inline-flex items-center gap-1.5 rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs font-medium backdrop-blur-sm mb-6">Software para escritórios contábeis</span>
          <h1 class="text-[clamp(40px,6vw,76px)] font-semibold leading-[1.03] tracking-[-0.04em]">
            A tecnologia que faz o seu escritório <span class="bg-gradient-to-r from-[#ff8a65] to-white bg-clip-text text-transparent">funcionar</span>.
          </h1>
          <p class="mt-6 max-w-[600px] text-[clamp(16px,1.4vw,19px)] leading-relaxed text-white/75">
            Gestão de tarefas, prazos e documentos construída para a rotina contábil brasileira. Centralize clientes, obrigações fiscais e equipe num só lugar.
          </p>
          <div class="mt-9 flex flex-wrap items-center justify-center gap-3">
            <RouterLink to="/cadastro" class="inline-flex items-center gap-2 rounded-xl bg-[#ff8a65] px-7 py-3.5 text-[15px] font-semibold text-white shadow-lg shadow-[#ff8a65]/30 transition-all hover:bg-[#f07047]">
              Criar conta grátis <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
            </RouterLink>
            <a href="#metodo" class="inline-flex items-center rounded-xl border border-white/30 px-6 py-3.5 text-[15px] font-semibold text-white transition-all hover:bg-white/10">Como funciona</a>
          </div>
        </div>
      </section>

      <!-- PROVA (Bento Grid de métricas) -->
      <section class="relative bg-[#f8fafc] border-y border-gray-100">
        <div class="mx-auto max-w-[1200px] px-6 py-24">
          <div v-fade-in class="mb-12 max-w-[680px]">
            <span class="font-mono text-xs uppercase tracking-[0.12em] text-[#ff8a65]">Prova em produção</span>
            <h2 class="text-[clamp(28px,3vw,40px)] font-bold tracking-[-0.03em] mt-3.5 text-[#19341a]">Números que estão no ar, rodando</h2>
            <p class="mt-4 text-gray-500 text-lg">A prova de um software de gestão é o sistema rodando em produção com escritórios reais.</p>
          </div>
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div v-for="s in stats" :key="s.label" v-fade-in class="relative flex h-full min-h-[220px] flex-col justify-between overflow-hidden rounded-2xl border border-gray-100 bg-white p-7 hover:shadow-md transition-all">
              <div class="absolute inset-0 bg-[linear-gradient(to_right,#80808006_1px,transparent_1px),linear-gradient(to_bottom,#80808006_1px,transparent_1px)] bg-[size:24px_24px] opacity-50"></div>
              <div class="relative text-[44px] font-bold leading-none tracking-[-0.04em] text-[#19341a]">{{ s.value }}</div>
              <div class="relative">
                <div class="text-sm font-semibold text-[#19341a]">{{ s.label }}</div>
                <p class="mt-1.5 text-[13px] leading-relaxed text-gray-500">{{ s.desc }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- CAPACIDADES (Split com nav lateral fixa) -->
      <section id="capacidades" class="relative bg-white">
        <div class="mx-auto max-w-[1200px] px-6 py-24">
          <div class="grid gap-10 lg:grid-cols-[0.82fr_1.18fr] lg:gap-16">
            <!-- Lateral Fixa -->
            <div class="lg:sticky lg:top-24 lg:self-start">
              <span class="font-mono text-xs uppercase tracking-[0.12em] text-[#ff8a65]">O que fazemos</span>
              <h2 class="text-[clamp(28px,3vw,40px)] font-bold tracking-[-0.03em] mt-3.5 text-[#19341a]">Tudo o que a operação precisa, numa casa só</h2>
              <p class="mt-4 text-gray-500 text-lg">Da importação de clientes ao envio de obrigações. Role e veja cada frente em ação.</p>
              <nav class="mt-9 hidden flex-col lg:flex">
                <a v-for="cap in capabilities" :key="cap.id" :href="`#${cap.id}`" class="flex items-center gap-3 border-l-2 py-2.5 pl-4 text-[15px] transition-all border-[#ff8a65] font-medium text-[#19341a]">
                  <span class="font-mono text-[11px] text-[#ff8a65]">{{ cap.num }}</span> {{ cap.tag }}
                </a>
              </nav>
            </div>
            <!-- Conteúdo que rola -->
            <div class="flex flex-col">
              <div v-for="cap in capabilities" :key="cap.id" :id="cap.id" class="flex min-h-[68vh] scroll-mt-24 flex-col justify-center border-t border-gray-100 py-12 first:border-t-0">
                <span class="flex size-12 items-center justify-center rounded-xl bg-[#eaf3ea] text-[#ff8a65] font-mono text-sm font-bold">{{ cap.num }}</span>
                <h3 class="mt-5 text-[clamp(22px,2.2vw,30px)] font-medium tracking-[-0.025em] text-[#19341a]">{{ cap.title }}</h3>
                <p class="mt-3 max-w-[440px] text-[15px] leading-relaxed text-gray-500">{{ cap.desc }}</p>
                
                <!-- Mockup Window -->
                <div class="mt-7 overflow-hidden rounded-xl border border-gray-100 bg-[#f8fafc]">
                  <div class="flex items-center gap-1.5 border-b px-3 py-2 border-gray-100 bg-white">
                    <span class="size-1.5 rounded-full bg-[#ff8a65]/50"></span>
                    <span class="size-1.5 rounded-full bg-gray-300"></span>
                    <span class="size-1.5 rounded-full bg-gray-300"></span>
                    <span class="ml-1.5 font-mono text-[9.5px] uppercase tracking-[0.1em] text-gray-400">{{ cap.tag }} · ao vivo</span>
                  </div>
                  <div class="p-6">
                    <!-- Calendário -->
                    <div v-if="cap.mockup === 'calendar'" class="grid grid-cols-7 gap-1.5">
                      <div v-for="n in 30" :key="n" class="aspect-square rounded border border-gray-100 bg-white p-1 flex flex-col">
                        <span class="text-[9px] text-gray-400">{{ n }}</span>
                        <div v-if="[5, 10, 15, 20, 25].includes(n)" class="mt-auto h-1.5 rounded-full bg-[#ff8a65] mb-0.5"></div>
                        <div v-if="[10, 20].includes(n)" class="h-1.5 rounded-full bg-[#19341a]"></div>
                      </div>
                    </div>
                    <!-- Workflow -->
                    <div v-else-if="cap.mockup === 'workflow'" class="flex items-center gap-3">
                      <div class="rounded-lg border border-gray-100 bg-white px-4 py-3"><span class="font-mono text-xs text-gray-500">DAS Maio</span></div>
                      <svg width="24" height="12" viewBox="0 0 24 12" class="text-[#ff8a65]"><path d="M0 6h20m-4-4 4 4-4 4" stroke="currentColor" stroke-width="1.6" fill="none"/></svg>
                      <div class="rounded-lg border border-[#ff8a65] bg-[#fff3e0] px-4 py-3"><span class="font-mono text-xs text-[#ff8a65]">✓ Concluído</span></div>
                      <svg width="24" height="12" viewBox="0 0 24 12" class="text-[#ff8a65]"><path d="M0 6h20m-4-4 4 4-4 4" stroke="currentColor" stroke-width="1.6" fill="none"/></svg>
                      <div class="rounded-lg bg-[#19341a] px-4 py-3"><span class="font-mono text-xs text-white">DAS Junho (auto)</span></div>
                    </div>
                    <!-- Cliente -->
                    <div v-else-if="cap.mockup === 'client'" class="space-y-3">
                      <div class="flex items-center gap-3 rounded-lg border border-gray-100 bg-white p-3">
                        <div class="size-8 rounded-full bg-[#19341a]/10 flex items-center justify-center text-xs font-bold text-[#19341a]">JA</div>
                        <div><div class="text-sm font-medium">João Alves ME</div><div class="font-mono text-[10px] text-gray-400">CNPJ 12.345.../0001-90</div></div>
                        <span class="ml-auto text-[10px] font-bold bg-[#eaf3ea] text-[#19341a] px-2 py-0.5 rounded">Simples</span>
                      </div>
                      <div class="grid grid-cols-3 gap-2">
                        <div class="rounded border border-gray-100 bg-white p-2 text-center"><div class="text-lg font-bold text-[#19341a]">3</div><div class="text-[9px] text-gray-400">Tarefas</div></div>
                        <div class="rounded border border-gray-100 bg-white p-2 text-center"><div class="text-lg font-bold text-[#ff8a65]">1</div><div class="text-[9px] text-gray-400">Atrasada</div></div>
                        <div class="rounded border border-gray-100 bg-white p-2 text-center"><div class="text-lg font-bold text-[#19341a]">5</div><div class="text-[9px] text-gray-400">Docs</div></div>
                      </div>
                    </div>
                    <!-- Documentos -->
                    <div v-else-if="cap.mockup === 'docs'" class="space-y-2">
                      <div class="flex items-center gap-3 rounded-lg border border-gray-100 bg-white p-3">
                        <span class="text-lg">📕</span><span class="text-sm">DAS-Maio.pdf</span><span class="ml-auto text-[10px] font-bold bg-blue-50 text-blue-600 px-2 py-0.5 rounded">Fiscal</span>
                      </div>
                      <div class="flex items-center gap-3 rounded-lg border border-gray-100 bg-white p-3">
                        <span class="text-lg">📄</span><span class="text-sm">notas.xml</span><span class="ml-auto text-[10px] font-bold bg-blue-50 text-blue-600 px-2 py-0.5 rounded">Fiscal</span>
                      </div>
                      <div class="flex items-center gap-3 rounded-lg border border-gray-100 bg-white p-3">
                        <span class="text-lg">📗</span><span class="text-sm">folha.xlsx</span><span class="ml-auto text-[10px] font-bold bg-amber-50 text-amber-600 px-2 py-0.5 rounded">DP</span>
                      </div>
                    </div>
                    <!-- Equipe -->
                    <div v-else-if="cap.mockup === 'team'" class="space-y-3">
                      <div class="flex items-center gap-3"><div class="size-8 rounded-full bg-[#19341a] text-white text-xs font-bold flex items-center justify-center">AC</div><div class="flex-1"><div class="flex justify-between text-xs mb-1"><span>Ana Costa</span><span class="text-[#ff8a65] font-bold">7 tarefas</span></div><div class="h-2 rounded-full bg-gray-100"><div class="h-2 rounded-full bg-[#ff8a65] w-[87%]"></div></div></div></div>
                      <div class="flex items-center gap-3"><div class="size-8 rounded-full bg-[#19341a] text-white text-xs font-bold flex items-center justify-center">RB</div><div class="flex-1"><div class="flex justify-between text-xs mb-1"><span>Rafael B.</span><span class="text-gray-400 font-bold">3 tarefas</span></div><div class="h-2 rounded-full bg-gray-100"><div class="h-2 rounded-full bg-[#19341a] w-[37%]"></div></div></div></div>
                    </div>
                    <!-- Sync -->
                    <div v-else-if="cap.mockup === 'sync'" class="text-center py-4">
                      <div class="inline-flex items-center gap-3 rounded-xl border border-gray-100 bg-white px-6 py-4">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ff8a65" stroke-width="2"><path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/><path d="M12 7v5l3 3"/></svg>
                        <span class="font-mono text-sm text-gray-500">.ics feed ativo</span>
                        <span class="font-mono text-xs bg-green-50 text-green-600 px-2 py-0.5 rounded">Sincronizando</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- MÉTODO (Linha do tempo técnica) -->
      <section id="metodo" class="relative bg-[#f8fafc] border-y border-gray-100">
        <div class="mx-auto max-w-[1200px] px-6 py-24">
          <div v-fade-in class="mb-12 max-w-[760px]">
            <span class="font-mono text-xs uppercase tracking-[0.12em] text-[#ff8a65]">Como funciona</span>
            <h2 class="text-[clamp(28px,3vw,40px)] font-bold tracking-[-0.03em] mt-3.5">Quatro passos para o controle total</h2>
            <p class="mt-4 text-gray-500 text-lg">Do cadastro do cliente à entrega da obrigação, sem correria e sem perder prazos.</p>
          </div>

          <!-- Cards dos passos (Grid 2x2) -->
          <div class="grid grid-cols-1 gap-4 md:grid-cols-2 max-w-4xl">
            <div v-for="(step, i) in steps" :key="step.num" v-fade-in class="relative flex flex-col overflow-hidden rounded-2xl p-7 border" :class="i === 3 ? 'bg-[#ff8a65] text-white border-transparent shadow-lg shadow-[#ff8a65]/20' : 'bg-white border-gray-100'">
              <div class="flex items-center justify-between">
                <span class="font-mono text-xs tracking-[0.12em]" :class="i === 3 ? 'text-white/80' : 'text-[#ff8a65]'">PASSO {{ step.num }}</span>
                <span class="rounded-full border px-3 py-1 font-mono text-[10px] uppercase tracking-[0.1em]" :class="i === 3 ? 'border-white/20 text-white/80' : 'border-gray-200 text-gray-400'">fluxo do escritório</span>
              </div>
              <h3 class="mt-3 text-xl font-medium tracking-tight" :class="i === 3 ? 'text-white' : 'text-[#19341a]'">{{ step.title }}</h3>
              <p class="mt-2 text-sm leading-relaxed" :class="i === 3 ? 'text-white/80' : 'text-gray-500'">{{ step.desc }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- CASOS -->
      <section id="casos" class="relative bg-white border-y border-gray-100">
        <div class="mx-auto max-w-[1200px] px-6 py-24">
          <div v-fade-in class="mb-12 max-w-[760px]">
            <span class="font-mono text-xs uppercase tracking-[0.12em] text-[#ff8a65]">Casos</span>
            <h2 class="text-[clamp(28px,3vw,40px)] font-bold tracking-[-0.03em] mt-3.5">O que muda na operação dos escritórios</h2>
          </div>
          <!-- Featured Case -->
          <div class="mb-4" v-fade-in>
            <article class="relative grid overflow-hidden rounded-2xl bg-[#19341a] lg:grid-cols-[1.15fr_0.85fr]">
              <div class="absolute inset-0 bg-[linear-gradient(to_right,#ffffff08_1px,transparent_1px),linear-gradient(to_bottom,#ffffff08_1px,transparent_1px)] bg-[size:24px_24px] opacity-30"></div>
              <div class="relative z-10 flex flex-col justify-between gap-10 p-9 lg:p-12">
                <div>
                  <span class="font-mono text-xs uppercase tracking-[0.12em] text-[#ff8a65]">Escritório · em destaque</span>
                  <blockquote class="mt-5 text-[clamp(22px,2.3vw,32px)] font-normal leading-[1.3] tracking-[-0.02em] text-white">"A automação de recorrência do ContablyTask deu nome e número ao que a planilha não enxergava. Cada tarefa concluída virou a do próximo mês, sem eu precisar lembrar."</blockquote>
                </div>
                <div class="flex flex-wrap items-end justify-between gap-6">
                  <div class="flex items-center gap-3.5">
                    <div class="flex size-11 items-center justify-center rounded-full bg-white/10 text-sm font-semibold text-white">EC</div>
                    <div>
                      <div class="text-sm font-semibold text-white">Contabilidade</div>
                      <div class="text-xs text-white/60">escritório contábil</div>
                    </div>
                  </div>
                  <div class="rounded-xl border border-white/12 bg-white/5 px-4 py-2.5">
                    <div class="font-mono text-xs uppercase tracking-[0.1em] text-[#ff8a65]">Contrato ativo</div>
                    <div class="text-sm font-medium text-white">desde 2026</div>
                  </div>
                </div>
              </div>
              <div class="relative min-h-[260px] overflow-hidden bg-[#0f2010] flex items-center justify-center p-9">
                <div class="grid grid-cols-2 gap-3 w-full max-w-xs">
                  <div class="rounded-xl border border-white/10 bg-white/5 p-4"><div class="text-2xl font-bold text-white">20</div><div class="text-xs text-white/50">Clientes</div></div>
                  <div class="rounded-xl border border-white/10 bg-white/5 p-4"><div class="text-2xl font-bold text-[#ff8a65]">0</div><div class="text-xs text-white/50">Atrasos</div></div>
                  <div class="rounded-xl border border-white/10 bg-white/5 p-4"><div class="text-2xl font-bold text-white">47</div><div class="text-xs text-white/50">Tarefas/mês</div></div>
                  <div class="rounded-xl border border-white/10 bg-white/5 p-4"><div class="text-2xl font-bold text-white">5h</div><div class="text-xs text-white/50">Poupadas/sem</div></div>
                </div>
              </div>
            </article>
          </div>
          <!-- Smaller Cases -->
          <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
            <div v-for="c in cases" :key="c.title" v-fade-in class="flex flex-col rounded-2xl border border-gray-100 bg-white p-7 hover:shadow-md transition-all">
              <span class="font-mono text-[10.5px] uppercase tracking-[0.12em] text-[#ff8a65]">{{ c.tag }}</span>
              <h3 class="mt-3 text-base font-medium leading-tight tracking-tight text-[#19341a]">{{ c.title }}</h3>
              <p class="mt-2 text-[13.5px] leading-relaxed text-gray-500">{{ c.desc }}</p>
              <div class="mt-auto border-t border-gray-100 pt-4">
                <span class="text-sm font-medium text-[#19341a]">{{ c.metric }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- PRICING -->
      <section id="pricing" class="relative bg-[#f8fafc] border-y border-gray-100">
        <div class="mx-auto max-w-[1200px] px-6 py-24">
          <div v-fade-in class="text-center mb-16">
            <span class="font-mono text-xs uppercase tracking-[0.12em] text-[#ff8a65]">Planos</span>
            <h2 class="text-[clamp(28px,3vw,40px)] font-bold tracking-[-0.03em] mt-3.5">Comece de graça. Evolua quando precisar.</h2>
            <p class="mt-4 text-gray-500 text-lg">Sem cartão de crédito para começar.</p>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4 items-start">
            <div v-for="p in plans" :key="p.name" v-fade-in class="bg-white p-8 rounded-2xl border transition-all hover:shadow-lg" :class="p.featured ? 'border-[#ff8a65] shadow-xl md:scale-105' : 'border-gray-100'">
              <div v-if="p.featured" class="bg-[#ff8a65] text-white text-xs font-bold px-3 py-1 rounded-full inline-block mb-4">Mais popular</div>
              <h3 class="font-mono text-xs uppercase tracking-[0.12em] text-gray-400 mb-3">{{ p.name }}</h3>
              <div class="flex items-end gap-1 mb-1">
                <span class="text-lg font-bold text-gray-400 mb-1">R$</span>
                <span class="text-4xl font-extrabold text-[#19341a] tracking-tight">{{ p.price }}</span>
              </div>
              <p class="text-xs text-gray-400 mb-6">{{ p.desc }}</p>
              <ul class="space-y-3 mb-8 border-t border-gray-100 pt-6">
                <li v-for="f in p.features" :key="f" class="text-sm text-gray-600 flex items-start gap-2">
                  <svg class="w-4 h-4 text-[#ff8a65] mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path></svg>
                  {{ f }}
                </li>
              </ul>
              <RouterLink to="/cadastro" class="block w-full text-center py-3 rounded-xl font-bold text-sm transition-all" :class="p.featured ? 'bg-[#ff8a65] text-white hover:bg-[#f07047]' : 'bg-gray-50 text-[#19341a] hover:bg-gray-100'">{{ p.cta }}</RouterLink>
            </div>
          </div>
        </div>
      </section>

      <!-- CTA FINAL (Orb flutuante) -->
      <section class="bg-white px-3 pb-3">
        <div class="relative isolate overflow-hidden rounded-[28px] bg-[#19341a] px-6 py-20 md:py-28">
          <div class="absolute inset-0 bg-[linear-gradient(to_right,#ffffff08_1px,transparent_1px),linear-gradient(to_bottom,#ffffff08_1px,transparent_1px)] bg-[size:32px_32px] opacity-40"></div>
          <div class="animate-float absolute -top-24 left-1/2 h-[34rem] w-[34rem] -translate-x-1/2 bg-[#ff8a65]/20 rounded-full blur-[80px]"></div>
          <div class="absolute inset-0" style="background:radial-gradient(120% 80% at 50% 0%, transparent 40%, rgba(25,52,26,.6) 100%)"></div>
          
          <div class="relative mx-auto flex max-w-[820px] flex-col items-center text-center">
            <span class="font-mono text-xs uppercase tracking-[0.12em] text-[#ff8a65]">Fale com a gente</span>
            <h2 class="mt-5 text-[clamp(30px,4vw,52px)] font-semibold leading-[1.06] tracking-[-0.035em] text-white">
              O que a gente defende, a gente já está <span class="bg-gradient-to-r from-[#ff8a65] to-white bg-clip-text text-transparent">fazendo</span>.
            </h2>
            <p class="mt-5 max-w-[560px] text-lg leading-relaxed text-white/70">Comece pelo plano gratuito. Se a ferramenta não fizer sentido pro seu escritório, você não perde nada.</p>
            <div class="mt-9 flex flex-wrap items-center justify-center gap-3">
              <RouterLink to="/cadastro" class="inline-flex items-center gap-2 rounded-xl bg-white px-7 py-3.5 text-sm font-semibold text-[#19341a] shadow-lg transition-all hover:bg-gray-100">
                Criar conta grátis <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
              </RouterLink>
              <a href="#metodo" class="inline-flex items-center rounded-xl border border-white/25 px-6 py-3.5 text-sm font-semibold text-white transition-all hover:bg-white/10">Como funciona</a>
            </div>
            <div class="mt-10 flex flex-wrap items-center justify-center gap-x-3 gap-y-2">
              <span class="rounded-full border border-white/12 bg-white/5 px-3.5 py-1.5 font-mono text-[11px] uppercase tracking-[0.08em] text-white/65">Plano gratuito para sempre</span>
              <span class="rounded-full border border-white/12 bg-white/5 px-3.5 py-1.5 font-mono text-[11px] uppercase tracking-[0.08em] text-white/65">Sem cartão de crédito</span>
              <span class="rounded-full border border-white/12 bg-white/5 px-3.5 py-1.5 font-mono text-[11px] uppercase tracking-[0.08em] text-white/65">Suporte em português</span>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- FOOTER -->
    <footer class="relative overflow-hidden bg-[#19341a] text-white">
      <div class="absolute inset-0 bg-[linear-gradient(to_right,#ffffff08_1px,transparent_1px),linear-gradient(to_bottom,#ffffff08_1px,transparent_1px)] bg-[size:32px_32px] opacity-30"></div>
      <div class="absolute -left-40 -top-32 h-[30rem] w-[30rem] bg-[#ff8a65]/10 rounded-full blur-[80px]"></div>
      
      <div class="relative mx-auto max-w-[1200px] px-6 pt-20">
        <div class="grid gap-12 md:grid-cols-2 lg:grid-cols-[1.5fr_1fr_1fr_1fr]">
          <div>
            <a href="/" class="inline-flex items-center gap-2.5">
              <div class="w-9 h-9 rounded-[10px] bg-white/10 flex items-center justify-center">
                <svg viewBox="0 0 24 24" fill="none" stroke="#ff8a65" stroke-width="2.5" class="w-5 h-5"><path d="M9 11l3 3L22 4" /><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" /></svg>
              </div>
              <span class="text-2xl font-extrabold tracking-tight">ContablyTask</span>
            </a>
            <p class="mt-4 max-w-[300px] text-sm leading-relaxed text-white/70">O hub operacional para escritórios contábeis. Centralize clientes, obrigações e documentos num só lugar.</p>
          </div>
          <div>
            <h5 class="mb-4 font-mono text-xs font-medium uppercase tracking-[0.12em] text-white/50">Capacidades</h5>
            <a href="#capacidades" class="block py-1.5 text-sm text-white/75 hover:text-white transition-colors">Calendário</a>
            <a href="#capacidades" class="block py-1.5 text-sm text-white/75 hover:text-white transition-colors">Workflow</a>
            <a href="#capacidades" class="block py-1.5 text-sm text-white/75 hover:text-white transition-colors">Clientes</a>
            <a href="#capacidades" class="block py-1.5 text-sm text-white/75 hover:text-white transition-colors">Documentos</a>
            <a href="#capacidades" class="block py-1.5 text-sm text-white/75 hover:text-white transition-colors">Equipe</a>
          </div>
          <div>
            <h5 class="mb-4 font-mono text-xs font-medium uppercase tracking-[0.12em] text-white/50">A casa</h5>
            <a href="#metodo" class="block py-1.5 text-sm text-white/75 hover:text-white transition-colors">Como funciona</a>
            <a href="#casos" class="block py-1.5 text-sm text-white/75 hover:text-white transition-colors">Casos</a>
            <a href="#pricing" class="block py-1.5 text-sm text-white/75 hover:text-white transition-colors">Planos</a>
          </div>
          <div>
            <h5 class="mb-4 font-mono text-xs font-medium uppercase tracking-[0.12em] text-white/50">Contato</h5>
            <a href="/cadastro" class="block py-1.5 text-sm text-white/75 hover:text-white transition-colors">Criar conta</a>
            <a href="/login" class="block py-1.5 text-sm text-white/75 hover:text-white transition-colors">Login</a>
          </div>
        </div>
        
        <!-- Logo gigante no rodapé -->
        <div class="pointer-events-none mt-16 select-none overflow-hidden">
          <div class="bg-gradient-to-b from-white/[0.07] to-white/0 bg-clip-text text-transparent">
            <span class="block text-[clamp(60px,14vw,200px)] font-extrabold lowercase leading-[0.82] tracking-[-0.04em]">ContablyTask</span>
          </div>
        </div>
        
        <div class="flex flex-wrap items-center justify-between gap-4 border-t border-white/10 py-7">
          <p class="text-xs text-white/55">© 2026 ContablyTask. Todos os direitos reservados.</p>
          <div class="flex gap-6">
            <a href="#" class="text-xs text-white/55 hover:text-white transition-colors">Privacidade</a>
            <a href="#" class="text-xs text-white/55 hover:text-white transition-colors">Termos</a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
html { scroll-behavior: smooth; }

@keyframes float {
  0%, 100% { transform: translate(-50%, 0); }
  50% { transform: translate(-50%, -20px); }
}
.animate-float {
  animation: float 6s ease-in-out infinite;
}
</style>