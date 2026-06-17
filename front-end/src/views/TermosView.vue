<template>
  <div class="min-h-screen bg-[#f8f8f8] py-12 px-4 sm:px-6 lg:px-8 selection:bg-[#ff8a65] selection:text-white">
    <div class="max-w-4xl mx-auto bg-white rounded-2xl shadow-[0_15px_40px_rgba(25,52,26,0.07)] border border-gray-100 overflow-hidden">
      
      <!-- Cabeçalho -->
      <div class="bg-[#19341a] px-8 sm:px-12 py-10">
        <h1 class="text-3xl font-extrabold text-white mb-2 tracking-tight">Termos de Uso</h1>
        <p class="text-sm text-white/60">Última atualização: Junho de 2026 · Ao usar o ContablyTask, você concorda com estes termos</p>
      </div>

      <!-- Conteúdo -->
      <div class="p-8 sm:p-12 space-y-8 text-[#2a2a2a]/80 leading-relaxed">
        
        <section>
          <h2 class="text-xl font-bold text-[#19341a] mb-3 tracking-tight">1. Aceitação dos Termos</h2>
          <p>
            Ao acessar, navegar ou utilizar a plataforma <strong class="text-[#19341a]">ContablyTask</strong>, você concorda integralmente em cumprir e ficar vinculado a estes Termos de Uso e à nossa Política de Privacidade. Se você não concordar com qualquer parte destes termos, não deverá acessar ou utilizar nossos serviços.
          </p>
        </section>

        <section>
          <h2 class="text-xl font-bold text-[#19341a] mb-3 tracking-tight">2. Descrição do Serviço</h2>
          <p>
            O ContablyTask é uma plataforma de Software as a Service (SaaS) desenvolvida para auxiliar escritórios de contabilidade e profissionais da área na centralização e gestão de clientes, obrigações fiscais e documentos. O sistema é fornecido "no estado em que se encontra", sujeito a atualizações, melhorias contínuas e manutenções programadas.
          </p>
        </section>

        <section>
          <h2 class="text-xl font-bold text-[#19341a] mb-3 tracking-tight">3. Responsabilidades do Usuário</h2>
          <ul class="list-disc pl-5 space-y-2 mt-2">
            <li>Fornecer informações verdadeiras, exatas e atualizadas no momento do cadastro.</li>
            <li>Manter a total confidencialidade de sua senha e credenciais de acesso, sendo responsável por todas as atividades realizadas em sua conta.</li>
            <li>Não utilizar a plataforma para fins ilegais, fraudulentos ou em desacordo com estes Termos.</li>
            <li>
              Garantir que possui base legal para inserir e tratar os dados de seus clientes na plataforma, atuando você como <strong>Controlador</strong> dos dados de terceiros e o ContablyTask como <strong>Operador</strong> técnico.
            </li>
          </ul>
        </section>

        <section>
          <h2 class="text-xl font-bold text-[#19341a] mb-3 tracking-tight">4. Pagamentos e Cancelamento</h2>
          <p>
            O uso de planos pagos exige o fornecimento de dados de pagamento válidos. As assinaturas são cobradas de forma recorrente (mensal) e serão renovadas automaticamente ao final de cada ciclo, salvo se canceladas pelo usuário dentro do painel ou mediante solicitação à equipe de suporte. Não realizamos reembolsos proporcionais por cancelamentos realizados no meio do ciclo já pago, exceto nos casos previstos em lei.
          </p>
        </section>

        <section>
          <h2 class="text-xl font-bold text-[#19341a] mb-3 tracking-tight">5. Propriedade Intelectual</h2>
          <p>
            Todo o código-fonte, design, arquitetura, marcas, logotipos e conteúdo original do ContablyTask são de propriedade exclusiva de seus criadores. A assinatura ou uso da plataforma concede ao usuário apenas uma licença limitada, não exclusiva e intransferível para utilização do software para fins comerciais internos do seu escritório.
          </p>
        </section>

        <section>
          <h2 class="text-xl font-bold text-[#19341a] mb-3 tracking-tight">6. Limitação de Responsabilidade</h2>
          <p>
            O ContablyTask é uma ferramenta de organização e gestão. Ele não substitui a responsabilidade técnica, fiscal e legal do profissional de contabilidade. Na máxima extensão permitida pela legislação, o ContablyTask não se responsabiliza por lucros cessantes, perda de dados (recomendamos backups paralelos), multas por atraso na entrega de obrigações decorrentes de falha do usuário em cadastrar os prazos, ou danos indiretos resultantes do uso ou da impossibilidade de uso da plataforma.
          </p>
        </section>

        <section>
          <h2 class="text-xl font-bold text-[#19341a] mb-3 tracking-tight">7. Modificações nos Termos</h2>
          <p>
            Reservamo-nos o direito de modificar estes Termos de Uso a qualquer momento para refletir alterações na legislação, nos serviços ou em nossas práticas operacionais. Os termos atualizados entrarão em vigor imediatamente após sua publicação nesta página. O uso continuado da plataforma após tais modificações constitui sua aceitação tácita dos novos termos.
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