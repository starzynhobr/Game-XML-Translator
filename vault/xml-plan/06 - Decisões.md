---
tipo: decisoes
status: ativo
atualizado: 2026-09-03
---

# Decisões

## Registro resumido

| ID | Decisão | Estado | Motivo |
|---|---|---|---|
| DEC-001 | Uma linha por tag alvo, não uma linha agregada por registro | Aceita | Mantém XPath, edição e exportação simples |
| DEC-002 | Tags alvo e tags de contexto são seleções separadas | Aceita | Evita alteração acidental do contexto |
| DEC-003 | Contexto vem da mesma ocorrência da tag pai | Aceita | Impede associação entre personagens/itens diferentes |
| DEC-004 | Presets antigos têm migração em leitura | Aceita | Compatibilidade sem reescrever dados silenciosamente |
| DEC-005 | Manter tabela virtualizada sem paginação | Aceita | Melhor para seleção contínua e arquivos grandes |
| DEC-006 | Definir fonte única de versão compatível com build local e release | Pendente | Regra atual e workflow ainda divergem na prática |
| DEC-007 | Traduzido e confirmado são estados diferentes | Aceita — domínio implementado em STA-001 | A tradução automática não equivale a revisão humana; ver nota 12 |
| DEC-008 | Provedor sem contexto seguro ignora contexto e avisa | Aceita | Não contaminar texto nem depender de parsing frágil |
| DEC-009 | Laterais serão recolhíveis | Proposta | Preserva área da tabela em janelas menores |
| DEC-010 | Desfazer só aparece com histórico real | Aceita | Evita promessa falsa na interface |
| DEC-011 | Italiano, russo, dinamarquês e turco entram como destinos P1 | Aceita | Há usuários relatados traduzindo para esses idiomas |
| DEC-012 | Manter interfaces Clássica e Nova durante o refactor | Aceita | Permite migração gradual e retorno sem perder o fluxo conhecido |
| DEC-013 | Busca fica em uma barra acima do cabeçalho da tabela | Aceita | Busca é ação sobre a lista; a lateral fica para filtros e estrutura persistentes |
| DEC-014 | Manter aplicação explícita da estrutura com prévia barata e processamento assíncrono | Aceita | Evita reconstruções acidentais sem congelar a interface |
| DEC-015 | Busca e ações contextuais compartilham uma barra acima da tabela | Aceita | Mantém o foco no subconjunto sem reduzir a área da tabela |

## DEC-001 — Granularidade das linhas

**Contexto:** uma tag pai pode conter várias tags alvo.

**Decisão:** gerar uma `TranslationEntry` para cada XPath alvo.

**Consequências:**

- mantém compatibilidade conceitual com injeção e checkpoint;
- permite traduzir e revisar campos separadamente;
- exige mostrar a tag de origem na tabela;
- o contexto pode ser repetido entre entradas do mesmo pai.

## DEC-004 — Compatibilidade dos presets

**Decisão:** aceitar o formato antigo na leitura e normalizá-lo em memória. Só persistir o novo formato quando o usuário salvar/editar o preset.

**Consequência:** reduz risco de perda e permite rollback para uma versão anterior do aplicativo enquanto o preset não for modificado.

## DEC-006 — Fonte da versão

**Problema observado:** `build_nuitka.bat`, `main_qt.py`, `pyproject.toml`, `installer.iss` e textos localizados ainda contêm 1.2.x, enquanto a tag/release é 1.3.0 e o workflow deriva a versão da tag.

**Opções:**

1. `APP_VERSION` no script de build como fonte canônica e workflow sincronizado a ela.
2. Arquivo Python pequeno de versão consumido pelo app e pelos scripts.
3. Tag Git como fonte exclusiva para releases, com fallback local explícito.

**Critério para decidir:** uma alteração de versão deve exigir editar um único valor e deve funcionar tanto no build local quanto no GitHub Actions, respeitando as regras do `AGENTS.md`.

**Estado:** aceita e implementada em 2026-09-06.

**Decisão:** `APP_VERSION` em `build_nuitka.bat`, no formato `X.Y.Z.W`, é a fonte canônica. O app lê essa declaração em execução a partir do código-fonte e lê os metadados PE quando compilado. O workflow bloqueia tags divergentes e confere `pyproject.toml`; Inno Setup e os nomes dos assets recebem a versão semântica derivada pelo build.

**Versão deste corte:** `1.4.0.0` nos artefatos Windows e `1.4.0` na versão semântica exibida.

## DEC-011 — Novos idiomas solicitados

**Decisão:** adicionar italiano, russo, dinamarquês e turco primeiro como idiomas de destino da tradução, usando os códigos gerais `it`, `ru`, `da` e `tr` e os códigos DeepL `IT`, `RU`, `DA` e `TR`.

**Evidência:** foi relatado uso real nos quatro idiomas, principalmente italiano entre os três pedidos iniciais.

**Limite:** isso não implica traduzir imediatamente toda a interface. Novos arquivos de locale só devem ser adicionados quando houver tradução e revisão suficientes para manter paridade com as chaves existentes.

## DEC-012 — Duas interfaces durante a migração

**Decisão:** oferecer `Clássica` e `Nova (Beta)` como cascas QML sobre o mesmo `AppViewModel` e o mesmo domínio. A preferência é persistida e aplicada no próximo início.

**Fallback:** se a entrada da Nova não criar uma janela raiz, o inicializador tenta a Clássica automaticamente sem apagar a preferência. Assim uma falha transitória continua diagnosticável.

**Limite:** o fallback cobre falha de carregamento do shell novo. Um defeito em componente compartilhado ou no backend ainda pode afetar as duas interfaces e deve ser coberto por testes de paridade.

## DEC-013 — Posição da busca

**Decisão:** a busca ficará em uma barra secundária imediatamente acima do cabeçalho da tabela. Ela deve pesquisar original, tradução, tag e contexto, mostrar contagem de resultados, ter ação de limpar e atalhos `Ctrl+F`/`Esc`.

**Consequência:** a lateral esquerda fica reservada para filtros de estado e configuração da estrutura XML, que permanecem úteis mesmo quando não há consulta textual ativa.

## DEC-014 — Estrutura explícita sem bloqueio

**Decisão:** manter `Aplicar estrutura` como confirmação antes de substituir as linhas da sessão. A análise inicial e a extração rodam fora da thread visual; tags, prévia e XPaths reutilizam um índice invalidado por caminho, tamanho e data de modificação.

**Consequências:**

- trocar tags não reconstrói milhares de linhas automaticamente;
- a prévia apenas conta correspondências e informa quantas linhas serão carregadas;
- a interface mostra estados de análise/carregamento e bloqueia ações conflitantes;
- a tabela continua virtualizada e sem paginação, conforme DEC-005.

## DEC-015 — Comandos contextuais da tabela

**Decisão:** a barra acima do cabeçalho mostra a busca normalmente e troca para ações contextuais quando há seleção múltipla. `Ctrl+F` limpa a seleção e leva o foco à busca; `Esc` limpa primeiro a seleção ou consulta ativa.

**Consequências:**

- a busca cobre original, tradução, tag de origem e chaves/valores de contexto;
- os números das linhas continuam correspondendo à posição no XML, mesmo com filtro ativo;
- traduzir, confirmar traduções não vazias e limpar a seleção ficam próximos ao subconjunto afetado;
- filtros de estado continuam separados e dependem da máquina de estados ampliada.

## DEC-016 — Paridade sem encerrar o Beta prematuramente

**Estado:** aceita em 2026-09-04 e concluída em 2026-09-06.

A Clássica permanece suportada durante o Beta. A Nova compartilha serviços, tabela e editor; não duplica regras de negócio. O editor moderno inicia com opções do provedor recolhidas e sem repetir ações globais da barra superior. Paridade técnica e renders offscreen não substituem validação manual de operações reais. Não criar filtros de confirmação antes de STA-001.

Migração e rollback: [[11 - Paridade e QA da Interface]]. Backlog: UIR-006, KEY-001, LOG-001.

Após validação visual do usuário, fluxo real e QA automatizado nos dois shells, a Nova deixou o sufixo Beta. A Clássica continua selecionável como opção de rollback; sua permanência não implica duplicar regras de negócio.

## DEC-017 — Não vincular o Gemini a um modelo temporário

**Estado:** aceita e implementada em API-002.

A disponibilidade de um teste com um modelo específico não justifica fixá-lo no aplicativo. O aplicativo descobre modelos compatíveis, preserva a escolha do usuário e mantém candidatos explícitos de compatibilidade, com erros visíveis quando a descoberta falha. Não trocar silenciosamente para um modelo com custo/capacidade diferente.

## DEC-018 — Setup tradicional e atualização assistida

**Estado:** aceita e implementada em 2026-09-06.

O artefato recomendado passa a ser `STZXMLTranslator-Setup-X.Y.Z.exe`, gerado pelo Inno Setup sobre o standalone Nuitka. O editor exibido em Programas e Recursos é `STZ Labs`; a instalação continua por usuário e preserva o `AppId` para upgrades. O CI também publica ZIP portátil e arquivos SHA-256. MSIX, certificado próprio e `install-app.ps1` deixam de ser o fluxo público principal.

A partir da 1.4.0, builds empacotados consultam a release estável mais recente no máximo uma vez por dia. Uma versão superior gera um banner não modal. O usuário pode ver novidades, ignorar a versão, adiar ou baixar. O instalador só é aberto após confirmação, com trabalho de XML/tradução inativo e após conferir o digest SHA-256 informado pelo GitHub.

Não há instalação silenciosa, downgrade nem atualização de prerelease. Falha automática de rede não interrompe o usuário; a verificação manual apresenta erro localizado. SmartScreen e a identificação como editor desconhecido continuam possíveis enquanto não houver assinatura de uma autoridade pública.

## Como registrar nova decisão

Adicionar nesta nota:

- contexto e problema;
- opções realmente consideradas;
- decisão e estado (`Proposta`, `Aceita`, `Substituída`);
- consequências e migração;
- backlog afetado.

Anterior: [[05 - Backlog]] · Próximo: [[07 - Design e Interface]].
