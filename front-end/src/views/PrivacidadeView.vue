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
          Política de Privacidade
        </h1>
        <p class="text-sm text-white/65">
          Última atualização: Junho de 2026 · Em conformidade com a LGPD (Lei nº 13.709/2018)
        </p>
      </div>

      <!-- Conteúdo -->
      <div class="space-y-8 p-8 leading-relaxed text-[var(--ct-text)] sm:p-12">
        <section>
          <p>
            A <strong class="text-[var(--ct-ink)]">ContablyTask</strong> compromete-se a proteger a
            privacidade e a segurança dos dados dos escritórios de contabilidade e de seus clientes.
            Esta política descreve como coletamos, usamos, armazenamos e protegemos as informações em
            conformidade com a Lei Geral de Proteção de Dados (LGPD).
          </p>
        </section>

        <section>
          <h2 class="mb-3 text-xl font-bold tracking-tight text-[var(--ct-ink)]">
            1. Dados que coletamos
          </h2>
          <ul class="mt-2 list-disc space-y-2 pl-5">
            <li>
              <strong class="text-[var(--ct-ink)]">Dados de cadastro e acesso:</strong>
              Nome, e-mail, nome do escritório e senhas criptografadas, fornecidos no momento do registro.
            </li>
            <li>
              <strong class="text-[var(--ct-ink)]">Dados de navegação:</strong>
              Endereço IP, tipo de navegador e cookies essenciais de sessão para garantir o funcionamento
              seguro da plataforma.
            </li>
            <li>
              <strong class="text-[var(--ct-ink)]">Dados de terceiros (clientes do escritório):</strong>
              Informações de CNPJ, CPF, razão social e documentos inseridos na plataforma pelos
              administradores do escritório. Nesse contexto, o <strong class="text-[var(--ct-ink)]">escritório de contabilidade atua como controlador</strong>
              dos dados de seus clientes, e a <strong class="text-[var(--ct-ink)]">ContablyTask atua como operadora</strong>,
              processando os dados exclusivamente para a prestação do serviço contratado.
            </li>
          </ul>
        </section>

        <section>
          <h2 class="mb-3 text-xl font-bold tracking-tight text-[var(--ct-ink)]">
            2. Como usamos seus dados
          </h2>
          <p>
            Utilizamos os dados exclusivamente para: (i) permitir o acesso e o funcionamento da
            plataforma; (ii) fornecer suporte técnico; (iii) enviar avisos críticos de segurança e
            atualizações do sistema; e (iv) cumprir obrigações legais.
            <strong class="text-[var(--ct-ink)]">
              A ContablyTask não vende, aluga nem compartilha seus dados para fins publicitários.
            </strong>
          </p>
        </section>

        <section>
          <h2 class="mb-3 text-xl font-bold tracking-tight text-[var(--ct-ink)]">
            3. Armazenamento e segurança
          </h2>
          <p>
            A comunicação entre seu navegador e nossos servidores é protegida por protocolos de
            criptografia, como HTTPS/TLS. As senhas são convertidas em hashes irreversíveis.
            Nossos bancos de dados podem ser hospedados em provedores de nuvem com controles de
            segurança e acesso restrito.
          </p>
        </section>

        <section>
          <h2 class="mb-3 text-xl font-bold tracking-tight text-[var(--ct-ink)]">
            4. Retenção e exclusão de dados
          </h2>
          <p>
            Mantemos seus dados pelo tempo necessário para fornecer os serviços solicitados.
            Caso você cancele sua assinatura ou solicite a exclusão da conta, seus dados primários
            serão removidos dos ambientes ativos, ressalvadas as retenções exigidas por obrigações
            legais, regulatórias ou fiscais.
          </p>
        </section>

        <section>
          <h2 class="mb-3 text-xl font-bold tracking-tight text-[var(--ct-ink)]">
            5. Seus direitos como titular
          </h2>
          <p>
            Você pode solicitar, a qualquer momento, o acesso aos seus dados, a correção de informações
            incompletas ou incorretas, a portabilidade dos dados e a eliminação dos dados pessoais
            armazenados em nossa plataforma, observadas as hipóteses legais aplicáveis.
          </p>
        </section>

        <section>
          <h2 class="mb-3 text-xl font-bold tracking-tight text-[var(--ct-ink)]">
            6. Contato
          </h2>
          <p>
            Para exercer seus direitos ou tirar dúvidas sobre privacidade, entre em contato pelo e-mail:
            <a
              href="mailto:fheidenblut@gmail.com"
              class="font-semibold text-[var(--ct-primary)] underline transition-colors hover:text-[var(--ct-primary-hover)] focus:outline-none focus:ring-2 focus:ring-[var(--ct-primary)] focus:ring-offset-2 rounded-sm"
            >
              fheidenblut@gmail.com
            </a>.
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