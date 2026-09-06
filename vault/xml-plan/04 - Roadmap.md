---
tipo: roadmap
status: ativo
atualizado: 2026-09-06
---

# Roadmap

O roadmap é orientado por dependências e critérios de saída, não por datas artificiais.

## Fase 0 — Estabilizar o que já foi iniciado

**Objetivo:** preservar o trabalho atual e estabelecer uma linha de base confiável.

- Revisar o diff de glossário, seleção múltipla e duplicatas.
- Executar testes, lint e inicialização QML.
- Fazer teste manual mínimo dos três fluxos.
- Registrar limitações de APIs não testadas ao vivo.

**Saída:** working tree conhecido, alterações agrupáveis e nenhum comportamento anterior quebrado.

## Fase 1 — P0 Tags e contexto

**Estado:** concluída em 2026-09-04.

**Objetivo:** resolver a dor relatada pelo usuário sem depender da reorganização completa da interface.

- Modelo e extração multi-tag.
- Contexto por ocorrência da tag pai.
- Presets e checkpoints retrocompatíveis.
- Contrato de contexto para provedores.
- Seletor multi-tag e painel de contexto.
- Testes com XMLs representativos.

**Saída:** todos os critérios de [[03 - P0 Tags e Contexto#Critérios de aceite]] atendidos.

## Fase 2 — Revisão confiável

**Estado:** concluída em 2026-09-05.

**Objetivo:** deixar claro o que foi gerado, revisado ou falhou.

- Estados `pending`, `translating`, `translated`, `confirmed` e `error`.
- Mensagem de erro por entrada e ação de tentar novamente.
- Confirmação individual e em lote sobre uma seleção.
- Filtros por estado com contadores.
- Migração de checkpoint/importação para o novo estado.

**Saída:** nenhuma tradução gerada é apresentada como confirmada sem ação explícita.

## Corte de desempenho — XMLs grandes

**Estado:** PERF-001 concluído em 2026-09-04.

- Índice reutilizável por arquivo para estrutura, prévia e extração.
- Prévia baseada em contagem, sem construir entradas ou XPaths.
- XPath linear por grupos de irmãos indexados uma vez.
- Análise e aplicação fora da thread visual, com feedback de carregamento.

**Saída medida:** no `characters.xml` real de 11,3 MB, prévia de 5.060 linhas em cerca de 5 ms e extração indexada em cerca de 32 ms após a análise inicial.

## Trilha paralela — Migração segura da interface

**Estado:** concluída em 2026-09-06; Clássica permanece disponível como rollback.

Esta trilha pode avançar em cortes pequenos sem bloquear o domínio. A interface clássica permanece selecionável enquanto a Nova (Beta) ganha paridade.

1. Fundação com duas entradas QML, preferência persistida e fallback automático.
2. Shell da Nova independente da composição clássica.
3. Barra superior com arquivo, idioma, progresso e ações globais.
4. Lateral esquerda com estrutura XML; filtros de estado permanecem em FIL-002.
5. Busca contextual acima da tabela e ações de seleção. **Concluída.**
6. Paridade funcional, QA visual e saída do modo Beta. **Concluída.**

Detalhamento e critérios: [[10 - Refatoração da Interface]].

## Fase 3 — Encontrar e agir em escala

**Estado:** concluída em 2026-09-06.

**Objetivo:** reduzir esforço em XMLs grandes.

- Busca em original, tradução, tag e contexto.
- Barra contextual para seleção múltipla.
- Propagação de duplicatas exatas com prévia do alcance.
- Atalhos de navegação, edição, confirmação e salvamento.
- Log técnico recolhível.

**Saída:** o usuário encontra pendências, seleciona um subconjunto e conclui ações sem percorrer a lista inteira.

## Fase 4 — Organização visual responsiva

**Estado:** concluída em 2026-09-06.

**Objetivo:** aplicar a hierarquia da referência sem copiar seus pontos fracos.

- Barra superior para o fluxo global.
- Lateral esquerda para busca, filtros e estrutura XML.
- Tabela central virtualizada sem paginação.
- Editor/contexto na lateral direita.
- Laterais recolhíveis e comportamento para janelas estreitas.
- QA visual em temas claros e escuros.

**Saída:** fluxo principal visível, tabela preservada e nenhum controle inacessível ao redimensionar.

### Situação em 2026-09-06

UIR-001 a UIR-006 entregues. A Nova saiu do Beta após validação visual do usuário, fluxo real e QA automatizado responsivo; a Clássica segue suportada como retorno seguro. Estados, filtros, busca, seleção em massa, duplicatas, teclado e atividade também estão concluídos.

## Fase 5 — Release coerente

**Estado:** implementação da candidata 1.4.0 concluída; faltam smoke real do glossário DeepL, build local do Setup e instalação/atualização/rollback.

**Objetivo:** preparar uma versão distribuível e diagnosticável.

- Resolver a fonte única da versão.
- Atualizar textos/documentação que ainda mencionam 1.2.
- Matriz de testes dos provedores.
- Build Nuitka standalone e Setup Inno conforme as regras do repositório.
- Notas de migração e release.
- Atualizador assistido para as versões posteriores à 1.4.0.

**Saída:** título do app, metadados, pacote, tag e release exibem a mesma versão.

Checklist e notas: [[16 - Release 1.4.0]].

## Dependências

```text
Estabilização
  → Tags e contexto
    → Estados de revisão
      → Busca e ações em escala
        → Reorganização visual
          → Release
```

Observação: melhorias visuais locais podem acompanhar cada fase; a mudança completa do shell só ocorre depois que o modelo de dados estiver estável.

Anterior: [[03 - P0 Tags e Contexto]] · Próximo: [[05 - Backlog]].
