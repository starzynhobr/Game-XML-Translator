# STA-003 — Revisão visual dos estados

Implementado em 2026-09-04, nos componentes compartilhados por Clássica e Nova.

- Rótulo textual na coluna de tradução: pendente, traduzindo, traduzido, confirmado ou erro. O rótulo não altera o texto exportado.
- Verde reservado a confirmado; erro usa superfície semântica de erro; seleção continua com destaque próprio. Cor não é a única indicação.
- Editor mostra estado e diagnóstico da entrada selecionada. Alterações do modelo atualizam essas informações sem exigir nova seleção.
- Entrada com erro mostra Tentar novamente no botão de tradução individual. Mantém o fluxo existente, sem retry automático. Seleção múltipla mantém sua ação de lote.
- Botão bloqueado enquanto há tradução individual, lote ou operação XML.
- Estados, mensagens seguras e ação localizados nos cinco idiomas da UI.

## Validação

QA offscreen: 24 cenários, dois shells × dois temas × três tamanhos × vazio/carregado. Dados sintéticos incluem confirmed, translated e error. Inspeção visual da Nova em 1280 escuro e 1024 claro; navegação/foco/log também exercitados. Não foi executada nova chamada real à API.

Teste de regressão verifica atualização após confirmação e erro, revisão do modelo e seleção inexistente. Testes completos e Ruff executados ao finalizar. Catálogo de mensagens traduzido nesta etapa; recomenda-se revisão linguística por falantes nativos.

## Próximo passo

FIL-002: filtros e contadores por estado. O rótulo compacto foi integrado à coluna de tradução existente para preservar largura e redimensionamento; não foi criada uma quarta coluna neste corte.

[[05 - Backlog]] · [[13 - Diagnóstico por Entrada]]
