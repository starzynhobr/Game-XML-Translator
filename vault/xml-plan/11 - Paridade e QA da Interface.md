# Paridade e QA da Interface

Data: 2026-09-06 · UIR-006 · **Concluído; Nova saiu do Beta.**

## Matriz de recursos

| Recurso | Clássica | Nova | Evidência nesta etapa |
|---|---|---|---|
| Carregar, estrutura multi-tag e contexto | Lateral | Barra superior + Estrutura XML | Componentes/serviços compartilhados; render com dados reais |
| Idioma, tradução de pendentes, glossário e exportação | Laterais | Barra superior | Paridade de ligação aos serviços; operações externas não executadas |
| Provedor, modelo, API, tema/contexto geral, pular linhas e reinício | Editor expandido | Seção expansível do editor | Inspeção de código; abrir/fechar seção testado |
| Tradução individual, confirmação e frases idênticas | Editor | Editor | Componente compartilhado; sem chamada a API neste QA |
| Busca e ações de seleção | Fluxo clássico existente | Barra acima da tabela | Testes de regressão existentes; não adicionar filtros de estado falsos |
| Original/tradução e seleção múltipla | Tabela compartilhada | Tabela compartilhada | Virtualização preservada; divisor e Ctrl/Shift existentes |
| Anterior/próxima e foco na tradução | Editor/tabela compartilhados | Editor/tabela compartilhados | Navegação e foco exercitados na Nova |
| Log | Painel original | Atividade recolhível (34/136 px) | Render e expansão/recolhimento exercitados |
| Configurações e escolha de interface | Diálogos compartilhados | Diálogos compartilhados | Inspeção de paridade; roteiro manual de diálogos pendente |

## Teclado entregue

- Tabela: setas, Home/End, PageUp/PageDown; Enter ou duplo clique leva ao campo de tradução com ajuste do scroll.
- Nova: Ctrl+F para busca; Ctrl+Enter para confirmar a entrada; Ctrl+S usa a ação existente de salvar no arquivo atual.
- Ctrl+S não confirma automaticamente um rascunho do editor. Confirmar primeiro, salvar depois.
- Log: cabeçalho focável e acionável por Space/Enter.
- Seleção de intervalo via Shift+teclado e auditoria completa de todos os diálogos não fazem parte deste aceite técnico.

## Evidência reproduzível

Na raiz do projeto:

```powershell
uv run pytest -q
uv run ruff check .
uv run python -m tests.qml_parity_check
```

Resultado mais recente: **334 testes passaram**, Ruff sem erros. Script GUI separado do pytest: **44 capturas por execução**, duas interfaces × dois temas (Windows Fluent/Light Azure) × três dimensões (1024×620, 1280×760, 1600×900) × vazio/carregado/filtrado, mais banner de atualização em 1024/1600 px. Fontes reais do Windows carregadas para inspeção visual.

Também executado com `characters.xml` real, extraindo 5060 entradas `action/dispName`. O argumento opcional do script recebe o caminho do XML. A carga de QA injeta entradas no modelo: não representa um teste ponta a ponta do seletor de arquivo, configuração de tags ou restauração de checkpoint. Capturas podem mostrar esses controles vazios apesar das linhas carregadas.

O script verifica avisos do engine QML, geometria de controles críticos, centralização vertical exata da busca, cinco idiomas da UI, nove idiomas de destino, anterior/próxima, seta para baixo, Enter/foco/scroll, clique, Ctrl+clique, Shift+clique, opções do provedor e altura do log. Não aciona tradução, confirmação com persistência ou sobrescrita de XML. Nenhuma chave de API é lida ou gravada pelo script.

Capturas temporárias da execução com XML real: `C:\Users\tz\AppData\Local\Temp\stz-uir006-esz0z0yi`. Não são artefatos permanentes do vault nem devem ser tratadas como teste nativo completo.

## Gate de saída do Beta

Atualização de 2026-09-04: usuário confirmou fluxo real, tradução inclusive Gemini e exportação funcionando. Mantidas abertas abaixo as verificações detalhadas que não foram explicitamente relatadas. STA-001 implementado depois desse teste; ver [[12 - Estados de Tradução]].

- [x] Abrir XML real, selecionar alvos/contexto e aplicar estrutura; serviços e controles são compartilhados pelos dois shells.
- [x] Traduzir e confirmar com provedor real; Gemini individual e em lote validados.
- [x] Exportar para uma cópia e validar o resultado; round-trip, estrutura e contexto também têm cobertura automatizada.
- [x] Salvar/checkpoint/retomada, estados e compatibilidade legada cobertos por integração.
- [x] Desabilitação, falhas seguras, cancelamento e recuperação de estados transitórios cobertos por automação.
- [x] Textos, contraste, foco, scroll, temas e dimensões validados pelo usuário e pelo QA renderizado.
- [x] Preferência Nova/Clássica, reinício e fallback cobertos pelos testes de bootstrap.

A instalação limpa e o teste de atualização/rollback do pacote pertencem ao gate de produção, não ao aceite visual de UIR-006.

## Migração e rollback

Escolher a interface em Configurações e reiniciar o aplicativo. Finalizar operações e salvar trabalho antes de fechar; não há troca de shell no meio de uma tradução. Para voltar, selecionar Clássica e reiniciar. O bootstrap mantém fallback automático se a Nova falhar ao carregar; isso não protege contra regressões em serviços ou componentes compartilhados. Manter cópias dos XMLs continua necessário.

## Fora deste aceite

Histórico de desfazer, estatísticas e descoberta mais ampla de idiomas permanecem evoluções P2. O build e o pacote 1.4.0 estão registrados em [[16 - Release 1.4.0]]; publicar a release continua uma ação separada.

Voltar: [[10 - Refatoração da Interface]] · [[05 - Backlog]] · [[06 - Decisões]].
