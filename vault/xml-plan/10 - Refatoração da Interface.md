---
tipo: plano
status: em-andamento
atualizado: 2026-09-04
---

# Refatoração da Interface

## Objetivo

Migrar gradualmente para a organização da referência sem interromper o fluxo já usado. Clássica e Nova (Beta) compartilham domínio e ViewModel; o trabalho novo fica concentrado na composição QML.

## Princípios

- Preservar recursos antes de mudar sua posição.
- Um corte deve iniciar e terminar utilizável.
- A Nova não substitui a Clássica até atingir paridade e passar pelo QA com XML real.
- Ações globais ficam na barra superior; ações da linha ficam no editor; ações de seleção ficam junto à tabela.
- Busca textual fica acima da tabela; filtros e estrutura XML ficam na lateral esquerda.
- Não adicionar paginação à tabela virtualizada.

## Linha de implementação

### UIR-001 — Fundação das duas interfaces

**Estado:** concluído.

- [x] Persistir `classic` ou `modern`.
- [x] Expor seleção em Configurações.
- [x] Aplicar a troca no próximo início.
- [x] Carregar entradas QML separadas.
- [x] Voltar automaticamente à Clássica se a Nova falhar ao iniciar.
- [x] Cobrir seleção, persistência e fallback com testes.

### UIR-002 — Shell independente da Nova

**Estado:** concluído.

- [x] Criar layout raiz próprio sem duplicar regras de negócio.
- [x] Reutilizar tabela, editor e componentes existentes inicialmente.
- [x] Definir regiões nomeadas para barra global, lateral, tabela, editor e rodapé/log.
- [x] Preservar estados vazio, carregado e traduzindo.
- [x] Comparar Clássica e Nova nas mesmas dimensões e com o mesmo estado.

**Aceite:** a Nova deixa de ser apenas uma casca da Clássica, abre sem warnings e mantém as ações principais alcançáveis.

### UIR-003 — Barra superior

**Estado:** concluído.

- [x] Carregar XML e mostrar nome/estado do arquivo.
- [x] Selecionar idioma de destino.
- [x] Mostrar progresso sem competir com a ação principal.
- [x] Expor Traduzir pendentes, Glossário, Configurações e Exportar.
- [x] Manter sobrescrita do arquivo como ação cautelosa, fora do destaque primário.
- [x] Reorganizar a barra em duas linhas no limite de 1024 px.

**Aceite:** o fluxo global pode ser entendido e iniciado pela barra sem procurar controles nas laterais.

### UIR-004 — Lateral esquerda

**Estado:** concluído.

- [x] Agrupar Tag pai, alvos e contexto como Estrutura XML.
- [x] Substituir rótulo ambíguo de recarga por Aplicar estrutura.
- [x] Remover da Nova os controles globais já disponíveis na barra superior.
- [x] Preservar a lateral completa da Clássica.
- [x] Permitir recolher a lateral e iniciar recolhida abaixo de 1120 px.
- [x] Adiar filtros para `STA-001/FIL-002`, evitando controles sem estado confiável.

**Aceite:** configuração estrutural e filtros permanecem legíveis sem consumir espaço desnecessário da tabela.

#### Complementos de QA

- [x] **UIR-004.1:** permitir redimensionar original/tradução pelo divisor do cabeçalho, mantendo 160 px mínimos por coluna e duplo clique para restaurar 45/55.
- [x] **UIR-004.2:** limitar `Traduzir pendentes` a 188 px preferenciais e manter o grupo alinhado à direita nas barras de uma e duas linhas.

### UIR-005 — Busca e ações da tabela

**Estado:** concluído.

- [x] Busca sobre original, tradução, tag e contexto.
- [x] Barra acima do cabeçalho com contagem, limpar, `Ctrl+F` e `Esc`.
- [x] Barra contextual ao selecionar várias linhas.
- [x] Manter Ctrl/Shift e virtualização.

**Aceite:** encontrar e agir sobre um subconjunto não exige percorrer o XML inteiro.

### UIR-006 — Paridade e saída do Beta

**Estado:** paridade técnica implementada; saída do Beta em validação manual.

- [x] Matriz de recursos Clássica × Nova: [[11 - Paridade e QA da Interface]].
- [x] QA offscreen vazio e com XML real em 1024 × 620, 1280 × 760 e 1600 × 900.
- [x] Render claro/escuro e verificações de navegação, foco, scroll e geometria em cinco idiomas.
- [ ] Validação manual nativa completa, incluindo diálogos, operações reais e estados ocupados.
- [x] Manter Clássica como modo suportado durante o Beta.
- [x] Documentar migração e rollback na matriz.

Complementos entregues: editor compacto na Nova com opções do provedor expansíveis; ações globais sem duplicação no editor; log recolhível; navegação entre entradas e foco no campo de tradução. A referência não implica implementar filtros/estados fictícios: STA-001/FIL-002 continuam separados.

**Aceite:** nenhuma função usada no fluxo real existe apenas na Clássica sem decisão explícita.

## Riscos e controles

| Risco | Controle |
|---|---|
| Componentes compartilhados quebrarem os dois modos | Testes de instanciação e paridade a cada corte |
| Nova acumular controles sem hierarquia | Mover por regiões e validar a ação primária em cada etapa |
| Preferência prender usuário em shell quebrado | Fallback automático de carregamento |
| Troca durante tradução perder estado | Aplicar somente no próximo início |
| Clássica impedir evolução indefinidamente | Critérios objetivos em UIR-006 para decidir seu destino |

## Próxima ação

Executar o roteiro manual de [[11 - Paridade e QA da Interface]] antes de retirar o Beta. O próximo incremento funcional é STA-001, base para FIL-002; a descoberta dinâmica de modelos Gemini fica em API-002.

Anterior: [[09 - Diário de Implementação]] · Decisões: [[06 - Decisões#DEC-012 — Duas interfaces durante a migração]].
