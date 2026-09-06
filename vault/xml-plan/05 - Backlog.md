---
tipo: backlog
status: ativo
atualizado: 2026-09-06
---

# Backlog

## Convenções

- Estados: `Ideia`, `Pronto`, `Em andamento`, `Em validação`, `Bloqueado`, `Concluído`.
- Prioridades: `P0` bloqueia o objetivo atual; `P1` alto valor; `P2` melhoria posterior.
- Cada item concluído deve apontar para evidência em [[09 - Diário de Implementação]].

## P0 — Dor principal

| ID | Entrega | Estado | Dependências | Aceite resumido |
|---|---|---|---|---|
| TAG-001 | Criar modelo tipado de entrada extraída | Concluído | — | `ExtractedEntry` representa alvo, pai e contexto |
| TAG-002 | Extrair várias tags e contexto em uma passagem | Concluído | TAG-001 | Uma linha por XPath, contexto isolado por pai |
| TAG-003 | Adaptar `TranslationProject` | Concluído | TAG-002 | Aceita lista e mantém chamada singular compatível |
| TAG-004 | Migrar presets antigos | Concluído | TAG-003 | Leitura não reescreve; salvamento explícito usa listas |
| TAG-005 | Isolar checkpoints por seleção de tags | Concluído | TAG-003 | Assinatura estável e fallback legado controlado |
| TAG-006 | Passar contexto aos provedores compatíveis | Concluído | TAG-002 | Gemini/Ollama delimitado, DeepL nativo, demais avisam |
| TAG-007 | Seletor QML multi-tag com chips | Concluído | TAG-003 | Alvo e contexto distinguíveis e acessíveis |
| TAG-008 | Exibir tag e contexto da linha | Concluído | TAG-003, TAG-007 | Origem da linha fica inequívoca |
| TAG-009 | Testar exportação e migrações | Concluído | TAG-004 a TAG-008 | Round-trip simples, namespace e XML real cobertos |

## P0 — Estabilização já iniciada

| ID | Entrega | Estado | Observação |
|---|---|---|---|
| GLO-001 | Glossário no Gemini individual e em lote | Concluído | Prompt individual/lote coberto e fluxo real Gemini validado |
| GLO-002 | Glossário protegido no DeepL | Em validação | Automação aprovada; requer smoke real com credencial DeepL |
| BULK-001 | Seleção múltipla Ctrl/Shift | Concluído | Interações reais no QML validam clique, Ctrl e Shift |
| BULK-002 | Traduzir somente linhas selecionadas | Concluído | ViewModel e worker limitam o lote aos XPaths selecionados |
| DUP-001 | Aplicar tradução a duplicatas exatas | Concluído | Alcance exato e somente pendentes cobertos no domínio e ViewModel |

## P0 — Desempenho com XML real

| ID | Entrega | Estado | Dependências | Aceite resumido |
|---|---|---|---|---|
| PERF-001 | Indexação reutilizável e carregamento assíncrono | Concluído | TAG-009 | XML de 11,3 MB analisado sem bloquear a UI; prévia e extração deixam de repetir o custo quadrático de XPath |

## P1 — Revisão e navegação

| ID | Entrega | Estado | Dependências |
|---|---|---|---|
| STA-001 | Expandir máquina de estados | Concluído — domínio, integração e checkpoint v2 | TAG-004; ver nota 12 |
| STA-002 | Persistir erro por entrada | Concluído — diagnóstico categorizado e checkpoint | STA-001; ver nota 13 |
| STA-003 | Separar traduzido de confirmado | Concluído — rótulos, editor e diagnóstico localizado | STA-001, STA-002 |
| FIL-001 | Busca por texto, tag e contexto | Concluído | TAG-009 |
| FIL-002 | Filtros e contadores por estado | Concluído — filtro combinado, contadores e seleção segura | STA-001 a STA-003; nota 15 |
| BULK-003 | Barra de ações da seleção | Concluído | BULK-001 |
| KEY-001 | Navegação por teclado | Concluído | Setas, Home/End, PageUp/PageDown, Enter, foco, Ctrl+F, Ctrl+Enter e Ctrl+S validados |
| LOG-001 | Log inferior recolhível | Concluído | UIR-006 |

## P1 — Migração segura da interface

| ID | Entrega | Estado | Dependências |
|---|---|---|---|
| UIR-001 | Duas entradas QML, preferência e fallback clássico | Concluído | — |
| UIR-002 | Shell independente da Nova (Beta) | Concluído | UIR-001 |
| UIR-003 | Barra superior com ações globais | Concluído | UIR-002 |
| UIR-004 | Reorganizar estrutura e filtros na lateral esquerda | Concluído | UIR-003 |
| UIR-004.1 | Divisor redimensionável entre original e tradução | Concluído | UIR-004 |
| UIR-004.2 | Ação Traduzir pendentes compacta e responsiva | Concluído | UIR-003 |
| UIR-005 | Busca acima da tabela e barra de seleção | Concluído | UIR-004, FIL-001, BULK-003 |
| UIR-006 | Paridade, QA responsivo e saída do Beta | Concluído | Validação do usuário + QA automatizado dos dois shells; ver matriz 11 |

Fluxo detalhado: [[10 - Refatoração da Interface]].

## P1 — Consistência do produto

| ID | Entrega | Estado | Dependências |
|---|---|---|---|
| VER-001 | Unificar versão do app e da release | Concluído | Fonte canônica 1.4.0.0, app/PE/Setup 1.4.0 e guardas de CI |
| DOC-001 | Atualizar Quick Start para `uv` | Concluído | README usa o fluxo `uv` atual |
| I18N-001 | Revisar paridade dos novos textos | Concluído | Cinco locales com chaves equivalentes, sem valores vazios |
| API-001 | Matriz de capacidades dos provedores | Ideia | TAG-007 |
| API-002 | Descoberta dinâmica e política de fallback de modelos Gemini | Concluído | Descoberta pela API, seleção persistida, candidatos compatíveis e erros claros |

## P0 — Distribuição e atualização da 1.4.0

| ID | Entrega | Estado | Evidência |
|---|---|---|---|
| PKG-001 | Substituir a distribuição principal MSIX por Inno Setup | Concluído | Setup por usuário, editor STZ Labs, CI e ZIP portátil |
| UPD-001 | Consultar e comparar releases em segundo plano | Concluído | GitHub latest, SemVer, intervalo diário, drafts/prereleases ignorados |
| UPD-002 | Banner e verificação manual nas Configurações | Concluído | Componente compartilhado nos dois shells e textos nos cinco locales |
| UPD-003 | Download com progresso e SHA-256 obrigatório | Concluído | Arquivo parcial, troca atômica, digest e erros seguros cobertos |
| UPD-004 | Abrir Setup, encerrar app e validar atualização real | Em validação | Lançamento/guardas automatizados; requer 1.4.0 publicada para teste real |

## P1 — Novos idiomas com demanda observada

Estes itens representam primeiro **idiomas de destino da tradução**. Localizar toda a interface para cada idioma é um trabalho separado.

| ID | Entrega | Estado | Evidência |
|---|---|---|---|
| LANG-001 | Adicionar italiano (`it`, DeepL `IT`) | Concluído | Smoke real Google: `L'eroe protegge la città.` |
| LANG-002 | Adicionar russo (`ru`, DeepL `RU`) | Concluído | Smoke real Google: `Герой защищает город.` |
| LANG-003 | Adicionar dinamarquês (`da`, DeepL `DA`) | Concluído | Smoke real Google: `Helten beskytter byen.` |
| LANG-004 | Adicionar turco (`tr`, DeepL `TR`) | Concluído | Smoke real Google: `Kahraman şehri korur.` |

Critérios comuns: aparecer no seletor de destino, mapear códigos por provedor, persistir a escolha, gerar checkpoint separado e passar por ao menos um smoke test real em provedor compatível.

## P2 — Evoluções futuras

| ID | Entrega | Estado | Nota |
|---|---|---|---|
| UX-001 | Histórico real de desfazer | Ideia | Não exibir botão antes do mecanismo existir |
| TM-001 | Memória de tradução exata persistente | Ideia | Evolução das duplicatas |
| LANG-005 | Melhorar descoberta de idiomas por provedor | Ideia | Evitar prometer pares incompatíveis |
| STAT-001 | Estatísticas detalhadas úteis | Ideia | Só após definir decisões que elas apoiam |

## Modelo de atualização de item

```text
ID: TAG-002
Estado: Em andamento
Mudança: ...
Critério sendo atendido: ...
Evidência/teste: ...
Risco ou bloqueio: ...
Próximo passo: ...
```

Anterior: [[04 - Roadmap]] · Próximo: [[06 - Decisões]].
