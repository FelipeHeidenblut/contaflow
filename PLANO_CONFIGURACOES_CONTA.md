# Próxima implementação: configurações da conta

Status: planejado a pedido do usuário; implementar na próxima sessão.
Este documento prepara o trabalho, sem implementar a funcionalidade.

## Objetivo e escopo inicial

Criar uma página autenticada de configurações da conta pessoal no ContablyTask,
acessível para administradores, gerentes e colaboradores pelo menu do usuário.

- Exibir nome, foto e e-mail do usuário conectado.
- Permitir editar e salvar o próprio nome.
- Permitir adicionar, substituir e remover a própria foto, com prévia antes de salvar.
- Exibir iniciais quando não houver foto.
- Manter o e-mail somente para consulta nesta primeira versão.
- Mostrar estados de carregamento, salvamento, sucesso e erro.
- Atualizar nome e foto na interface após salvar, sem exigir novo login.
- Adaptar a página para celular e teclado, seguindo os componentes visuais existentes.

Alteração de e-mail, senha, exclusão da conta, configurações do escritório e
edição de outros membros ficam fora deste incremento.

## Pontos já identificados no código

- `backend/models.py`: o modelo `Profile` já possui `name`; verificar a migration
  necessária para registrar o caminho da foto.
- `backend/auth.py` e `backend/auth_service.py`: reaproveitar a resolução do usuário
  autenticado e a resposta de `/api/v1/auth/me`.
- `front-end/src/stores/auth.ts`: o nome mostrado hoje é inicializado a partir
  dos metadados do Supabase. Ajustar a leitura para priorizar o perfil persistido
  no backend e evitar que um novo login restaure um nome antigo.
- `front-end/src/components/Layout.vue`: já mostra nome e iniciais; adicionar
  acesso às configurações e renderização da foto com fallback.
- `front-end/src/router`: incluir a rota protegida `/configuracoes/conta`.
- Examinar o armazenamento e as validações existentes de documentos para
  reaproveitar infraestrutura, mantendo fotos separadas dos documentos contábeis.

## Sequência de implementação

1. Rever o estado atual do repositório e confirmar os contratos de autenticação,
   armazenamento, permissões e metadados do Supabase antes de editar.
2. Definir o perfil do backend como fonte do nome e do caminho da foto. Verificar
   consumidores de metadados e eventual sincronização, sem criar duas fontes
   conflitantes nem permitir que metadados alterem permissões ou escritório.
3. Criar migration aditiva para o caminho da foto, se necessário; preservar
   contas existentes e não persistir URLs assinadas que expiram.
4. Implementar leitura e atualização do próprio perfil e upload/remoção de foto.
   Resolver usuário e escritório pela autenticação, nunca por IDs enviados pelo cliente.
5. Para a foto, validar tamanho e conteúdo real da imagem, limitar formatos
   (proposta inicial: JPEG, PNG e WebP, até 2 MB), usar nomes gerados e controlar
   acesso no armazenamento. Confirmar suporte às validações nas dependências.
6. Substituir a referência somente após upload bem-sucedido. Planejar limpeza
   de arquivos antigos e de uploads sem referência, sem perder a foto atual
   quando alguma etapa falhar. Renovar URLs temporárias quando necessário.
7. Construir a página, integrar o menu do usuário e atualizar o estado de
   autenticação. Nome e foto devem continuar corretos após recarregar e relogar.
8. Validar o fluxo e registrar instruções de migration e configuração do bucket
   necessárias para disponibilizar a funcionalidade.

## Critérios de aceitação e testes

- Nome válido persiste; nome vazio ou acima do limite retorna erro claro.
- Adicionar, substituir e remover foto funciona; cancelamento não salva a prévia.
- Arquivo inválido ou acima do limite é recusado sem alterar o perfil.
- Falha ao salvar mantém os dados anteriores e permite tentar novamente.
- Cada usuário altera apenas a própria conta; testar isolamento entre escritórios.
- Nome e foto aparecem corretamente na página e no menu após salvar e relogar.
- Contas sem foto mantêm o fallback de iniciais, inclusive se o download falhar.
- Conferir desktop, celular, navegação por teclado e ausência de erros no navegador.
- Executar testes relevantes do backend, lint, tipos, formatação e build do frontend.

## Retomada

Pedido sugerido para a próxima sessão: “Implemente a página de configurações
da conta seguindo o PLANO_CONFIGURACOES_CONTA.md”.

Não há execução agendada: este arquivo registra o escopo para retomada.
