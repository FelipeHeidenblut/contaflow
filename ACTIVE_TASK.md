# Estado ativo da evolução do ContablyTask

Atualizado em: 30 de agosto de 2026

Este arquivo registra o ponto atual do trabalho iniciado a partir da revisão de
qualidade do projeto. Ele deve ser atualizado ao concluir cada etapa, para que a
próxima sessão possa continuar sem refazer análises ou ampliar o escopo sem
autorização.

## Status atual

- **Progresso:** 10 etapas concluídas e nenhuma etapa pendente da revisão.
- **Última etapa concluída:** relatórios.
- **Estado:** ciclo de melhorias concluído; alterações aguardam preparação para
  homologação e organização em commits.
- **Próxima etapa:** validar em homologação e preparar commits somente após
  autorização do usuário.
- **Base de verificação:** 159 testes aprovados, 1 ignorado e nenhum erro de
  compilação nos módulos alterados.

## O que foi feito

### 1. Paginação das listagens principais

- Clientes, documentos, obrigações e membros passaram a usar paginação no
  servidor.
- Foram adicionados filtros executados no backend e limite máximo de 100 itens
  por página.
- O frontend passou a consumir a resposta paginada e ganhou um controle de
  paginação reutilizável.
- Resumos operacionais são calculados dentro do escopo autorizado, sem carregar
  toda a tabela em memória.

### 2. Consultas operacionais e índices

- As consultas mais usadas foram revisadas para reduzir risco de N+1 e leituras
  desnecessárias.
- Foram adicionados índices compostos alinhados às consultas de clientes,
  documentos, obrigações e membros.
- Foi criada uma migration específica para esses índices.

### 3. Exportação administrativa

- A exportação do superadmin foi alterada para processamento em fluxo, evitando
  carregar grandes volumes integralmente em memória.
- O formato público da exportação foi preservado.

### 4. Autenticação e organizações

- A resolução do usuário, perfil e escritório foi centralizada.
- Regras de sincronização e contexto de autenticação foram extraídas das rotas
  para um serviço próprio.
- As verificações de organização e permissões passaram a usar os helpers
  centralizados de controle de acesso.
- As rotas de autenticação ficaram responsáveis principalmente por receber e
  devolver dados HTTP.

### 5. Obrigações e recorrências

- Criação, edição, conclusão, exclusão e listagem de obrigações foram extraídas
  para um serviço de domínio.
- A camada de rotas foi reduzida à coordenação HTTP.
- O motor existente de recorrência continua sendo a implementação canônica.
- A geração da próxima ocorrência permanece idempotente e protegida contra
  duplicação por série e competência.
- Foram adicionados testes para criação, atribuição, edição de recorrência,
  conclusão, exclusão, paginação e resumo autorizado.

### 6. Cobrança e planos

- Sincronização do pagador, contratação de assinatura e reconciliação com o
  Asaas foram extraídas das rotas para um serviço próprio.
- `asaas.py` ficou responsável pelo contrato HTTP, autenticação do webhook e
  validação do segredo da reconciliação.
- O processamento idempotente de eventos e transições financeiras permanece no
  motor canônico de cobrança.
- Respostas externas usadas na contratação e reconciliação passaram a ter
  validação defensiva, inclusive para itens malformados na lista de cobranças.
- Permissão administrativa, isolamento do escritório, referências imutáveis de
  assinatura e trilha de auditoria foram preservados.
- Limites e nomes dos planos passaram a ser consultados por funções centrais do
  catálogo; clientes e membros não mantêm mais mapas próprios desses valores.
- Foram adicionados testes para o serviço de assinatura, catálogo, autorização,
  formatos de CPF/CNPJ, ciclo anual e respostas malformadas do gateway.

### 7. Clientes e responsáveis

- Criação, listagem, desativação, atribuição de responsável e importação CSV
  foram extraídas das rotas para um serviço de domínio próprio.
- `clientes.py` ficou responsável pelo contrato HTTP, limites do upload e
  tradução dos parâmetros para o serviço.
- Permissões de administrador e gerente, escopo da carteira do colaborador e
  isolamento entre escritórios foram preservados no serviço.
- Operações por ID passaram a bloquear o registro durante alterações de estado,
  reduzindo o risco de atualizações concorrentes perdidas.
- A importação continua limitada a 2 MB, atômica e protegida pelo limite do
  plano; nenhum registro é persistido quando o lote excede a capacidade.
- A autorização do upload ocorre antes da leitura do arquivo, evitando consumo
  desnecessário de recursos por usuários sem permissão.
- A verificação de CPF/CNPJ existente passou de uma consulta por linha para
  consultas em lotes de até 1.000 documentos por tipo de pessoa.
- O parsing do CSV passou a ocorrer antes do bloqueio do escritório, reduzindo o
  tempo da seção crítica da transação.
- Foram adicionados testes para o serviço, delegação das rotas, autorização
  antecipada do upload, atomicidade, concorrência do limite e deduplicação em
  lote.

### 8. Documentos

- Listagem, upload, download e exclusão foram extraídos das rotas para um
  serviço de domínio próprio.
- `documentos.py` ficou responsável pelo contrato HTTP, formulários e
  redirecionamento para a URL assinada.
- Permissões, escopo da carteira do colaborador, vínculos com clientes e tarefas
  e isolamento entre escritórios foram preservados no serviço.
- Nomes enviados pelo usuário são normalizados e o caminho no Storage continua
  usando UUID aleatório dentro do prefixo do escritório e do cliente.
- Uploads permanecem limitados a 5 MB e são verificados por extensão e
  assinatura; arquivos DOCX e XLSX também precisam conter a estrutura interna
  correspondente, impedindo ZIPs genéricos disfarçados.
- Caminhos recuperados do banco são validados contra o escritório e o cliente
  autorizados antes de gerar links ou excluir objetos.
- Se o registro no banco falhar após o upload, o serviço tenta remover o objeto
  do Storage e desfaz a transação local.
- Se a exclusão no Storage falhar, o registro permanece no banco para permitir
  nova tentativa, evitando arquivos sensíveis órfãos e sem referência.
- Erros da integração deixaram de ser impressos diretamente e passaram a usar
  logging interno com respostas públicas genéricas.
- Foram adicionados testes para listagem autorizada, upload, nomes e caminhos
  seguros, compensação de falhas, validação de Office Open XML, exclusão e URL
  assinada.

### 9. Notificações e alertas

- Preferências individuais, seleção de vencimentos, reserva idempotente,
  processamento do lote e envio SMTP foram extraídos das rotas para um serviço
  de domínio próprio.
- `alertas.py` ficou responsável pelo contrato HTTP, validação do payload e
  proteção do endpoint agendado.
- O destinatário continua sendo o funcionário responsável pela tarefa, nunca o
  cliente atendido pelo escritório.
- Consultas de candidatos preservam a igualdade de escritório entre tarefa,
  cliente e funcionário, além de ignorarem clientes inativos e tarefas
  concluídas.
- Reservas existentes passaram a usar bloqueio de linha; uma reserva em
  processamento pode ser retomada após 15 minutos, evitando alertas presos para
  sempre quando o processo é interrompido.
- Conflitos de criação continuam protegidos pela restrição única do banco, e
  alertas enviados ou com cinco tentativas não são reprocessados.
- Falhas inesperadas do adaptador de e-mail agora ficam isoladas por alerta, de
  modo que os demais itens do lote continuam sendo processados.
- A configuração SMTP passou a validar porta, combinação de TLS/SSL, par de
  credenciais e impedir autenticação por transporte sem criptografia.
- Título, nomes e cliente continuam escapados no conteúdo HTML; quebras de linha
  são removidas do assunto do e-mail.
- Foram adicionados testes para concorrência, recuperação de reserva abandonada,
  isolamento de falhas no lote e transporte seguro de credenciais SMTP.

### 10. Relatórios

- Validação de acesso, capacidades por plano, filtros, consultas autorizadas e
  agregação foram extraídas das rotas para um serviço de domínio próprio.
- `relatorios.py` ficou responsável somente pelo contrato HTTP e pela tradução
  dos parâmetros para o serviço.
- Os identificadores de planos pagos passaram a reutilizar o catálogo canônico,
  eliminando uma lista duplicada que poderia divergir da cobrança.
- O serviço valida permissão, plano pago e assinatura ativa mesmo quando chamado
  fora da rota, antes de qualquer consulta ao banco.
- Filtros de cliente continuam usando a carteira acessível, filtros de
  responsável exigem vínculo com o mesmo escritório e a consulta de tarefas
  sempre recebe o escopo do usuário autenticado.
- O plano Essencial deixou de consultar nomes de clientes e membros que seriam
  descartados da resposta resumida, reduzindo consultas e exposição interna de
  dados desnecessários.
- Períodos, filtros avançados e status inválidos são rejeitados antes de acessar
  o banco.
- A classificação de tarefas atrasadas passou a usar explicitamente o fuso
  `America/Sao_Paulo`, sem depender do fuso do servidor de produção.
- O formato já consumido pelo frontend foi preservado, incluindo resumo,
  distribuição, linha do tempo, clientes, equipe, filtros e capacidades.
- Foram adicionados testes para acesso fechado, validação antecipada, carteira,
  cliente inacessível, consultas mínimas e fuso horário operacional.

### Verificação mais recente

- Backend: 159 testes aprovados e 1 teste ignorado.
- Compilação dos módulos alterados aprovada.
- `git diff --check` aprovado.
- Nenhuma dependência nova foi adicionada nas etapas de obrigações, cobrança,
  clientes, documentos, alertas ou relatórios.

## O que ficou pendente

Todas as separações por domínio recomendadas na revisão foram concluídas.

Pendências técnicas conhecidas:

- Corrigir o aviso de configuração legada do Pydantic em
  `backend/fiscal_deadlines.py` antes da adoção do Pydantic 3.
- Revisar e organizar o conjunto amplo de alterações ainda não commitadas antes
  de preparar merge ou implantação.
- Executar validação em ambiente de homologação e testes com banco PostgreSQL
  real antes de publicar migrations e mudanças de cobrança.
- Medir o upload com o SDK síncrono do Supabase em homologação e avaliar
  offload/cliente assíncrono. O executor de threads deste ambiente local fica
  bloqueado até em chamadas triviais, por isso a mudança não foi mantida sem
  uma verificação confiável.
- Validar o envio de alertas em homologação com o provedor SMTP real. Como SMTP
  não oferece chave de idempotência, uma interrupção depois da aceitação da
  mensagem e antes da confirmação no banco pode gerar reenvio após o prazo de
  15 minutos. Quando há nova execução no mesmo dia, o fluxo privilegia nova
  tentativa de entrega e não a garantia impossível de envio exatamente uma vez.
- Medir relatórios de escritórios Empresariais com grande volume em PostgreSQL
  real. Se a materialização de até 366 dias de tarefas se tornar um gargalo,
  migrar os cálculos para agregações agrupadas no banco sem alterar a resposta.

## Decisões tomadas

- As melhorias serão executadas incrementalmente, uma etapa por vez.
- Antes de começar outra melhoria ou domínio, é necessário pedir autorização ao
  usuário.
- As APIs públicas existentes devem ser preservadas durante as extrações, salvo
  quando uma mudança de contrato for discutida e aprovada.
- Rotas coordenam HTTP; serviços concentram regras de negócio; helpers de acesso
  garantem organização e permissões.
- A separação por domínio deve resolver acoplamento real e não criar camadas
  genéricas sem uso concreto.
- Toda listagem com crescimento contínuo deve ser paginada no servidor e ter
  limite máximo.
- Agregações e resumos devem respeitar o mesmo escopo de organização e usuário
  aplicado aos registros.
- Regras de acesso sensíveis também devem ser verificadas na camada de serviço,
  sem depender exclusivamente das dependências HTTP.
- Datas operacionais devem usar explicitamente o fuso do negócio e não o fuso
  implícito do servidor.
- Regras de recorrência devem permanecer centralizadas, transacionais e
  idempotentes.
- Importações em lote devem validar autorização antes de ler o arquivo, evitar
  consultas por linha e persistir todos os registros ou nenhum deles.
- Operações que combinam banco e Storage devem compensar falhas ou preservar
  uma referência recuperável; falhas externas não podem ser simplesmente
  ignoradas durante exclusões.
- Processadores agendados devem reservar itens com proteção contra concorrência,
  permitir recuperação de reservas abandonadas e isolar falhas externas por
  item do lote.
- Credenciais SMTP só podem ser usadas com TLS ou SSL e as configurações de
  transporte devem falhar de forma explícita quando forem inconsistentes.
- Arquivos Office Open XML devem ser validados pela estrutura interna, não
  apenas pela assinatura genérica de ZIP.
- Alterações devem preservar o isolamento entre escritórios e validar recursos
  também nas operações por ID.
- Não serão adicionadas dependências quando a biblioteca padrão e os recursos já
  instalados forem suficientes.
- A suíte focada deve passar antes da suíte completa do backend.
- Não realizar commit automaticamente; o usuário decide quando preparar e criar
  o commit.

## Arquivos principais alterados

### Paginação e desempenho

- `backend/pagination.py`
- `backend/clientes.py`
- `backend/documentos.py`
- `backend/membros.py`
- `backend/obrigacoes.py`
- `backend/admin.py`
- `backend/alembic/versions/a6f2d8c4b190_add_operational_query_indexes.py`
- `front-end/src/components/PaginationControls.vue`
- `front-end/src/services/pagination.ts`
- `front-end/src/views/ClientsView.vue`
- `front-end/src/views/DocumentosView.vue`
- `front-end/src/views/MembrosView.vue`
- `front-end/src/views/ObrigacoesView.vue`

### Autenticação, organização e autorização

- `backend/auth_service.py`
- `backend/auth.py`
- `backend/security.py`
- `backend/access_control.py`
- `backend/tests/test_auth_service.py`
- `backend/tests/test_security_context.py`
- `backend/tests/test_access_control.py`

### Obrigações e recorrências

- `backend/task_service.py`
- `backend/obrigacoes.py`
- `backend/recurrence.py`
- `backend/models.py`
- `backend/alembic/versions/b4e8c2f9a731_make_task_recurrence_idempotent.py`
- `backend/tests/test_task_service.py`
- `backend/tests/test_recurrence.py`
- `backend/tests/test_pagination.py`

### Cobrança e planos

- `backend/subscription_service.py`
- `backend/billing.py`
- `backend/asaas.py`
- `backend/plan_config.py`
- `backend/clientes.py`
- `backend/membros.py`
- `backend/tests/test_subscription_service.py`
- `backend/tests/test_plan_config.py`
- `backend/tests/test_asaas_customer.py`
- `backend/tests/test_billing.py`

### Clientes e responsáveis

- `backend/client_service.py`
- `backend/clientes.py`
- `backend/tests/test_client_service.py`
- `backend/tests/test_clients.py`

### Documentos

- `backend/document_service.py`
- `backend/documentos.py`
- `backend/tests/test_document_service.py`

### Notificações e alertas

- `backend/alert_service.py`
- `backend/alertas.py`
- `backend/tests/test_alert_service.py`
- `backend/tests/test_alertas.py`

### Relatórios

- `backend/report_service.py`
- `backend/relatorios.py`
- `backend/tests/test_report_service.py`
- `backend/tests/test_reports.py`

## Próximo passo

Preparar a validação em **homologação** com PostgreSQL, Supabase, Asaas e SMTP
reais, executar os fluxos críticos descritos no manual e organizar o conjunto
amplo de alterações em commits revisáveis. Nenhum commit deve ser criado sem
autorização explícita do usuário.
