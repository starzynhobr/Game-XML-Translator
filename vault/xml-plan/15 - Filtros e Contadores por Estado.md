# FIL-002 — Filtros e contadores por estado

Implementado em 2026-09-05. Disponível na lateral esquerda da Clássica e da Nova.

## Comportamento

- Seletor único: Todos, Pendente, Traduzindo, Traduzido, Confirmado e Erro.
- Contadores correspondem à sessão carregada inteira, como indica o rótulo. Não são reduzidos pela busca textual.
- Filtro de estado e busca se combinam por interseção. Busca continua acima da tabela na Nova; não foi adicionada busca à Clássica neste corte.
- Pendente significa estritamente pending; erros têm opção própria. Isto difere da ação global Traduzir pendentes, que inclui erros para nova tentativa.
- Estado ativo e número de resultados aparecem acima do cabeçalho, com botão Todos, inclusive quando a lateral está recolhida. Todos limpa somente o estado, preservando busca.
- Sem resultados: mensagem localizada, sem reconstruir XML ou criar paginação.
- Números originais das linhas preservados. Alterações de estado atualizam contadores e entrada/saída do filtro.
- Mudança no conjunto de linhas limpa seleção/editor para evitar ações sobre linhas ocultas ou índices antigos. Confirmação múltipla usa uma cópia dos XPaths selecionados, mesmo quando as linhas desaparecem durante a operação.
- Carregar/aplicar uma estrutura com sucesso restaura Todos, juntamente com a limpeza de busca existente. Filtro não é salvo em checkpoint nem preferência.

## Escopo das ações

Filtro altera visualização, não exportação ou ações globais. Exportar, confirmar todas e traduzir pendentes mantêm o escopo de sessão. Ações da seleção usam XPaths explicitamente selecionados; nenhum envio adicional à API foi introduzido.

## Desempenho e QA

Contadores são incrementais por estado anterior conhecido, sem percorrer todo o projeto para cada contador/atualização. Aplicar filtro percorre o modelo em memória; extração XML não é repetida e tabela permanece virtualizada.

Validação: 299 testes passaram, Ruff limpo. Casos novos cobrem os cinco estados, interseção com busca, contadores globais, atualização externa do domínio, IDs originais, estado inválido, limpeza da seleção e confirmação de linhas que desaparecem.

QA offscreen: dois shells, dois temas, três dimensões, estados vazio/carregado/filtrado. Inspeção visual em Nova (1280 escuro e 1024 claro) e Clássica (1280 escuro). Testes sem chamadas reais à API ou escrita em XMLs do jogo.

## Próximo passo

Validação manual do fluxo de revisão: filtrar Traduzido, confirmar seleção, verificar Confirmado; filtrar Erro e tentar novamente. Depois revisar as prioridades restantes no backlog (idiomas demandados, versão e matriz de provedores), sem presumir autorização para release.

[[05 - Backlog]] · [[14 - Revisão Visual dos Estados]]
