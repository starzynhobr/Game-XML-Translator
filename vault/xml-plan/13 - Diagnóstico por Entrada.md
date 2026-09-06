# STA-002 — Diagnóstico por entrada

Implementado em 2026-09-04. Continua [[12 - Estados de Tradução]].

## Entrega

- Cada entrada tem error_code e uma mensagem derivada de catálogo fechado.
- Categorias: credencial/acesso, limite/cota, indisponibilidade, conexão/timeout, resposta vazia, resultado ausente no lote, falha de lote sem detalhe e desconhecido.
- Checkpoint v2 recebe error_code opcional; versões anteriores do v2 sem esse campo continuam legíveis. Erro sem diagnóstico recebe unknown.
- A mensagem é derivada do código ao ler, sem duplicar texto livre no checkpoint. Valores desconhecidos ou malformados são normalizados.
- Recarregar estrutura preserva o diagnóstico da entrada. Nova tentativa, sucesso, confirmação e reinício limpam o erro anterior.
- Tradução anterior continua preservada em caso de falha; XML/CSV não recebem mensagens de erro.
- O modelo QML expõe errorCode/errorMessage com notificação. A apresentação no editor e localização dessas mensagens ficam para STA-003; não foi adicionado painel nesta etapa.

## Diagnóstico e privacidade

Exceções do worker são classificadas, não persistidas como texto bruto nem encaminhadas cruas aos seus logs/erro individual. Não há armazenamento de chave, URL, prompt ou corpo de resposta no diagnóstico. Classificação textual é aproximada; desconhecido é preferível a inventar um motivo. Adaptadores que retornam apenas None recebem batch_failed, sem alegar conhecer a causa. Isto não é uma auditoria de todos os logs do aplicativo.

Gemini preserva a categoria da exceção de lote para as entradas afetadas. Resposta parcial marca missing_result somente nos itens ausentes/vazios. Ollama mantém tentativa individual quando o mini-lote falha. Nenhuma política nova de retry automático ou troca de modelo foi introduzida.

## Validação

- `uv run pytest -q`: 289 testes passaram (21 novos).
- Casos: classificação, checkpoint/retomada, campos inválidos, limpeza de diagnóstico, segurança dos logs/checkpoint Gemini, erro seguido de sucesso, lote parcial, roles QML e recarga estrutural.
- `uv run ruff check .`: limpo.
- Provedores simulados; sem usar chaves reais ou editar XMLs do jogo.

## Próximo passo

STA-003: mostrar estado e diagnóstico no editor/tabela, localizar mensagens e tornar a nova tentativa explícita. Em seguida FIL-002: filtros e contadores por estado.

[[05 - Backlog]] · [[09 - Diário de Implementação]]
