---
tipo: plano-mestre
status: ativo
atualizado: 2026-09-03
---

# Plano Mestre de Implementação

## Objetivo

Evoluir o STZ XML Translator sem reescrever o produto, priorizando a principal dor relatada por usuários reais: traduzir várias tags do mesmo bloco XML usando outras tags como contexto.

## Prioridade atual

> [!important] P0 — Tags de tradução e tags de contexto
> Permitir selecionar várias tags a traduzir e várias tags somente para contexto. O contexto deve ajudar o provedor sem ser alterado nem exportado como tradução.

Exemplo esperado:

```xml
<baseVillain>
  <dispName>WHIPLASH</dispName>
  <bio>An extraordinarily gifted technician...</bio>
</baseVillain>
```

- `bio`: tag a traduzir.
- `dispName`: tag de contexto.
- Resultado: uma linha para `bio`, enviada ao tradutor junto de `dispName=WHIPLASH`.
- `dispName` permanece intacta no XML.

## Ordem de execução

- [ ] 1. Fechar as decisões abertas de [[03 - P0 Tags e Contexto]].
- [ ] 2. Implementar o domínio e o extrator multi-tag.
- [ ] 3. Adaptar presets e checkpoints com migração retrocompatível.
- [ ] 4. Entregar contexto aos provedores sem misturá-lo ao texto traduzível.
- [ ] 5. Implementar seleção por chips e prévia da estrutura XML.
- [ ] 6. Cobrir o fluxo com testes e um XML real anonimizado.
- [ ] 7. Fazer QA visual e de interação em tamanhos de janela diferentes.
- [ ] 8. Seguir para estados de revisão, busca/filtros e reorganização da tela.

## Regra de andamento

Um item só muda para **Concluído** quando código, testes e validação relevante estiverem finalizados. Código presente apenas no working tree fica como **Em validação**, não como entregue.

## Navegação

1. [[01 - Visão do Produto]]
2. [[02 - Estado Atual e Evidências]]
3. [[03 - P0 Tags e Contexto]]
4. [[04 - Roadmap]]
5. [[05 - Backlog]]
6. [[06 - Decisões]]
7. [[07 - Design e Interface]]
8. [[08 - Qualidade, Dados e Release]]
9. [[09 - Diário de Implementação]]
10. [[10 - Refatoração da Interface]]

## Definição de pronto do plano

- O usuário consegue escolher mais de uma tag de destino.
- O usuário consegue escolher tags adicionais apenas como contexto.
- O XML exportado altera somente as tags escolhidas para tradução.
- Presets antigos continuam funcionando.
- Provedores sem suporte seguro a contexto deixam isso claro.
- Arquivos grandes continuam navegáveis e a tradução pode ser retomada.
- Versão exibida, pacote e release deixam de divergir.

Próximo: [[01 - Visão do Produto]].
