# ContablyTask

SaaS para gestão da rotina de escritórios contábeis, com frontend Vue e API FastAPI.

## Ambientes

O projeto reconhece quatro ambientes: `development`, `test`, `staging` e `production`.
Cada ambiente deve usar recursos isolados.

| Recurso              | Desenvolvimento            | Homologação             | Produção            |
| -------------------- | -------------------------- | ----------------------- | ------------------- |
| Banco PostgreSQL     | banco local ou exclusivo   | banco exclusivo         | banco exclusivo     |
| Projeto Supabase     | projeto de desenvolvimento | projeto de homologação  | projeto de produção |
| Bucket de documentos | bucket de desenvolvimento  | bucket de homologação   | bucket de produção  |
| Asaas                | sandbox                    | sandbox                 | produção            |
| Frontend e API       | localhost                  | domínios de homologação | domínios oficiais   |

Nunca reutilize `DATABASE_URL`, `SUPABASE_SERVICE_KEY`, bucket ou credenciais do Asaas entre
homologação e produção.

## Execução local

Pré-requisitos: Python 3.11, Node.js 22 e PostgreSQL.

1. Prepare as variáveis sem colocar segredos no Git:

   ```bash
   cp backend/.env.development.example backend/.env
   cp front-end/.env.development.example front-end/.env.local
   ```

2. Preencha as credenciais do projeto Supabase de desenvolvimento e crie o bucket indicado em
   `SUPABASE_STORAGE_BUCKET`.

3. Instale o backend e aplique o schema exclusivamente com Alembic:

   ```bash
   cd backend
   python -m venv venv
   ./venv/bin/python -m pip install -r requirements-dev.txt
   ./venv/bin/python -m alembic upgrade head
   ./venv/bin/python -m uvicorn main:app --reload
   ```

4. Em outro terminal, inicie o frontend:

   ```bash
   cd front-end
   npm ci
   npm run dev
   ```

## Homologação e produção

- Backend: use `.env.staging.example` ou `.env.production.example` como checklist das variáveis da
  plataforma de hospedagem.
- Frontend: configure as variáveis do arquivo correspondente no projeto de preview/produção da
  Vercel. Variáveis `VITE_*` são incorporadas durante o build.
- Execute `alembic upgrade head` contra o banco do ambiente antes de liberar a nova API.
- `CORS_ALLOWED_ORIGINS` aceita uma lista separada por vírgulas e nunca aceita `*`.
- O backend bloqueia localhost e Asaas de produção em homologação.
- Em produção, confirme o nome do bucket já utilizado antes do deploy para não perder acesso aos
  documentos existentes.

### Manter o backend ativo no Render gratuito

O workflow `.github/workflows/backend-keep-alive.yml` chama `GET /health` a cada 5 minutos,
mesmo sem usuários com o site aberto. A rota é pública, retorna `{"status":"ok"}` e não
consulta banco, Supabase ou Asaas. Ela verifica somente se a API está respondendo.

Para ativar:

1. Faça deploy do backend com a rota `/health` e publique o workflow na branch padrão do
   repositório no GitHub.
2. Em **Settings > Secrets and variables > Actions > Variables**, crie a variável de repositório
   `BACKEND_BASE_URL` com a URL pública do backend, por exemplo
   `https://seu-backend.onrender.com` (sem `/health` e sem credenciais).
3. Em **Actions > Manter backend ativo > Run workflow**, execute manualmente e confirme o
   resultado **Backend ativo e respondendo.** Depois, confira as execuções agendadas.

O ping aceita até 90 segundos por tentativa para permitir a inicialização de uma instância
adormecida e tenta novamente em falhas transitórias. Se `/health` responder 404, o workflow
consulta `/` para compatibilidade com deploys antigos e valida a mensagem de status do ContaFlow.
Nos demais casos, `/health` deve retornar HTTP 200 e `{"status":"ok"}`. Uma resposta HTTP
inesperada ou um conteúdo que não corresponda à rota faz a execução falhar.

Se ambas as rotas retornarem 404, confira se `BACKEND_BASE_URL` contém somente a origem HTTPS
do backend, sem `/health`, `/api/v1` ou o domínio do frontend. Após publicar uma correção no
workflow, use **Run workflow** para iniciar uma nova execução com a versão atualizada.

Limitações:

- O [Render gratuito](https://render.com/docs/free) suspende serviços após 15 minutos sem
  tráfego e oferece 750 horas de instância por mês, compartilhadas pelo workspace. Um único
  serviço ativo durante 31 dias consome 744 horas; outros serviços compartilham a mesma cota.
- O [agendamento do GitHub Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)
  pode atrasar ou perder execuções. Em repositórios públicos, é desativado após 60 dias sem
  atividade. Portanto, essa solução reduz a ocorrência de partidas a frio, mas não garante
  disponibilidade contínua.
- São aproximadamente 8.640 execuções em 30 dias. Em repositórios privados, acompanhe a cota
  e o orçamento de minutos do Actions antes de ativar.
- Para usar um monitor HTTP externo no lugar do Actions, configure `GET` para
  `https://seu-backend.onrender.com/health` a cada 5 minutos, esperando HTTP 200 e
  `{"status":"ok"}`. Para desativar o agendamento no GitHub, use **Disable workflow**.

### Convites de membros

O administrador envia um convite por e-mail; a senha é definida pelo próprio funcionário. O backend
usa a primeira origem de `CORS_ALLOWED_ORIGINS` e acrescenta `/redefinir-senha` ao redirecionamento.

Em **Authentication > URL Configuration** de cada projeto Supabase:

- configure a `Site URL` do respectivo frontend;
- adicione a URL exata `<origem-do-frontend>/redefinir-senha` em `Redirect URLs`;
- mantenha o modelo **Invite user** usando `{{ .ConfirmationURL }}`;
- configure SMTP próprio antes de usar convites em produção.

O prazo do convite segue o valor de **Email OTP Expiration** configurado no Supabase. Um link
expirado precisa ser substituído por um novo convite.

## Validação

```bash
cd backend && ./venv/bin/python -m pytest tests -q
cd front-end && npm run lint:check && npm run format:check && npm run type-check && npm run build-only
```

O workflow `.github/workflows/ci.yml` executa essas verificações, testa as migrations em um
PostgreSQL descartável e audita as dependências em pushes e pull requests.

## Teste de 14 dias do Profissional

Novos escritórios recebem 14 dias do Profissional (100 clientes e 10 membros) ao concluir
`sincronizar-cadastro`, inclusive após confirmação de e-mail. Não há cartão ou cobrança automática.
Escritórios anteriores à migration não recebem teste retroativo; convites e novos logins não
reiniciam o prazo. O CPF/CNPJ continua único por escritório.

- A migration `f2d8a1b6c903` acrescenta datas opcionais de início, término e conversão.
  Execute `alembic upgrade head` **antes** de publicar o backend e, depois, publique o frontend.
  Não use `create_all` como substituto da migration.
- O plano contratado permanece separado do acesso temporário. O backend verifica a expiração
  a cada requisição em UTC, independentemente de cron ou disponibilidade do Render.
- O checkout pendente não encerra o teste. O primeiro pagamento confirmado encerra o benefício
  e libera o plano pago; os dias gratuitos restantes não são adicionados à assinatura.
- Ao expirar sem conversão, o acesso volta ao Gratuito. Acima de 5 clientes ativos ou 1 membro,
  mutações são bloqueadas até adequação ou contratação. O administrador ainda pode desativar
  clientes e remover membros; consultas e downloads continuam disponíveis. Dados não são apagados.
- O administrador pode exportar clientes, obrigações, comentários e metadados de documentos em
  JSON pelo aviso do teste. Arquivos anexados são baixados separadamente em Documentos.
- O painel informa o término e reforça o lembrete nos últimos 3 dias, atualizando o estado a
  cada minuto enquanto aberto. Nesta versão, os lembretes são no aplicativo, não por e-mail.
- Datas de início e conversão permitem acompanhar testes e assinaturas convertidas. A primeira
  atividade pode ser verificada pelos cadastros existentes; não há envio a analytics externo.

Valide em homologação o cadastro, a expiração, os limites e o pagamento sandbox antes da oferta
em produção. O teste de migration com PostgreSQL exige `MIGRATION_TEST_DATABASE_URL` apontando
para um banco descartável vazio; nunca use o banco da aplicação para esse teste.

## Configuração das tarefas agendadas

Os workflows de cobrança, recorrências e alertas usam a variável de **repositório**
`BACKEND_BASE_URL` como URL padrão. Os secrets opcionais `ASAAS_RECONCILIATION_URL`,
`RECURRENCE_PROCESS_URL` e `ALERT_PROCESS_URL` têm prioridade, quando definidos, e devem
conter somente a origem HTTPS da API, sem o caminho do endpoint.

Cada tarefa exige também seu próprio segredo de autenticação:

| Tarefa | Secret do repositório no GitHub e variável no Render |
| --- | --- |
| Cobrança Asaas | `ASAAS_RECONCILIATION_SECRET` |
| Recorrências | `RECURRENCE_CRON_SECRET` |
| Alertas de vencimento | `ALERT_CRON_SECRET` |

Para cada linha, configure o mesmo valor no GitHub e no backend. No GitHub, use
**Settings > Secrets and variables > Actions > Secrets > New repository secret**.
Esses workflows não usam um GitHub Environment; configurações existentes apenas no ambiente
`Production` não são disponibilizadas a eles. Não coloque os valores dos segredos no código.

Uma configuração ausente agora é identificada pelo nome no log. Isso é diferente de falhas HTTP:
404 indica rota não encontrada, 401/403 indica recusa de acesso e 5xx exige verificar a resposta
da API e os logs do Render. Uma execução verde do keep-alive confirma apenas que a API responde;
não valida autenticação, banco ou integrações dessas tarefas.

## Recorrências mensais

- As competências e vencimentos são datas civis; a regra operacional adotada é o calendário de
  `America/Sao_Paulo`, sem depender do relógio ou do fuso do servidor.
- Cada série possui uma identidade e uma competência mensal persistentes no banco.
- A próxima competência é criada quando a ocorrência atual é concluída e é calculada a partir
  dessa ocorrência, inclusive na virada do ano.
- Dias inexistentes são limitados ao último dia do mês e fins de semana passam para a segunda-feira.
- Editar uma recorrência ativa preserva a série; desativá-la e reativá-la começa uma nova série.
- A restrição única no banco impede duas tarefas da mesma série e competência.
- O workflow `.github/workflows/recurrences.yml` reconcilia conclusões interrompidas sem duplicar
  tarefas. Configure `RECURRENCE_PROCESS_URL` e `RECURRENCE_CRON_SECRET` nos secrets do GitHub e o
  mesmo `RECURRENCE_CRON_SECRET` no backend.

## Cobrança e Asaas

- O plano contratado é vinculado por um código imutável salvo na assinatura e na referência
  externa; valores pagos nunca são usados para descobrir o plano.
- IDs de cliente, assinatura, cobrança e evento do Asaas são persistidos separadamente.
- O webhook valida `asaas-access-token`, limita o payload, persiste o evento antes do processamento
  e usa o ID do evento para impedir efeitos duplicados.
- Confirmação, recebimento, atraso, estorno, cancelamento e chargeback possuem estados distintos.
- Eventos com falha usam retentativas exponenciais e uma execução travada pode ser retomada após o
  vencimento da lease.
- O workflow `.github/workflows/asaas-reconciliation.yml` reprocessa a fila e consulta assinaturas
  e cobranças no Asaas a cada 15 minutos. Configure `ASAAS_RECONCILIATION_URL` e
  `ASAAS_RECONCILIATION_SECRET` nos secrets do GitHub, além do mesmo segredo no backend.
- As URLs utilizadas são `api-sandbox.asaas.com/v3` em desenvolvimento/homologação e
  `api.asaas.com/v3` em produção.
