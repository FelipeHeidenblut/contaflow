<template>
  <div class="min-h-screen bg-[#f8f8f8] py-12 px-4 sm:px-6 lg:px-8 selection:bg-[#ff8a65] selection:text-white">
    <div class="max-w-4xl mx-auto bg-white rounded-2xl shadow-[0_15px_40px_rgba(25,52,26,0.07)] border border-gray-100 overflow-hidden">
      
      <!-- Cabeçalho -->
      <div class="bg-[#19341a] px-8 sm:px-12 py-10">
        <h1 class="text-3xl font-extrabold text-white mb-2 tracking-tight">Política de Privacidade</h1>
        <p class="text-sm text-white/60">Última atualização: Junho de 2026 · Em conformidade com a LGPD (Lei nº 13.709/2018)</p>
      </div>

      <!-- Conteúdo -->
      <div class="p-8 sm:p-12 space-y-8 text-[#2a2a2a]/80 leading-relaxed">
        
        <section>
          <p>
            A <strong class="text-[#19341a]">ContablyTask</strong> compromete-se a proteger a privacidade e a segurança dos dados dos escritórios de contabilidade e de seus clientes. Esta política descreve como coletamos, usamos, armazenamos e protegemos as informações em conformidade com a Lei Geral de Proteção de Dados (LGPD).
          </p>
        </section>

        <section>
          <h2 class="text-xl font-bold text-[#19341a] mb-3 tracking-tight">1. Dados que Coletamos</h2>
          <ul class="list-disc pl-5 space-y-2 mt-2">
            <li>
              <strong>Dados de Cadastro e Acesso:</strong> Nome, e-mail, nome do escritório e senhas criptografadas, fornecidos no momento do registro.
            </li>
            <li>
              <strong>Dados de Navegação:</strong> Endereço IP, tipo de navegador, e cookies essenciais de sessão para garantir o funcionamento seguro da plataforma.
            </li>
            <li>
              <strong>Dados de Terceiros (Clientes do Escritório):</strong> Informações de CNPJ, CPF, razão social e documentos inseridos na plataforma pelos administradores do escritório. Neste contexto, o <strong>escritório de contabilidade atua como Controlador</strong> dos dados de seus clientes, e o <strong>ContablyTask atua como Operador</strong>, processando os dados exclusivamente para prestação do serviço contratado.
            </li>
          </ul>
        </section>

        <section>
          <h2 class="text-xl font-bold text-[#19341a] mb-3 tracking-tight">2. Como Usamos Seus Dados</h2>
          <p>
            Utilizamos os dados exclusivamente para: (i) permitir o acesso e o funcionamento da plataforma; (ii) fornecer suporte técnico; (iii) enviar avisos críticos de segurança e atualizações do sistema; e (iv) cumprir obrigações legais. <strong class="text-[#19341a]">A ContablyTask não vende, aluga nem compartilha seus dados para fins publicitários.</strong>
          </p>
        </section>

        <section>
          <h2 class="text-xl font-bold text-[#19341a] mb-3 tracking-tight">3. Armazenamento e Segurança</h2>
          <p>
            A comunicação entre seu navegador e nossos servidores é protegida por protocolos de criptografia (HTTPS/TLS). As senhas são convertidas em hashes irreversíveis. Nossos bancos de dados estão hospedados em provedores de nuvem de alto padrão de segurança e certificação (ISO 27001), com backups automáticos e controle de acesso restrito.
          </p>
        </section>

        <section>
          <h2 class="text-xl font-bold text-[#19341a] mb-3 tracking-tight">4. Retenção e Exclusão de Dados</h2>
          <p>
            Mantemos seus dados pelo tempo necessário para fornecer os serviços solicitados. Caso você cancele sua assinatura ou solicite a exclusão da conta, seus dados primários serão permanentemente removidos de nossos servidores ativos em até 30 dias, ressalvadas as retenções exigidas por obrigações legais ou fiscais.
          </p>
        </section>

        <section>
          <h2 class="text-xl font-bold text-[#19341a] mb-3 tracking-tight">5. Seus Direitos como Titular (LGPD)</h2>
          <p>
            Você tem o direito de solicitar, a qualquer momento: o acesso aos seus dados, a correção de informações incompletas ou incorretas, a portabilidade dos dados, e a eliminação total dos seus dados pessoais armazenados em nossa plataforma.
          </p>
        </section>

        <section>
          <h2 class="text-xl font-bold text-[#19341a] mb-3 tracking-tight">6. Contato com o Encarregado (DPO)</h2>
          <p>
            Para exercer seus direitos ou tirar dúvidas sobre privacidade, entre em contato com nosso encarregado pelo tratamento de dados pessoais através do e-mail: <a href="mailto:fheidenblut@gmail.com" class="text-[#ff8a65] hover:text-[#f07047] font-semibold">fheidenblut@gmail.com</a>.
          </p>
        </section>

      </div>

      <!-- Rodapé / Botão Voltar -->
      <div class="px-8 sm:px-12 py-6 bg-[#f8f8f8] border-t border-gray-100 text-center">
        <button
          @click="$router.back()"
          class="inline-flex items-center gap-2 bg-white text-[#19341a] border border-gray-200 hover:border-[#19341a] rounded-xl py-2.5 px-6 font-bold text-sm transition-all shadow-sm"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
          Voltar
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Nenhuma lógica complexa é necessária para uma página estática
</script>