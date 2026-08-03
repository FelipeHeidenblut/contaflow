<template>
  <div
    class="min-h-screen bg-[var(--ct-bg)] px-4 py-12 selection:bg-[var(--ct-primary)] selection:text-white sm:px-6 lg:px-8"
  >
    <div
      class="mx-auto max-w-4xl overflow-hidden rounded-3xl border border-[var(--ct-border)] bg-white shadow-[0_15px_40px_rgba(15,23,42,0.07)]"
    >
      <!-- Cabeçalho -->
      <div class="bg-[var(--ct-navy)] px-8 py-10 sm:px-12">
        <h1 class="mb-2 text-3xl font-extrabold tracking-tight text-white">
          Termos de Uso
        </h1>
        <p class="text-sm text-white/65">
          Última atualização: Junho de 2026 · Ao usar a ContablyTask, você concorda com estes termos
        </p>
      </div>

      <!-- Conteúdo -->
      <div class="space-y-8 p-8 leading-relaxed text-[var(--ct-text)] sm:p-12">
        <section>
          <h2 class="mb-3 text-xl font-bold tracking-tight text-[var(--ct-ink)]">
            1. Aceitação dos termos
          </h2>
          <p>
            Ao acessar, navegar ou utilizar a plataforma
            <strong class="text-[var(--ct-ink)]">ContablyTask</strong>, você concorda em cumprir estes
            Termos de Uso e a nossa Política de Privacidade. Se não concordar com qualquer parte destes
            termos, não deverá acessar ou utilizar os serviços.
          </p>
        </section>

        <section>
          <h2 class="mb-3 text-xl font-bold tracking-tight text-[var(--ct-ink)]">
            2. Descrição do serviço
          </h2>
          <p>
            A ContablyTask é uma plataforma SaaS desenvolvida para apoiar escritórios de contabilidade e
            profissionais da área na centralização e gestão de clientes, obrigações e documentos.
            O sistema é fornecido de forma contínua, sujeito a atualizações, melhorias e manutenções
            programadas.
          </p>
        </section>

        <section>
          <h2 class="mb-3 text-xl font-bold tracking-tight text-[var(--ct-ink)]">
            3. Responsabilidades do usuário
          </h2>
          <ul class="mt-2 list-disc space-y-2 pl-5">
            <li>Fornecer informações verdadeiras, exatas e atualizadas no momento do cadastro.</li>
            <li>Manter a confidencialidade da senha e das credenciais de acesso da conta.</li>
            <li>Não utilizar a plataforma para fins ilegais, fraudulentos ou contrários a estes termos.</li>
            <li>
              Garantir que possui base legal para inserir e tratar os dados de seus clientes na plataforma,
              atuando como <strong class="text-[var(--ct-ink)]">controlador</strong> desses dados,
              enquanto a <strong class="text-[var(--ct-ink)]">ContablyTask atua como operadora</strong>
              técnica no contexto da prestação do serviço.
            </li>
          </ul>
        </section>

        <section>
          <h2 class="mb-3 text-xl font-bold tracking-tight text-[var(--ct-ink)]">
            4. Pagamentos e cancelamento
          </h2>
          <p>
            O uso de planos pagos pode exigir o fornecimento de dados de pagamento válidos.
            Assinaturas podem ser cobradas de forma recorrente, conforme o plano contratado, e renovadas
            automaticamente até cancelamento. Condições comerciais, prazos, testes gratuitos, reembolsos
            e regras de cancelamento devem seguir a oferta vigente apresentada ao usuário no momento da contratação.
          </p>
        </section>

        <section>
          <h2 class="mb-3 text-xl font-bold tracking-tight text-[var(--ct-ink)]">
            5. Propriedade intelectual
          </h2>
          <p>
            O código-fonte, o design, a arquitetura, as marcas, os logotipos e os demais elementos
            originais da ContablyTask são protegidos por direitos de propriedade intelectual.
            O uso da plataforma concede ao usuário apenas uma licença limitada, não exclusiva e
            intransferível para utilização do software dentro das finalidades previstas no serviço.
          </p>
        </section>

        <section>
          <h2 class="mb-3 text-xl font-bold tracking-tight text-[var(--ct-ink)]">
            6. Limitação de responsabilidade
          </h2>
          <p>
            A ContablyTask é uma ferramenta de organização e gestão operacional.
            Ela não substitui a responsabilidade técnica, contábil, fiscal ou legal do profissional
            responsável. Na máxima medida permitida pela legislação aplicável, a plataforma não responde
            por danos indiretos, perdas decorrentes de uso inadequado, falhas de cadastro de informações
            ou decisões tomadas exclusivamente com base nos dados inseridos pelo usuário.
          </p>
        </section>

        <section>
          <h2 class="mb-3 text-xl font-bold tracking-tight text-[var(--ct-ink)]">
            7. Modificações nos termos
          </h2>
          <p>
            Estes Termos de Uso podem ser modificados para refletir alterações legais, operacionais
            ou funcionais da plataforma. A versão atualizada passará a valer a partir de sua publicação
            nesta página, observados os requisitos legais aplicáveis.
          </p>
        </section>
      </div>

      <!-- Rodapé -->
      <div class="border-t border-[var(--ct-border)] bg-[var(--ct-bg)] px-8 py-6 text-center sm:px-12">
        <button
          @click="$router.back()"
          class="inline-flex items-center gap-2 rounded-2xl border border-[var(--ct-border)] bg-white px-6 py-2.5 text-sm font-bold text-[var(--ct-ink)] shadow-sm transition-all hover:border-[var(--ct-primary)] hover:text-[var(--ct-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--ct-primary)] focus:ring-offset-2"
        >
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Voltar
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Página estática
</script>

<style scoped>
:global(:root) {
  --ct-bg: #F8FAFC;
  --ct-surface: #FFFFFF;
  --ct-border: #E2E8F0;

  --ct-ink: #0F172A;
  --ct-text: rgba(15, 23, 42, 0.78);
  --ct-text-muted: #64748B;

  --ct-primary: #2563EB;
  --ct-primary-hover: #1D4ED8;
  --ct-primary-soft: #DBEAFE;
  --ct-navy: #172554;
}
</style>