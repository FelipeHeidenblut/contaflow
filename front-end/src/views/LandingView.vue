<script setup lang="ts">
const handleSubmit = (e: Event) => {
  e.preventDefault()
  alert('Obrigado pelo interesse! Entraremos em contato em breve.')
}
</script>

<template>
  <div class="bg-white text-slate-800">
    <!-- NAVEGAÇÃO -->
    <nav class="fixed top-0 w-full bg-white/80 backdrop-blur-md z-50 border-b border-slate-100">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <span class="text-2xl font-black tracking-tight text-slate-900"
            >Conta<span class="text-indigo-600">Flow</span>.</span
          >
          <div class="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600">
            <a href="#funcionalidades" class="hover:text-indigo-600 transition-colors"
              >Funcionalidades</a
            >
            <a href="#planos" class="hover:text-indigo-600 transition-colors">Planos</a>
            <a href="#contato" class="hover:text-indigo-600 transition-colors">Contato</a>
          </div>
          <div class="flex items-center gap-4">
            <a
              href="/login"
              class="text-sm font-medium text-slate-600 hover:text-indigo-600 transition-colors"
              >Login</a
            >
            <a
              href="/cadastro"
              class="bg-indigo-600 text-white text-sm font-semibold py-2 px-4 rounded-lg hover:bg-indigo-700 transition-colors shadow-sm"
              >Começar Grátis</a
            >
          </div>
        </div>
      </div>
    </nav>

    <!-- HERO -->
    <header class="pt-24 pb-16 md:pt-32 md:pb-24 bg-slate-50 overflow-hidden">
      <div
        class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center gap-12"
      >
        <div class="md:w-1/2 text-center md:text-left">
          <h1
            class="text-4xl md:text-5xl lg:text-6xl font-black tracking-tight text-slate-900 leading-tight mb-6"
          >
            Software contábil para <span class="text-indigo-600">gestão de escritórios</span> sem
            retrabalho
          </h1>
          <p class="text-lg md:text-xl text-slate-600 mb-8 max-w-2xl mx-auto md:mx-0">
            Chega de prazos perdidos e informações espalhadas. O ContaFlow centraliza clientes,
            obrigações e documentos em um só lugar.
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center md:justify-start">
            <a
              href="/cadastro"
              class="bg-indigo-600 text-white font-semibold py-3 px-8 rounded-lg hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-500/30"
              >Teste Grátis por 14 Dias</a
            >
            <a
              href="#funcionalidades"
              class="bg-white text-slate-700 font-semibold py-3 px-8 rounded-lg border border-slate-200 hover:border-indigo-300 hover:text-indigo-600 transition-colors shadow-sm"
              >Ver Funcionalidades</a
            >
          </div>
        </div>
        <div class="md:w-1/2 relative">
          <div
            class="bg-white p-4 rounded-2xl shadow-2xl border border-slate-100 rotate-1 hover:rotate-0 transition-transform duration-500"
          >
            <div
              class="bg-slate-100 rounded-lg h-64 md:h-96 flex items-center justify-center text-slate-400"
            >
              <img
                src="/dashboard.png"
                alt="Dashboard do ContaFlow"
                class="rounded-lg w-full h-auto shadow-sm"
              />
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- PROBLEMA -->
    <section class="py-16 md:py-24 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 class="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
          O caos da burocracia não pode ser o padrão
        </h2>
        <p class="text-lg text-slate-600 max-w-3xl mx-auto mb-12">
          A pressão por cumprir obrigações como ECD e ECF é enorme. Informações espalhadas geram
          retrabalho e risco de erros.
        </p>
        <div class="grid md:grid-cols-3 gap-8">
          <div class="p-6 border border-red-100 bg-red-50/50 rounded-xl">
            <div class="text-3xl mb-3">🤯</div>
            <h3 class="font-bold text-slate-900 mb-2">Informações Espalhadas</h3>
            <p class="text-slate-600 text-sm">
              Planilhas e e-mails que se perdem e geram dupla digitação.
            </p>
          </div>
          <div class="p-6 border border-red-100 bg-red-50/50 rounded-xl">
            <div class="text-3xl mb-3">⏰</div>
            <h3 class="font-bold text-slate-900 mb-2">Prazos no Limite</h3>
            <p class="text-slate-600 text-sm">
              Medo constante de atrasar obrigações e gerar multas.
            </p>
          </div>
          <div class="p-6 border border-red-100 bg-red-50/50 rounded-xl">
            <div class="text-3xl mb-3">📉</div>
            <h3 class="font-bold text-slate-900 mb-2">Falta de Visibilidade</h3>
            <p class="text-slate-600 text-sm">
              Impossível saber o status real das entregas sem cobrar a equipe.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- FUNCIONALIDADES -->
    <section id="funcionalidades" class="py-16 md:py-24 bg-slate-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h2 class="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
            Tudo que você precisa para organizar a operação
          </h2>
          <p class="text-lg text-slate-600 max-w-2xl mx-auto">
            O ContaFlow complementa sua contabilidade, dando o controle de volta para as suas mãos.
          </p>
        </div>
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div
            class="bg-white p-6 rounded-xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow"
          >
            <div
              class="h-12 w-12 bg-indigo-100 rounded-lg flex items-center justify-center mb-4 text-indigo-600 font-bold text-xl"
            >
              1
            </div>
            <h3 class="text-lg font-bold text-slate-900 mb-2">Cadastro de Clientes</h3>
            <p class="text-slate-600 text-sm">
              Centralize dados, status e responsáveis internos em um lugar seguro.
            </p>
          </div>
          <div
            class="bg-white p-6 rounded-xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow"
          >
            <div
              class="h-12 w-12 bg-indigo-100 rounded-lg flex items-center justify-center mb-4 text-indigo-600 font-bold text-xl"
            >
              2
            </div>
            <h3 class="text-lg font-bold text-slate-900 mb-2">Gestão de Pendências</h3>
            <p class="text-slate-600 text-sm">
              Organize checklists por cliente com prioridades claras e documentação anexa.
            </p>
          </div>
          <div
            class="bg-white p-6 rounded-xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow"
          >
            <div
              class="h-12 w-12 bg-indigo-100 rounded-lg flex items-center justify-center mb-4 text-indigo-600 font-bold text-xl"
            >
              3
            </div>
            <h3 class="text-lg font-bold text-slate-900 mb-2">Agenda de Prazos</h3>
            <p class="text-slate-600 text-sm">
              Visualize obrigações (ECD, ECF) e receba alertas para evitar atrasos e multas.
            </p>
          </div>
          <div
            class="bg-white p-6 rounded-xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow"
          >
            <div
              class="h-12 w-12 bg-indigo-100 rounded-lg flex items-center justify-center mb-4 text-indigo-600 font-bold text-xl"
            >
              4
            </div>
            <h3 class="text-lg font-bold text-slate-900 mb-2">Repositório de Documentos</h3>
            <p class="text-slate-600 text-sm">
              Armazene arquivos por cliente e obrigação com acesso rápido e seguro.
            </p>
          </div>
          <div
            class="bg-white p-6 rounded-xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow"
          >
            <div
              class="h-12 w-12 bg-indigo-100 rounded-lg flex items-center justify-center mb-4 text-indigo-600 font-bold text-xl"
            >
              5
            </div>
            <h3 class="text-lg font-bold text-slate-900 mb-2">Dashboard de Visão Geral</h3>
            <p class="text-slate-600 text-sm">
              Saiba instantaneamente o status: pendências, atrasos e clientes críticos.
            </p>
          </div>
          <div
            class="bg-white p-6 rounded-xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow"
          >
            <div
              class="h-12 w-12 bg-indigo-100 rounded-lg flex items-center justify-center mb-4 text-indigo-600 font-bold text-xl"
            >
              6
            </div>
            <h3 class="text-lg font-bold text-slate-900 mb-2">Comunicação Interna</h3>
            <p class="text-slate-600 text-sm">
              Histórico de observações no cartão do cliente para reduzir perda de contexto.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- PLANOS -->
    <section id="planos" class="py-16 md:py-24 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 class="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
          Planos para escritórios em crescimento
        </h2>
        <p class="text-lg text-slate-600 mb-12">Sem surpresas. Cancele quando quiser.</p>
        <div class="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <div
            class="border border-slate-200 rounded-2xl p-8 text-left hover:border-indigo-300 transition-colors shadow-sm"
          >
            <h3 class="text-xl font-bold text-slate-900 mb-2">ContaFlow Início</h3>
            <p class="text-sm text-slate-500 mb-6">
              Ideal para escritórios menores organizando a rotina digital.
            </p>
            <div class="mb-6">
              <span class="text-4xl font-black text-slate-900">R$ 0</span>
              <span class="text-slate-500 text-sm"> /mês durante o Beta</span>
            </div>
            <ul class="space-y-3 mb-8 text-sm text-slate-600">
              <li class="flex items-center gap-2">✅ Até 20 clientes ativos</li>
              <li class="flex items-center gap-2">✅ Gestão de prazos básica</li>
              <li class="flex items-center gap-2">✅ 1 GB de armazenamento</li>
            </ul>
            <a
              href="/cadastro"
              class="block text-center bg-white border border-slate-800 text-slate-800 font-semibold py-3 px-6 rounded-lg hover:bg-slate-800 hover:text-white transition-colors"
              >Começar Grátis</a
            >
          </div>
          <div class="border-2 border-indigo-600 rounded-2xl p-8 text-left relative shadow-lg">
            <span
              class="absolute -top-3 left-1/2 -translate-x-1/2 bg-indigo-600 text-white text-xs font-bold px-3 py-1 rounded-full"
              >POPULAR</span
            >
            <h3 class="text-xl font-bold text-slate-900 mb-2">ContaFlow Pro</h3>
            <p class="text-sm text-slate-500 mb-6">
              Para escritórios que precisam de controle total.
            </p>
            <div class="mb-6">
              <span class="text-4xl font-black text-slate-900">R$ 79</span>
              <span class="text-slate-500 text-sm"> /mês</span>
            </div>
            <ul class="space-y-3 mb-8 text-sm text-slate-600">
              <li class="flex items-center gap-2">🚀 Clientes ilimitados</li>
              <li class="flex items-center gap-2">🚀 Alertas avançados de prazos</li>
              <li class="flex items-center gap-2">🚀 50 GB de armazenamento</li>
              <li class="flex items-center gap-2">🚀 Suporte prioritário</li>
            </ul>
            <a
              href="/cadastro"
              class="block text-center bg-indigo-600 text-white font-semibold py-3 px-6 rounded-lg hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-500/30"
              >Assinar ContaFlow Pro</a
            >
          </div>
        </div>
      </div>
    </section>

    <!-- CTA FINAL -->
    <section id="contato" class="py-16 md:py-24 bg-slate-900 text-white">
      <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 class="text-3xl md:text-4xl font-bold mb-4">Pronto para acabar com o retrabalho?</h2>
        <p class="text-lg text-slate-300 mb-8">
          Junte-se aos primeiros contadores transformando a gestão de seus negócios.
        </p>
        <form
          @submit.prevent="handleSubmit"
          class="flex flex-col sm:flex-row gap-3 max-w-xl mx-auto"
        >
          <input
            type="email"
            placeholder="Seu e-mail corporativo"
            required
            class="flex-1 px-4 py-3 rounded-lg text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            type="submit"
            class="bg-indigo-500 hover:bg-indigo-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors shadow-lg"
          >
            Quero Acesso
          </button>
        </form>
      </div>
    </section>

    <!-- RODAPÉ -->
    <footer class="bg-slate-950 text-slate-400 py-8">
      <div
        class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center gap-4"
      >
        <span class="text-xl font-black text-white"
          >Conta<span class="text-indigo-400">Flow</span>.</span
        >
        <p class="text-sm">&copy; 2024 ContaFlow. Todos os direitos reservados.</p>
        <div class="flex gap-6 text-sm">
          <a href="#" class="hover:text-white transition-colors">Termos</a>
          <a href="#" class="hover:text-white transition-colors">Privacidade</a>
        </div>
      </div>
    </footer>
  </div>
</template>
