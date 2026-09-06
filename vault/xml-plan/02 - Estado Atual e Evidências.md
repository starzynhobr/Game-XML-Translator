---
tipo: inventario
status: ativo
atualizado: 2026-09-03
---

# Estado Atual e Evidências

## Produto existente

- Python 3.12, PySide6 e QML.
- Provedores: Google Translate, Gemini, DeepL, Azure e Ollama.
- Tabela virtualizada, edição individual, lote, checkpoint, importação e exportação.
- Cinco idiomas de interface e cinco temas.
- Presets de tags e glossário.

## Limites confirmados no código

| Área | Estado atual | Consequência |
|---|---|---|
| Extração | `extrair_textos(arquivo, parent_tag, target_tag)` aceita uma tag alvo | O usuário repete o carregamento para cada campo |
| Projeto | Guarda `parent_tag` e `target_tag` como strings | Não representa várias tags nem contexto |
| Entrada | XPath, original, tradução e `pending/translating/done` | Não distingue traduzido, confirmado e erro |
| Presets | Identidade por rótulo + tag pai + tag alvo | Precisa de migração para listas |
| Checkpoint | Nome por caminho do XML + idioma | Configurações diferentes do mesmo arquivo podem compartilhar checkpoint |
| Tabela | Já suporta seleção Ctrl/Shift no working tree | Base pronta para ações em lote selecionadas |
| Duplicatas | Propagação exata já está no working tree | Precisa de validação e decisão de UX |
| Glossário | Ajustes para Gemini e DeepL estão no working tree | Ainda não tratar como release publicada |
| Versão | Há referências locais a 1.2.x e release/tag 1.3.0 | Fonte de versão está divergente |

## Working tree em 2026-09-03

Há alterações não commitadas em domínio, provedores, worker, QML, ViewModel, traduções e testes. Elas incluem glossário, seleção múltipla e duplicatas exatas. Devem ser preservadas e validadas antes de qualquer refatoração de tags.

## Hipóteses a validar com XML real

- As tags de contexto úteis são normalmente filhas diretas do mesmo elemento pai.
- Uma linha por tag traduzível é mais compreensível que uma linha agregando vários campos.
- O nome da tag e os pares `tag=valor` fornecem contexto suficiente para a maioria dos provedores de IA.
- Alguns arquivos usam namespaces, tags aninhadas ou conteúdo misto; a solução não pode assumir apenas XML simples.

## Riscos técnicos já visíveis

- `xml.etree.ElementTree` e XPath construído por string têm limitações com namespaces.
- Alterar o formato de retorno do extrator afeta projeto, ViewModel, exportação e testes.
- Injetar contexto concatenado no texto pode fazer um provedor traduzir ou devolver o contexto junto.
- Salvar traduções após mudar a seleção de tags pode restaurar dados de checkpoint indevidos se a configuração não fizer parte da identidade.
- A reorganização visual pode comprimir a tabela em janelas menores se as duas laterais forem fixas.

## Evidência necessária antes de encerrar P0

- Fixture pequena cobrindo duas tags alvo e duas tags de contexto.
- Fixture com tag ausente e contexto vazio.
- Fixture com namespace.
- Exportação comparada nó a nó: somente alvos selecionados mudam.
- Teste de migração de preset antigo.
- Execução com ao menos um provedor de IA e um provedor sem contexto nativo.

Anterior: [[01 - Visão do Produto]] · Próximo: [[03 - P0 Tags e Contexto]].
