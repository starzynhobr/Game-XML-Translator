# STA-001 — Estados de tradução

Implementado em 2026-09-04. Referência: [[04 - Roadmap#Fase 2 — Revisão confiável]].

| Estado | Significado | Traduzir pendentes |
|---|---|---|
| pending | Sem tradução concluída | Inclui |
| translating | Requisição em andamento | Exclui |
| translated | Texto gerado/importado, ainda sem confirmação | Exclui |
| confirmed | Confirmação explícita individual, seleção ou todas | Exclui |
| error | Falha ou resposta ausente/vazia | Inclui para nova tentativa |

## Regras

- Tradução recebida/importada entra como translated; confirmar texto não vazio entra como confirmed.
- Alterar texto pelo domínio invalida confirmação anterior; texto vazio retorna a pending. Rascunho ainda não aplicado no editor não altera o domínio.
- Não confirmar entrada em translating. Indicador de atividade não substitui o conteúdo por reticências.
- Erro mantém texto anterior, quando existente; mensagem de API não é gravada como tradução. Detalhes persistentes de erro continuam em STA-002.
- Cancelamento recupera entradas em translating para translated se havia texto ou pending se vazias. Não presume confirmação depois de uma operação interrompida.
- Tradução explícita da seleção pode refazer entradas já traduzidas/confirmadas; pendentes não as refaz.
- Estatística de progresso existente soma translated + confirmed. Contadores por estado estão disponíveis no domínio, não expostos como filtros nesta etapa.
- Exportação mantém compatibilidade: exporta textos não vazios, sem exigir confirmação; em caso de falha ao retraduzir, preserva a tradução anterior.

## Persistência e compatibilidade

Checkpoint v2 contém version e entries, com translation/status por XPath. Lê o formato antigo XPath → texto e o alias done como translated, nunca como confirmed. Estados transitórios são recuperados na leitura. Arquivos inválidos/versões desconhecidas não são aplicados. Confirmação explícita e tradução individual salvam checkpoint; lote salva progresso também ao terminar/cancelar.

Programas antigos não entendem o formato v2: manter cópias dos checkpoints antes de voltar a um executável anterior. Clássica e Nova deste checkout compartilham o mesmo leitor v2. XMLs exportados não recebem metadados de estado.

## Verificação

- `uv run pytest -q`: 268 testes passaram, incluindo 22 testes novos de estados e integração.
- `uv run ruff check .`: sem erros.
- `uv run python -m tests.qml_parity_check`: 24 cenários offscreen; dois shells, dois temas e três dimensões; navegação/foco/log.
- Provedores simulados nos testes; nenhuma chamada real ou alteração em XML do jogo nesta etapa.

## Próximo passo

STA-002 concluído: [[13 - Diagnóstico por Entrada]]. Próximo: concluir STA-003 na apresentação (traduzido × confirmado × erro e diagnóstico) e FIL-002 nos filtros/contadores. translated e confirmed ainda compartilham o destaque verde existente.

[[05 - Backlog]] · [[09 - Diário de Implementação]]
