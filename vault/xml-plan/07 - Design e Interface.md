---
tipo: design
status: direcao-aprovavel
atualizado: 2026-09-03
---

# Design e Interface

## Direção

Ferramenta desktop densa e organizada, com superfícies neutras, uma cor de destaque e hierarquia baseada primeiro em posição, espaçamento e tipografia. A referência fornecida orienta a organização, mas não será copiada literalmente.

## Estrutura recomendada

```text
┌ Barra global: arquivo · idioma · progresso · traduzir · glossário · configurações · exportar ┐
├ Estrutura e filtros ┬ Tabela virtualizada ┬ Editor e contexto ┤
│ busca               │ tag | original      │ contexto do pai   │
│ status              │ tradução | status  │ original           │
│ tag pai             │                     │ tradução           │
│ alvos [chips]       │                     │ ações do item      │
│ contexto [chips]    │                     │ provedor           │
├─────────────────────┴─────────────────────┴────────────────────┤
│ Atalhos · resumo                         Log técnico recolhível │
└────────────────────────────────────────────────────────────────┘
```

## Estratégia de migração

- `Clássica`: fluxo atual preservado e selecionável.
- `Nova (Beta)`: entrada separada, construída em cortes pequenos sobre o mesmo ViewModel.
- A troca é feita em Configurações e entra no próximo início para evitar reconstruir a árvore QML com uma tradução em andamento.
- Falha ao carregar a Nova tenta a Clássica automaticamente.
- Componentes e backend continuam compartilhados; cada corte exige teste de paridade para reduzir o risco comum às duas interfaces.

Na fundação UIR-001, a Nova reutilizava deliberadamente a composição Clássica. Em UIR-002 ela ganhou uma árvore própria, com regiões nomeadas e componentes funcionais compartilhados. A composição visual foi mantida equivalente antes da entrada da barra superior em UIR-003.

## Busca e filtros

- Busca textual: barra compacta acima do cabeçalho da tabela, porque seu resultado e seu escopo pertencem à lista central.
- Filtros persistentes: lateral esquerda, agrupados por estado e estrutura XML.
- A busca cobre original, tradução, tag e contexto; exibe quantidade encontrada e pode ser limpa sem alterar filtros.
- Atalhos previstos: `Ctrl+F` foca a busca e `Esc` limpa ou devolve o foco à tabela.

## Hierarquia de ações

- Primária global: **Traduzir pendentes**.
- Primária contextual: **Traduzir seleção** ou **Confirmar tradução**.
- Secundárias globais: glossário, configurações e exportar.
- Cautelosa: salvar sobre o arquivo atual, separada de exportar.
- Destrutivas: redefinir traduções e sobrescrever sempre exigem escopo claro e confirmação adequada.

### Barra superior da Nova (UIR-003)

- Grupo de arquivo: carregar XML e identificar o arquivo selecionado.
- Grupo de execução: idioma de destino, progresso numérico e barra de progresso.
- Grupo de ações: Traduzir pendentes como ação primária; Glossário, Configurações e Exportar XML como secundárias.
- Em largura regular/ampla, os três grupos ocupam uma linha.
- No limite de 1024 px, as ações passam para uma segunda linha sem rolagem horizontal nem perda do editor.
- Os controles equivalentes antigos permanecem acessíveis durante a transição e serão tratados em UIR-004/QA de paridade.

### Lateral de estrutura da Nova (UIR-004)

- A lateral da Nova contém apenas Estrutura XML, aplicação da seleção e a ação cautelosa de salvar no arquivo atual.
- Carregar XML, idioma, progresso, exportação e acesso às configurações foram removidos da lateral somente na Nova, pois já estão disponíveis na barra superior.
- O rótulo `Recarregar` virou `Aplicar estrutura`, descrevendo o efeito real da ação.
- Em larguras a partir de 1120 px a lateral inicia expandida; abaixo disso inicia recolhida e mantém um controle explícito para reabrir.
- A Clássica preserva integralmente a lateral anterior.
- Filtros de estado não aparecem antes de `STA-001/FIL-002`; não haverá controles visuais sem comportamento e persistência correspondentes.

## P0 na interface

### Estrutura XML

- `Tag pai`: seletor único pesquisável.
- `Tags a traduzir`: seletor múltiplo com chips e contagem.
- `Tags de contexto`: seletor múltiplo visualmente diferente, mas sem depender só de cor.
- Tags já usadas em uma lista ficam indisponíveis na outra, com explicação curta.
- Botão **Aplicar estrutura** substitui uma recarga ambígua.
- Prévia informa `N registros · M linhas · C campos de contexto`.

### Tabela

- Nova coluna compacta `Tag` antes de `Texto original`.
- Estado continua textual além da cor.
- Não adicionar paginação; preservar virtualização e seleção Ctrl/Shift.
- Ao selecionar várias linhas, mostrar uma barra contextual com quantidade e alcance das ações.

### Editor

- Mostrar contexto acima do original em pares `tag: valor` somente leitura.
- Permitir copiar valores de contexto.
- Exibir um aviso quando o provedor atual não usa contexto.
- Manter original e tradução próximos e com alturas redimensionáveis.

## Responsividade de desktop

- Largura ampla: três colunas.
- Largura regular: lateral esquerda estreita e editor preservado.
- Largura estreita: uma lateral aberta por vez; tabela nunca fica espremida abaixo de uma largura útil.
- Estados das laterais podem ser lembrados localmente, mas não entram no preset de XML.
- Rótulos longos dos cinco idiomas devem ser testados; não fixar a geometria pelo português.

## Estados obrigatórios

- vazio antes de carregar XML;
- analisando estrutura;
- nenhum alvo selecionado;
- combinação inválida de alvo/contexto;
- nenhuma linha encontrada;
- traduzindo e cancelando;
- item traduzido, confirmado e com erro;
- provedor sem suporte a contexto;
- arquivo alterado externamente ou falha ao salvar.

## Acessibilidade e interação

- Foco visível em chips, tabela, campos e botões.
- Remoção de chip acessível por teclado.
- Estado não comunicado apenas por verde/amarelo/vermelho.
- Tooltips complementam rótulos; não substituem ações frequentes.
- Alvos de clique adequados e textos desabilitados legíveis nos temas claros e escuros.

## Itens da referência que não entram agora

- Paginação.
- `Confirmado por` e autoria multiusuário.
- Data de modificação por item sem persistência correspondente.
- Botão de desfazer sem histórico real.
- Painéis de estatísticas sem decisão de produto associada.

## QA visual obrigatório após implementação

- Capturar o app vazio e com XML carregado.
- Comparar 1024×720, 1280×800 e largura ampla.
- Testar ao menos um tema claro e um escuro.
- Verificar textos longos em português e alemão/idioma longo quando disponível; na ausência, usar strings de teste.
- Verificar seleção, foco, hover, disabled, loading, error e scroll.

Anterior: [[06 - Decisões]] · Próximo: [[08 - Qualidade, Dados e Release]] · Plano de migração: [[10 - Refatoração da Interface]].
