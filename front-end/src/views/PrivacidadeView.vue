<script setup lang="ts">
import PublicLayout from '@/components/PublicLayout.vue'
</script>

<template>
  <PublicLayout>
    <main class="bg-white py-10 sm:py-14">
      <article
        class="mx-auto w-[min(100%-2rem,48rem)] overflow-hidden rounded-xl border border-[var(--ct-border)] bg-white"
      >
        <header class="bg-[var(--ct-navy)] px-7 py-9 text-white sm:px-11">
          <p class="text-xs font-semibold uppercase tracking-[0.12em] text-[var(--ct-accent)]">
            Transparência e dados pessoais
          </p>
          <h1 class="mt-3 text-3xl font-semibold tracking-tight">Política de Privacidade</h1>
          <p class="mt-3 text-sm text-white/70">
            Última atualização: agosto de 2026 · Práticas orientadas pela LGPD
          </p>
        </header>

        <div class="space-y-9 p-7 text-sm leading-7 text-[var(--ct-text)] sm:p-11 sm:text-base">
          <section>
            <h2 class="text-xl font-semibold tracking-tight text-[var(--ct-ink)]">
              1. Papéis e responsabilidades
            </h2>
            <p class="mt-3">
              A ContablyTask trata os dados de cadastro necessários para prestar e administrar o
              serviço. Quando um escritório insere informações de seus próprios clientes, o
              escritório atua como controlador desses dados e a ContablyTask atua como operadora,
              processando-os para disponibilizar as funcionalidades contratadas.
            </p>
          </section>

          <section>
            <h2 class="text-xl font-semibold tracking-tight text-[var(--ct-ink)]">
              2. Dados tratados
            </h2>
            <ul class="mt-3 list-disc space-y-2 pl-5">
              <li>
                <strong class="text-[var(--ct-ink)]">Cadastro do escritório:</strong> nome, e-mail,
                nome do escritório e CPF ou CNPJ informado pelo responsável.
              </li>
              <li>
                <strong class="text-[var(--ct-ink)]">Uso da plataforma:</strong> clientes, tarefas,
                responsáveis, vencimentos e documentos enviados pelos usuários autorizados.
              </li>
              <li>
                <strong class="text-[var(--ct-ink)]">Dados técnicos:</strong> endereço IP,
                navegador, registros de acesso e cookies essenciais. Medição de audiência só é
                ativada após o aceite de cookies opcionais.
              </li>
              <li>
                <strong class="text-[var(--ct-ink)]">Pagamento:</strong> informações necessárias à
                criação e gestão da assinatura. Os dados do meio de pagamento são tratados no
                checkout do provedor de cobrança.
              </li>
            </ul>
          </section>

          <section>
            <h2 class="text-xl font-semibold tracking-tight text-[var(--ct-ink)]">
              3. Finalidades
            </h2>
            <p class="mt-3">
              Utilizamos os dados para criar e proteger contas, entregar as funções da plataforma,
              processar assinaturas, atender solicitações, prevenir abuso, comunicar alterações
              importantes e cumprir obrigações legais. A ContablyTask não comercializa dados
              pessoais para publicidade.
            </p>
          </section>

          <section>
            <h2 class="text-xl font-semibold tracking-tight text-[var(--ct-ink)]">
              4. Serviços utilizados
            </h2>
            <p class="mt-3">
              Para operar o produto, utilizamos fornecedores especializados, incluindo Supabase para
              autenticação e armazenamento, Asaas para cobrança, Cloudflare Turnstile para prevenção
              de abuso e Google Analytics para métricas opcionais. Cada serviço trata somente os
              dados necessários à sua função e conforme suas próprias condições de privacidade.
            </p>
          </section>

          <section>
            <h2 class="text-xl font-semibold tracking-tight text-[var(--ct-ink)]">
              5. Segurança e acesso
            </h2>
            <p class="mt-3">
              A comunicação com a plataforma utiliza HTTPS/TLS. A autenticação é administrada pelo
              provedor de identidade, sem armazenamento de senhas em texto legível pela aplicação.
              As consultas são limitadas ao escritório autenticado, e downloads de documentos são
              liberados por links assinados com validade temporária. Arquivos também passam por
              validações de formato, conteúdo e tamanho antes do armazenamento.
            </p>
          </section>

          <section>
            <h2 class="text-xl font-semibold tracking-tight text-[var(--ct-ink)]">
              6. Retenção e exclusão
            </h2>
            <p class="mt-3">
              Os dados são mantidos enquanto a conta estiver ativa e pelo período necessário para
              cumprir a prestação do serviço e obrigações aplicáveis. Solicitações de acesso,
              correção, portabilidade ou exclusão são analisadas individualmente. Algumas
              informações podem ser preservadas quando houver obrigação legal ou necessidade de
              proteção contra fraude e exercício regular de direitos.
            </p>
          </section>

          <section>
            <h2 class="text-xl font-semibold tracking-tight text-[var(--ct-ink)]">
              7. Seus direitos e contato
            </h2>
            <p class="mt-3">
              Para solicitar confirmação de tratamento, acesso, correção, portabilidade, informação
              sobre compartilhamento ou exclusão, escreva para
              <a
                class="font-semibold text-[var(--ct-primary)] underline"
                href="mailto:suporte@contablytask.com.br"
              >
                suporte@contablytask.com.br</a
              >. Poderemos solicitar informações adicionais para confirmar a identidade e proteger a
              conta antes de atender ao pedido.
            </p>
          </section>
        </div>
      </article>
    </main>
  </PublicLayout>
</template>
