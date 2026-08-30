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
