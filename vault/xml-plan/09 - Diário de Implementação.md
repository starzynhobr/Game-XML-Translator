---
tipo: diario
status: ativo
atualizado: 2026-09-03
---

# Diário de Implementação

Use esta nota como índice cronológico curto. Detalhes duráveis ficam no backlog e nas decisões; o diário registra evidência do que aconteceu.

## 2026-09-03 — Planejamento inicial

### Contexto

Feedback de usuário real destacou quatro necessidades:

- várias tags alvo e tags adicionais de contexto;
- mais idiomas;
- substituição de frases idênticas em massa;
- tradução de vários itens selecionados.

### Decisão de prioridade

Tags alvo múltiplas + tags de contexto são P0 porque afetam a qualidade da tradução e eliminam a repetição do fluxo por campo.

### Estado observado

- A aplicação ainda modela uma única tag alvo.
- Alterações de glossário, duplicatas e seleção múltipla existem no working tree e estão em validação.
- A versão publicada 1.3.0 diverge de referências locais 1.2.x.
- A referência visual é útil como organização, mas paginação e metadados colaborativos foram rejeitados para o escopo atual.

### Documentos criados

- [[00 - Plano Mestre de Implementação]]
- [[01 - Visão do Produto]]
- [[02 - Estado Atual e Evidências]]
- [[03 - P0 Tags e Contexto]]
- [[04 - Roadmap]]
- [[05 - Backlog]]
- [[06 - Decisões]]
- [[07 - Design e Interface]]
- [[08 - Qualidade, Dados e Release]]

### Próxima ação executável

Implementar TAG-004, migrando presets antigos em memória sem reescrever o arquivo durante a leitura.

## 2026-09-03 — Primeiro corte de tags e contexto

### Escopo

- TAG-001, TAG-002, TAG-003 e parte de TAG-009.

### Alterações

- Criado `ExtractedEntry` com XPath, XPath do contêiner, tag de origem, original e contexto.
- Criada extração de várias tags alvo na ordem escolhida.
- Contexto limitado aos filhos da mesma ocorrência da tag pai.
- Tags solicitadas são deduplicadas e sobreposição alvo/contexto é recusada.
- XML com namespace passa a gerar XPath baseado em `local-name()` compatível com o injetor lxml.
- `TranslationProject.load` aceita string antiga ou lista de alvos, preservando `target_tag` para compatibilidade.

### Validação

- `uv run pytest -q`: 184 testes aprovados.
- `uv run ruff check .`: aprovado.
- `git diff --check`: aprovado; apenas avisos de conversão LF/CRLF do Git.
- Round-trip com namespace confirmou que a tag de contexto permanece intacta.

### Próximo passo

- TAG-005: isolar checkpoints por configuração de tags.

## 2026-09-03 — Presets multi-tag e idiomas solicitados

### Escopo

- TAG-004 e registro de LANG-001 a LANG-003.

### Alterações

- Presets legados com `target_tag` são convertidos apenas em memória para `target_tags`.
- A leitura não modifica o arquivo existente.
- Salvamentos explícitos usam `target_tags` e `context_tags`, sem o campo singular legado.
- Importação deduplica formatos antigo e novo como a mesma configuração.
- Italiano, russo e dinamarquês foram registrados como destinos P1 respaldados por uso relatado.

### Próximo passo

- TAG-005: incluir a assinatura da seleção de tags nos checkpoints e carregar legado somente como fallback controlado.

## 2026-09-03 — Checkpoints isolados por estrutura

### Escopo

- TAG-005 e cobertura adicional de TAG-009.

### Alterações

- O nome atual do checkpoint inclui assinatura de tag pai, tags alvo e tags de contexto.
- A assinatura ignora a ordem das listas, evitando duplicar progresso para a mesma seleção semântica.
- O formato antigo de nome continua calculável como fallback.
- O checkpoint atual sempre tem precedência; fallback só ocorre quando ele não existe.
- O worker e a restauração da interface usam a mesma regra.
- Limpar progresso remove o checkpoint atual e os legados relevantes para impedir reaparecimento.

### Validação

- `uv run pytest -q`: 198 testes aprovados.
- `uv run ruff check .`: aprovado.
- `git diff --check`: aprovado; apenas avisos LF/CRLF.
- Inicialização e encerramento do QML em modo offscreen: aprovados.

### Próximo passo

- TAG-006: passar o contexto estruturado aos provedores compatíveis sem misturá-lo ao texto traduzível.

## 2026-09-03 — Contexto entregue aos provedores

### Escopo

- TAG-006, cobertura adicional de TAG-009 e registro de LANG-004.

### Alterações

- Gemini recebe contexto delimitado por entrada e instrução para não o traduzir nem devolver.
- DeepL recebe tag de origem e campos relacionados pelo parâmetro nativo `context` do SDK.
- Ollama individual recebe bloco delimitado; lotes usam objetos separados com `text`, `field` e `context`.
- Google gratuito e Azure ignoram contexto de entrada e emitem um único aviso localizado por execução.
- O worker cria uma cópia da configuração por entrada, sem contaminar a configuração compartilhada.
- Turco foi registrado como idioma alvo P1 com demanda real relatada.

### Validação

- Assinatura instalada de `deepl.Translator.translate_text` confirma o parâmetro `context`.
- `uv run pytest -q`: 209 testes aprovados.
- `uv run ruff check .`: aprovado.
- `git diff --check`: aprovado; apenas avisos LF/CRLF.
- Inicialização e encerramento QML em modo offscreen: aprovados.
- APIs externas não foram chamadas ao vivo neste corte.

### Próximo passo

- TAG-007: criar o seletor QML multi-tag com chips, preservando acessibilidade e o fluxo singular atual durante a transição.

## 2026-09-04 — Seleção multi-tag na interface

### Escopo

- TAG-007 e cobertura adicional de TAG-009.

### Alterações

- A tag pai continua singular; tags alvo e tags de contexto agora usam seletores separados com chips removíveis.
- Tags alvo usam marcador `T` e destaque primário; contexto usa marcador `C` e destaque de atenção, sem depender apenas de cor nos nomes acessíveis.
- A mesma tag fica indisponível no seletor oposto e a regra também é garantida no ViewModel.
- A interface mostra, antes de recarregar, quantas tags foram escolhidas, quantas linhas reais serão extraídas e quantos campos de contexto foram selecionados.
- Presets novos salvam e reaplicam as duas listas; os slots singulares continuam disponíveis durante a transição.
- O estado multi-tag foi centralizado no ViewModel e o carregamento, recarregamento e salvamento no arquivo atual preservam a seleção completa.

### Validação

- Testes dedicados cobrem ordenação, deduplicação, exclusão mútua, troca da tag pai, prévia sem mutação, recarregamento multi-alvo e aplicação de preset.
- Chamada QML com `QVariantList` confirmou a conversão de arrays para os slots multi-tag.
- Renderização nativa em 1280 × 760 confirmou chips, estados vazios, resumo e hierarquia visual; o QML carregou sem warnings.
- `pytest -q`: 216 testes aprovados.
- `ruff check .`: aprovado.
- Os cinco JSONs de idioma foram validados e a inicialização QML terminou com uma raiz e zero warnings.
- `git diff --check`: aprovado; apenas avisos de conversão LF/CRLF do Git.

### Próximo passo

- TAG-008: exibir a tag de origem e o contexto da linha na tabela e no painel de edição.

## 2026-09-04 — Origem e contexto visíveis por entrada

### Escopo

- TAG-008 e cobertura adicional de TAG-009.

### Alterações

- O modelo da tabela expõe papéis próprios para `source_tag` e `context`, preservando as três colunas existentes.
- A tag de origem aparece como badge compacto dentro da coluna de texto original, sem comprimir a tabela com uma quarta coluna.
- Ao selecionar uma linha, o ViewModel envia a tag de origem e o mapa de contexto junto aos dados já exibidos no editor.
- O painel direito mostra um bloco somente leitura com o campo de origem e cada par `tag: valor` do mesmo registro pai.
- Entradas sem contexto recebem um estado vazio explícito em vez de uma área silenciosamente ausente.
- Carregar outro XML limpa texto e metadados da seleção anterior.

### Validação

- Testes dedicados verificam os papéis do modelo e o metadado emitido ao selecionar uma linha.
- Renderização nativa em 1280 × 760 conferiu badges, contexto, quebra de texto e encaixe no painel rolável.
- A inicialização QML terminou com uma raiz e zero warnings.
- `pytest -q`: 218 testes aprovados.
- `ruff check .`: aprovado; os cinco JSONs de idioma também foram validados.
- `git diff --check`: aprovado; apenas avisos de conversão LF/CRLF do Git.

### Próximo passo

- TAG-009: fechar a matriz de testes e QA do fluxo multi-tag completo, incluindo exportação e migrações.

## 2026-09-04 — Fechamento do fluxo multi-tag

### Escopo

- TAG-009 e critérios de saída da Fase 1.

### Alterações

- Foi criada uma suíte integrada para o ciclo carregar, traduzir alvos diferentes, salvar checkpoint, retomar e exportar.
- O round-trip compara ordem dos elementos, atributos, valores de contexto, alvos alterados e campos não selecionados.
- O salvamento no arquivo atual é exercitado somente sobre uma cópia temporária.
- Um XML exportado é recarregado com os dois alvos ainda endereçáveis e o contexto associado ao mesmo registro.

### Validação automatizada

- `pytest -q`: 221 testes aprovados.
- `ruff check .`: aprovado.
- Inicialização QML em escala 125%: uma raiz e zero warnings.
- Os cinco JSONs de idioma foram validados.
- `git diff --check`: aprovado; apenas avisos de conversão LF/CRLF do Git.

### Validação com XML real

- `characters.xml` do MAA Redux foi lido com `baseVillain` como pai, `bio` e `cogBio` como alvos e `dispName` como contexto.
- Resultado: 95 registros, 190 entradas, dois tipos de origem e contexto presente em todas as entradas.
- A exportação alterou dois XPaths em um arquivo temporário; a estrutura, os atributos e todos os valores de `dispName` permaneceram iguais.
- O teste manual do usuário confirmou os 190 itens, os badges de origem e o contexto correto no painel direito.

### QA visual

- Largura mínima de 1024 × 620: recursos continuam acessíveis por rolagem; texto da tabela usa elipse e o conteúdo completo permanece no editor.
- Largura regular de 1280 × 760 e captura ampla do usuário: chips, badges e contexto mantêm a hierarquia e não apresentam sobreposição.

### Limites mantidos fora deste fechamento

- Nenhuma API externa foi chamada ao vivo nesta etapa; o smoke test real dos provedores continua como gate de release.
- A versão visível ainda precisa ser unificada por VER-001 antes da publicação.

### Próximo passo

- Iniciar a Fase 2 por STA-001: expandir a máquina de estados para separar tradução gerada, confirmação e erro.

## 2026-09-04 — Fundação para interfaces Clássica e Nova

### Escopo

- UIR-001.

### Alterações

- O inicializador escolhe a entrada QML a partir da preferência `classic` ou `modern`.
- A Nova (Beta) começa como uma casca sobre a composição clássica, mantendo paridade funcional enquanto o shell independente é preparado.
- Se a Nova não criar uma janela raiz, o carregador limpa o cache QML e tenta a Clássica automaticamente.
- Configurações ganhou um seletor de interface com aviso de que a troca é aplicada após reiniciar.
- A preferência é validada, persistida junto às demais configurações e exposta pelo ViewModel.
- Os cinco idiomas atuais receberam os textos do seletor.

### Validação

- `pytest -q`: 228 testes aprovados.
- `ruff check .`: aprovado.
- As entradas `main.qml` e `ModernMain.qml` criaram uma raiz e não emitiram warnings QML.
- Capturas em 1280 × 760 e 1024 × 620 confirmaram encaixe e rolagem do painel de configurações.
- Os cinco JSONs de idioma foram validados e `git diff --check` não encontrou erros.

### Decisões

- [[06 - Decisões#DEC-012 — Duas interfaces durante a migração]].
- [[06 - Decisões#DEC-013 — Posição da busca]].

### Próximo passo

- UIR-002: criar o shell independente da Nova mantendo tabela, editor e ações atuais conectados ao mesmo ViewModel.

## 2026-09-04 — Shell independente da Nova (Beta)

### Escopo

- UIR-002.

### Alterações

- `ModernMain.qml` deixou de instanciar a composição clássica e passou a possuir seu próprio `ApplicationWindow`.
- A Nova mantém o mesmo `AppViewModel`, temas e componentes funcionais da Clássica, sem duplicar regras de negócio.
- Foram definidas regiões identificáveis para ações globais, workbench, estrutura XML, conteúdo, tabela, atividade/log e editor.
- A região global começa oculta e sem altura, reservada para UIR-003 sem alterar o layout deste corte.
- O título da janela identifica explicitamente `Nova (Beta)`.
- A dependência transitória `qmldir`/`ClassicMain` foi removida.

### Validação

- Testes estruturais impedem que a Nova volte a herdar `ClassicMain` e verificam regiões e componentes compartilhados.
- Clássica e Nova criaram uma raiz, sem warnings QML.
- Sinais de log, progresso e limpeza de workspace foram exercitados nas duas interfaces.
- Todas as sete regiões da Nova foram encontradas na árvore QML em runtime.
- Capturas em 1280 × 760 e 1024 × 620 foram comparadas pixel a pixel, sem diferença na área cliente.

### Próximo passo

- UIR-003: preencher a região global com a nova barra superior, mantendo as ações antigas acessíveis durante a transição.

## 2026-09-04 — Barra superior da Nova (Beta)

### Escopo

- UIR-003.

### Alterações

- A região global da Nova recebeu uma barra com arquivo, idioma de destino, progresso e ações.
- `Traduzir pendentes` é a ação primária; Glossário, Configurações e Exportar XML usam tratamento secundário.
- Carregar XML reutiliza o seletor e o estado de tags da lateral existente.
- Glossário e Configurações abrem os diálogos já existentes; não foram criadas cópias de estado ou persistência.
- A barra usa uma linha em largura regular e duas linhas abaixo de 1120 px.
- Sobrescrever o arquivo atual continua fora da barra, preservando seu caráter cauteloso.
- Foram adicionados textos específicos e curtos nos cinco idiomas atuais.

### Correção durante QA

- A primeira versão mantinha largura implícita excessiva em 1024 px, cortando Configurações/Exportar e deslocando o editor.
- A barra passou a aceitar compressão pelo layout; o modo compacto agora entra corretamente e mantém todos os controles dentro da janela.

### Validação

- A Nova criou uma raiz sem warnings e todos os controles globais foram encontrados na árvore QML.
- Em 1280 × 760, a barra usa uma linha; em 1024 × 620, as ações usam a segunda linha.
- Verificação geométrica confirmou barra, botões, lateral, tabela e editor inteiramente dentro da janela nas duas dimensões.
- Os botões da barra abriram Configurações e Glossário em testes de interação.
- No estado vazio, Carregar XML fica ativo e Traduzir/Exportar ficam desabilitados.

### Próximo passo

- UIR-004: concentrar a lateral esquerda em estrutura XML e filtros, removendo as duplicações globais somente na Nova.

## 2026-09-04 — Lateral de Estrutura XML da Nova

### Escopo

- UIR-004.

### Alterações

- `LeftSidebar` recebeu um modo enxuto opt-in; o comportamento padrão da Clássica não mudou.
- Na Nova, foram removidas da lateral as duplicações de carregar XML, idioma, progresso, exportação e configurações.
- Tag pai, alvos e contexto foram agrupados sob o título Estrutura XML.
- `Recarregar` foi renomeado para `Aplicar estrutura` somente no novo fluxo.
- Salvar no arquivo atual permanece na lateral como ação cautelosa e separada da exportação.
- A Nova ganhou um dock recolhível: expandido em largura regular e recolhido por padrão abaixo de 1120 px.
- O botão da barra superior continua abrindo Configurações mesmo quando a lateral está fechada.

### Decisão de escopo

- Filtros de estado permanecem em `STA-001/FIL-002`. Não foram adicionados botões sem filtragem e persistência reais.

### Validação

- A Clássica manteve visíveis todos os controles globais anteriores.
- A Nova ocultou apenas as duplicações e manteve título, seletores, aplicação da estrutura e salvamento.
- Recolher, expandir e abrir Configurações com a lateral fechada foram exercitados em runtime.
- Capturas nativas foram inspecionadas em 1280 × 760 e 1024 × 620, sem corte ou sobreposição.
- A árvore QML iniciou sem warnings nas duas variantes.

### Próximo passo

- UIR-005/FIL-001: implementar busca por original, tradução, tag e contexto acima da tabela; depois conectar ações contextuais da seleção.

## 2026-09-04 — Carregamento indexado e assíncrono de XML

### Escopo

- PERF-001.

### Alterações

- O XML ativo passa a ser analisado uma vez e reutilizado enquanto caminho, tamanho e data de modificação não mudarem.
- A prévia conta correspondências no índice sem criar `ExtractedEntry` nem calcular XPath.
- O cálculo de XPath compartilha índices por grupo de irmãos e deixa de revarrer milhares de elementos para cada linha.
- Análise inicial e extração rodam em workers; somente a aplicação ao projeto e ao modelo Qt ocorre na thread principal.
- As duas interfaces mostram estados de análise/carregamento, bloqueiam ações conflitantes e mantêm `Aplicar estrutura` como confirmação explícita.
- A Nova informa a quantidade diretamente na ação: `Carregar 5.060 linhas`.

### Validação

- XML real: `characters.xml`, 11.343.959 bytes, 288.782 elementos e 5.060 linhas em `<action>/<dispName>`.
- Antes: prévia mediana de 5,750 s e carga de 5,639 s.
- Depois: análise fria de 0,672 s fora da UI, prévia em 0,005 s, extração indexada em 0,032 s e carga fria completa em 0,751 s.
- `reloadXml()` retornou à thread visual em 0,0004 s; conclusão observada em 0,093 s com o índice já preparado.
- 237 testes passaram e o Ruff não encontrou violações.
- Clássica e Nova criaram raiz sem warnings QML; os estados analisando, prévia pronta e 5.060 linhas carregadas foram renderizados na Nova em 1280 × 760.

### Decisão

- [[06 - Decisões#DEC-014 — Estrutura explícita sem bloqueio]].

### Próximo passo

- Retomar UIR-005/FIL-001 com a busca acima da tabela, agora sobre um carregamento de XML estável.

## 2026-09-04 — Ajustes da tabela e busca contextual

### Escopo

- UIR-004.1, UIR-004.2, UIR-005, FIL-001 e BULK-003.

### Alterações

- O divisor entre Texto Original e Tradução agora pode ser arrastado; a primeira coluna permanece fixa, cada coluna de conteúdo conserva no mínimo 160 px e duplo clique restaura a proporção 45/55.
- `Traduzir pendentes` deixou de absorver todo o espaço disponível: usa 188 px preferenciais, até 200 px, e o grupo fica alinhado à direita também no modo compacto.
- A Nova recebeu uma barra diretamente acima da tabela para buscar em original, tradução, tag e contexto, mostrar `resultados/total` e limpar a consulta.
- `Ctrl+F` foca a busca e `Esc` limpa a seleção múltipla ou a consulta ativa.
- Com duas ou mais linhas selecionadas, a mesma região mostra Traduzir seleção, Confirmar seleção e Limpar seleção.
- Confirmar seleção altera apenas itens selecionados que já possuem tradução não vazia.
- O filtro atua no modelo virtualizado e conserva a numeração original do XML.
- Uma nova carga de XML limpa a consulta anterior para evitar uma tabela aparentemente vazia.

### Validação

- 245 testes passaram; Ruff não encontrou violações e os cinco arquivos JSON de locale foram validados.
- A raiz QML iniciou sem warnings e expôs busca, divisor e ações contextuais.
- Capturas renderizadas foram inspecionadas em 1280 × 760 e 1024 × 620, sem corte ou sobreposição.
- Interação automatizada confirmou mudança do divisor, consulta com um resultado e limpeza de três linhas selecionadas.
- Busca sintética em 5.060 entradas levou 7,56 ms nesta execução.

### Decisão

- [[06 - Decisões#DEC-015 — Comandos contextuais da tabela]].

### Próximo passo

- UIR-006: montar a matriz de paridade Clássica × Nova e iniciar o QA final dos dois shells.

## 2026-09-04 — Validação real do Gemini e correção do atalho de busca

### Escopo

- Diagnóstico do Gemini e QA do UIR-005.

### Alterações

- O atalho padrão de busca passou a usar `sequences: [StandardKey.Find]`, eliminando o warning emitido pelo Qt para teclas padrão com mais de uma combinação associada.
- A chave temporária fornecida para o teste foi usada somente em memória e não foi persistida no projeto nem na configuração do aplicativo.

### Validação do Gemini

- Autenticação e listagem funcionaram: 19 modelos disponíveis, sendo 15 classificados como gratuitos e 4 como pagos pela regra atual.
- `gemini-flash-lite-latest` respondeu HTTP 503 por alta demanda; a rota e a autenticação já haviam sido validadas.
- `gemini-2.5-flash-lite` concluiu uma tradução individual com tag e contexto em 3,77 s.
- O caminho em lote usado por `Traduzir pendentes` retornou e interpretou corretamente 2 de 2 entradas em 2,24 s com o modelo estável.

### Conclusão

- O Gemini funciona no fluxo individual e em lote. A falha observada é específica da disponibilidade do alias `Latest`; considerar tornar o modelo estável a opção inicial ou adicionar fallback explícito em um corte separado.

### Próximo passo

- UIR-006 e decisão sobre política de fallback de modelos Gemini.

## 2026-09-04 — UIR-006: paridade técnica e editor compacto

### Alterações

- Nova: opções do provedor recolhíveis, remoção de ações globais duplicadas no editor e atividade inferior compacta/expansível.
- Tabela/editor compartilhados: anterior/próxima, navegação por teclado e foco com scroll até a tradução.
- Atalhos de confirmação/salvamento na Nova, com bloqueio durante operações conflitantes.
- Novos rótulos nas cinco traduções da interface; roteiro GUI reproduzível e matriz [[11 - Paridade e QA da Interface]].

### Validação

- `uv run pytest -q`: 246 passed.
- `uv run ruff check .`: sem erros.
- `uv run python -m tests.qml_parity_check`: QA offscreen com dados sintéticos e novamente com characters.xml real (5060 entradas), 24 capturas por execução, navegação/foco/log e geometria em cinco idiomas.
- Inspeção visual com fontes reais: editor moderno permanece mais acessível nos temas claro/escuro. Testes não chamaram API, gravaram configuração nem sobrescreveram XML de jogo.

### Limites e próximo passo

UIR-006 permanece em validação até o roteiro manual nativo; Nova mantém Beta e Clássica segue suportada (DEC-016). STA-001 precede filtros de estado. Gemini não foi fixado em 2.5: descoberta e política de fallback ficam em API-002/DEC-017.

## 2026-09-04 — Validação do usuário e STA-001

O usuário confirmou fluxo real, tradução, Gemini e exportação funcionando na Nova, com screenshot. Evidência manual limitada a essas operações; não presumir validação de todos os diálogos, escalas ou rollback.

STA-001 entregue: cinco estados tipados, alias legado done → translated, confirmação explícita e checkpoint v2 compatível com leitura antiga. Corrigidos reticências sobrescrevendo conteúdo e erro individual de API sendo tratado como tradução. Pendentes incluem erros para nova tentativa; recuperação de cancelamentos evita estados transitórios presos. Exportação mantém o contrato de textos não vazios.

Validação: 268 testes passaram; Ruff limpo; 24 cenários offscreen dos dois shells passaram. Sem chamadas reais nesta execução. Regras, limites e próximo passo em [[12 - Estados de Tradução]]. Próximo: STA-002; apresentação visual de estados em STA-003 e filtros em FIL-002.

## 2026-09-04 — STA-002: diagnóstico persistente por entrada

Implementados error_code e mensagem segura de catálogo, persistência opcional no checkpoint v2, preservação ao recarregar e limpeza ao tentar novamente/concluir/confirmar/resetar. Worker associa falhas individuais/de lote à entrada sem persistir exceção bruta; modelo QML expõe os novos campos para STA-003.

Validação com skill python-testing-patterns: 289 testes passaram, incluindo 21 novos; Ruff limpo. Provedores simulados, sem chamadas reais. Mensagens atuais do catálogo são em português; localização e exibição no editor são escopo de STA-003. Detalhes em [[13 - Diagnóstico por Entrada]].

## 2026-09-04 — STA-003: estados e diagnóstico na interface

Rótulos de estado na tabela, verde exclusivo para confirmação, superfície de erro e estado/diagnóstico no editor compartilhado. Ação individual de erro renomeada para Tentar novamente; guardas de operação ocupada preservadas. Mensagens localizadas em pt_BR/en_US/es_ES/fr_FR/ja_JP. Skill product-design orientou rótulos além da cor e QA nos temas claro/escuro.

QA offscreen de 24 cenários passou; inspeção visual de erro/confirmado/traduzido na Nova. Sem chamadas reais. Próximo: FIL-002. Detalhes em [[14 - Revisão Visual dos Estados]].

## 2026-09-05 — FIL-002: filtros e contadores por estado

Seletor com seis opções e contadores globais na lateral compartilhada. Interseção com busca; estado ativo com reset visível na tabela, vazio localizado e seleção invalidada ao mudar linhas. Confirmação múltipla preserva snapshot de XPaths; contadores incrementais evitam varreduras repetidas.

299 testes passaram; Ruff limpo; QA offscreen e inspeção visual das duas interfaces, temas claro/escuro e janela estreita. Skills product-design e python-testing-patterns orientaram escopo visual e regressões. Nenhuma API real ou XML de jogo alterado. Detalhes em [[15 - Filtros e Contadores por Estado]].

## 2026-09-05 — Acabamento visual de FIL-002 e auditoria pré-release

O seletor de estado recebeu superfície, texto, borda, indicador e popup baseados nos tokens do tema. O handler QML passou a declarar `index` explicitamente, removendo o aviso de parâmetro injetado. A barra de busca teve alinhamento vertical uniforme e a faixa do filtro ativo ganhou separação geométrica do cabeçalho, sem sobreposição do botão de limpar.

Validação: 299 testes passaram; Ruff limpo; QA offscreen com 36 capturas passou nos dois shells, dois temas, três dimensões e estados vazio/carregado/filtrado. Inspeção visual confirmou contraste nos temas escuro e claro, alinhamento da busca e separação da tabela. A skill product-design orientou o uso dos tokens existentes e a hierarquia espacial.

A auditoria de produção confirmou dois gaps objetivos: versão local/build ainda em 1.2.0 enquanto 1.3.0 já está publicada; italiano, russo, dinamarquês e turco permanecem documentados, mas ausentes dos destinos. API-002 foi reclassificado como concluído após confirmar descoberta dinâmica, seleção persistida, candidatos de fallback e cobertura automatizada. O corte mínimo está em [[08 - Qualidade, Dados e Release]].

## 2026-09-05 — Centralização geométrica e quatro novos destinos

A barra contextual foi limitada a 42 px e suas duas páginas passaram a usar um contêiner interno com margens verticais simétricas. Um teste de geometria compara os centros globais da barra e do campo com tolerância de 1 px; ele reproduziu o desvio anterior de 6 px antes da correção.

Italiano, russo, dinamarquês e turco foram adicionados como destinos, com códigos gerais e DeepL definidos na DEC-011. Destinos agora são uma coleção independente dos arquivos de localização da interface: ambos os shells exibem nove destinos, enquanto o seletor de UI continua oferecendo somente as cinco traduções completas. Persistência, checkpoint e configuração dos provedores reutilizam o fluxo existente.

Validação: 305 testes passaram; Ruff limpo; QA offscreen de 36 capturas passou e confirmou centralização, nove destinos, responsividade, temas e estados. Os LANG-001 a LANG-004 ficam em validação até smoke real em provedor compatível.

## 2026-09-06 — Fechamento funcional e candidata 1.4.0

### Escopo

- UIR-006, KEY-001, GLO-001, BULK-001/002, DUP-001, LANG-001 a LANG-004, VER-001, DOC-001 e I18N-001.

### Alterações

- A Nova saiu do Beta após a validação visual do usuário e a matriz automatizada dos dois shells; a Clássica permanece como rollback.
- A versão canônica passou para `1.4.0.0`, exibida como `1.4.0`, com guardas contra divergência no workflow.
- O Quick Start foi atualizado para `uv`; cinco locales permanecem com paridade de chaves e sem textos vazios.
- Italiano, russo, dinamarquês e turco passaram por smoke real no Google Translate.
- Seleção QML com clique, Ctrl e Shift, lote restrito à seleção e duplicatas exatas receberam cobertura de integração.
- Notas, migração, limitações, rollback e gates finais estão em [[16 - Release 1.4.0]].

### Validação

- `uv run pytest -q`: 311 testes aprovados.
- `uv run ruff check .`: aprovado.
- `uv run python -m tests.qml_parity_check`: 36 cenários aprovados.
- Nuitka standalone compilado com `FileVersion`/`ProductVersion` `1.4.0.0`; processo compilado permaneceu ativo no smoke oculto.
- MSIX `1.4.0.0` criado e assinado; assinatura válida, payload conferido e SHA-256 registrado na nota de release.

### Limites e próximo passo

GLO-002 continua aberto porque a proteção de glossário DeepL só foi validada com mock. O pacote não foi instalado por cima da 1.3.0 atual. Antes de publicar: smoke real DeepL, instalação limpa, atualização 1.3.0 → 1.4.0 e rollback.

## 2026-09-06 — PKG-001 e UPD-001 a UPD-004

### Alterações

- O Inno Setup substituiu MSIX/certificado/PowerShell como distribuição pública principal; editor `STZ Labs`, instalação por usuário e `AppId` estável foram preservados.
- O workflow gera Setup, ZIP portátil e SHA-256, sem secrets de certificado próprio.
- Builds empacotados verificam a release estável do GitHub uma vez por dia; Configurações oferece verificação manual.
- Banner compartilhado permite ver novidades, ignorar, adiar, baixar e instalar após confirmação.
- Download usa nome exato do asset, arquivo parcial, troca atômica e digest SHA-256 obrigatório.
- Tradução, operação individual ou carga XML bloqueiam download/instalação; erro automático de rede permanece silencioso.

### Validação

- `uv run pytest -q`: 334 testes aprovados; Ruff sem erros.
- Testes isolam respostas HTTP, versões inválidas, asset ausente, digest, adulteração, persistência, intervalo diário, bloqueios e lançamento do Setup.
- QA QML: 44 capturas, incluindo atualização nos dois shells, temas claro/escuro e larguras 1024/1600 px; inspeção visual aprovada.
- Nuitka standalone recompilado com o updater, `CompanyName=STZ Labs`, versão `1.4.0.0`, payload QML presente e smoke oculto aprovado.
- Consulta real à API pública do GitHub aprovada; como a última release publicada é anterior à 1.4.0, o resultado correto foi sem atualização disponível.
- Inno não está instalado neste host, portanto a compilação e a instalação real do Setup permanecem no gate de release.

### Próximo passo

- Rodar a suíte completa e, após disponibilizar um Setup de teste, executar UPD-004 ponta a ponta sem usar a release pública como primeiro ensaio.

## Modelo de nova entrada

```markdown
## AAAA-MM-DD — Título

### Escopo
- IDs do backlog afetados

### Alterações
- arquivos e comportamento

### Validação
- comandos e resultados exatos

### Decisões ou desvios
- link para decisão, se houver

### Próximo passo
- uma ação concreta
```

Anterior: [[08 - Qualidade, Dados e Release]] · Voltar: [[00 - Plano Mestre de Implementação]].
