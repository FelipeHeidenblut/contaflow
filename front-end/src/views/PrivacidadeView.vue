<template>
  <div
    class="min-h-screen bg-gray-900 py-12 px-4 sm:px-6 lg:px-8 selection:bg-indigo-500 selection:text-white"
  >
    <div
      class="max-w-3xl mx-auto bg-gray-800 rounded-xl shadow-xl overflow-hidden border border-gray-700 p-8 sm:p-12"
    >
      <div class="mb-10 border-b border-gray-700 pb-6">
        <h1 class="text-3xl font-bold text-white mb-2">Política de Privacidade</h1>
        <p class="text-sm text-gray-400">Última atualização: Junho de 2026</p>
      </div>

      <div class="space-y-8 text-gray-300 leading-relaxed">
        <section>
          <p>
            O <strong>ContaFlow</strong> leva a sua privacidade a sério. Esta política descreve como
            coletamos, usamos e protegemos suas informações pessoais, em conformidade com a Lei
            Geral de Proteção de Dados (LGPD - Lei nº 13.709/2018).
          </p>
        </section>

        <section>
          <h2 class="text-xl font-semibold text-white mb-3">1. Dados que Coletamos</h2>
          <ul class="list-disc pl-5 space-y-2 mt-2">
            <li>
              <strong>Dados de Cadastro:</strong> Nome, e-mail e nome da empresa/escritório,
              coletados no momento do registro.
            </li>
            <li>
              <strong>Dados de Uso e Navegação:</strong> Endereço IP, tipo de navegador, cookies
              básicos de sessão e informações de diagnóstico geradas durante o uso do sistema.
            </li>
            <li>
              <strong>Dados de Terceiros:</strong> Informações de clientes que você insere na
              plataforma (você atua como Controlador destes dados e o ContaFlow como Operador).
            </li>
          </ul>
        </section>

        <section>
          <h2 class="text-xl font-semibold text-white mb-3">2. Como Usamos Seus Dados</h2>
          <p>
            Utilizamos os dados exclusivamente para permitir o acesso e funcionamento da plataforma,
            fornecer suporte técnico, enviar avisos de segurança e melhorar a sua experiência no
            sistema. Não vendemos ou repassamos seus dados para terceiros para fins publicitários.
          </p>
        </section>

        <section>
          <h2 class="text-xl font-semibold text-white mb-3">3. Armazenamento e Segurança</h2>
          <p>
            Suas senhas são criptografadas (hashes irreversíveis) e a comunicação entre o seu
            navegador e nossos servidores ocorre através de protocolos seguros (HTTPS). Nossos
            bancos de dados estão hospedados em provedores de nuvem de alto padrão de segurança.
          </p>
        </section>

        <section>
          <h2 class="text-xl font-semibold text-white mb-3">4. Seus Direitos (LGPD)</h2>
          <p>
            Você tem o direito de solicitar o acesso, a correção ou a exclusão total dos seus dados
            pessoais armazenados em nossa plataforma a qualquer momento, bastando entrar em contato
            com nossa equipe ou utilizando a opção de exclusão de conta no painel do usuário.
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
