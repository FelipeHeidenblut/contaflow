<template>
  <div
    class="min-h-screen bg-gray-900 py-12 px-4 sm:px-6 lg:px-8 selection:bg-indigo-500 selection:text-white"
  >
    <div
      class="max-w-3xl mx-auto bg-gray-800 rounded-xl shadow-xl overflow-hidden border border-gray-700 p-8 sm:p-12"
    >
      <div class="mb-10 border-b border-gray-700 pb-6">
        <h1 class="text-3xl font-bold text-white mb-2">Termos de Uso</h1>
        <p class="text-sm text-gray-400">Última atualização: Junho de 2026</p>
      </div>

      <div class="space-y-8 text-gray-300 leading-relaxed">
        <section>
          <h2 class="text-xl font-semibold text-white mb-3">1. Aceitação dos Termos</h2>
          <p>
            Ao acessar e utilizar o <strong>ContaFlow</strong>, você concorda em cumprir e ficar
            vinculado a estes Termos de Uso. Se você não concordar com qualquer parte destes termos,
            não deverá utilizar nossos serviços.
          </p>
        </section>

        <section>
          <h2 class="text-xl font-semibold text-white mb-3">2. Descrição do Serviço</h2>
          <p>
            O ContaFlow é uma plataforma de Software as a Service (SaaS) desenvolvida para auxiliar
            escritórios e profissionais no gerenciamento de dados e processos. O sistema é fornecido
            "no estado em que se encontra", durante sua fase de testes (Beta).
          </p>
        </section>

        <section>
          <h2 class="text-xl font-semibold text-white mb-3">3. Responsabilidades do Usuário</h2>
          <ul class="list-disc pl-5 space-y-2 mt-2">
            <li>Fornecer informações verdadeiras e exatas no momento do cadastro.</li>
            <li>Manter a confidencialidade de sua senha e credenciais de acesso.</li>
            <li>Não utilizar a plataforma para fins ilegais, fraudulentos ou não autorizados.</li>
            <li>
              Garantir que os dados inseridos (como de seus clientes) possuem base legal para
              tratamento.
            </li>
          </ul>
        </section>

        <section>
          <h2 class="text-xl font-semibold text-white mb-3">4. Propriedade Intelectual</h2>
          <p>
            Todo o código, design, arquitetura e conteúdo do ContaFlow são de propriedade exclusiva
            de seus desenvolvedores. O uso da plataforma não transfere nenhum direito de propriedade
            intelectual ao usuário.
          </p>
        </section>

        <section>
          <h2 class="text-xl font-semibold text-white mb-3">5. Limitação de Responsabilidade</h2>
          <p>
            Por estarmos em fase contínua de desenvolvimento, o ContaFlow não se responsabiliza por
            eventuais instabilidades, perda de dados ou lucros cessantes decorrentes do uso da
            plataforma. Recomendamos que você mantenha backups paralelos de informações sensíveis.
          </p>
        </section>
      </div>

      <div class="mt-10 pt-6 border-t border-gray-700 text-center">
        <button
          @click="$router.back()"
          class="text-indigo-400 hover:text-indigo-300 font-medium transition-colors"
        >
          &larr; Voltar
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Nenhuma lógica complexa é necessária para uma página estática
</script>
