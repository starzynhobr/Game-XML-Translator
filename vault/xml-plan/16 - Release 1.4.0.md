---
tipo: release
versao: 1.4.0
status: candidata
atualizado: 2026-09-06
---

# Release 1.4.0

Esta é a candidata de produção posterior à 1.3.0. O código e o executável standalone foram gerados e validados localmente. O Setup Inno substituiu o MSIX como canal recomendado e ainda precisa ser compilado/instalado no gate final.

## Principais mudanças

- Nova interface reorganizada, responsiva e fora do Beta, mantendo a Clássica como opção de retorno.
- Várias tags alvo e tags de contexto por estrutura XML, com origem/contexto visíveis por linha.
- Carregamento assíncrono e indexado para XMLs grandes.
- Estados pendente, traduzindo, traduzido, confirmado e erro; diagnóstico por entrada e filtros combináveis.
- Busca por original, tradução, tag e contexto; seleção Ctrl/Shift, tradução de subconjunto e duplicatas exatas.
- Italiano, russo, dinamarquês e turco como novos idiomas de destino.
- Descoberta dinâmica de modelos Gemini, sem fixar um alias temporário.
- Versão unificada em 1.4.0 e Quick Start atualizado para `uv`.
- Verificação automática diária de releases, banner de atualização e download verificado antes de abrir o Setup.

## Compatibilidade e migração

- Presets antigos continuam aceitos e só são convertidos quando salvos explicitamente.
- Checkpoints legados continuam consultáveis; o formato atual separa tags, idioma, estados e erros.
- A escolha entre Nova e Clássica fica nas Configurações e é aplicada no próximo início.
- O fallback para a Clássica cobre falha de carregamento do shell Nova, não falhas em componentes compartilhados.

## Limitações conhecidas

- GLO-002 tem cobertura automatizada, mas o glossário protegido do DeepL ainda precisa de uma chamada real com credencial.
- API-001, histórico de desfazer, memória de tradução persistente e estatísticas detalhadas ficam para versões futuras.
- O Setup não possui assinatura de uma autoridade pública; o Windows SmartScreen pode informar editor desconhecido.
- A atualização é assistida: nunca baixa/instala silenciosamente, não interrompe tradução e exige confirmação.

## Rollback

1. Salvar o trabalho e manter uma cópia do XML antes de sobrescrever o arquivo atual.
2. Para regressão apenas visual, selecionar a interface Clássica em Configurações e reiniciar.
3. Para regressão do pacote, desinstalar 1.4.0 e reinstalar o Setup 1.3.0 preservado; validar antes em ambiente limpo que dados de configuração esperados permanecem acessíveis.

## Evidência validada

- `uv run pytest -q`: 334 testes aprovados.
- `uv run ruff check .`: aprovado.
- `uv run python -m tests.qml_parity_check`: 44 cenários aprovados, incluindo o banner nos dois shells e temas.
- Gemini real: tradução individual e lote aprovados.
- Google real: smokes de italiano, russo, dinamarquês e turco aprovados.
- Nuitka: standalone compilado; PE em `1.4.0.0` e inicialização sem saída prematura.
- Metadado do executável: `CompanyName=STZ Labs`; módulo do updater e banner QML incluídos no bundle.
- Consulta pública real ao endpoint de latest release aprovada.
- Empacotamento: Inno usa o standalone Nuitka, instalação por usuário, `AppId` estável e editor `STZ Labs`.
- Atualizador: release estável, intervalo diário, ignorar/adiar, download atômico, SHA-256 e lançamento do Setup cobertos por automação.

## Gates finais antes de publicar

- [ ] Executar GLO-002 com uma credencial DeepL temporária e conferir preservação do termo do glossário.
- [ ] Compilar `STZXMLTranslator-Setup-1.4.0.exe` com Inno Setup 6.
- [ ] Instalar em máquina/usuário limpo, abrir e executar o fluxo mínimo.
- [ ] Atualizar de 1.3.0 para 1.4.0 e confirmar preferências/checkpoint.
- [ ] Validar desinstalação e procedimento de rollback.
- [ ] Criar tag `v1.4.0`; o workflow deve rejeitar qualquer divergência de versão.
- [ ] Publicar os artefatos e estas notas somente após os gates anteriores.

Após publicar a 1.4.0, validar UPD-004 com uma release de teste superior ou em um repositório/canal controlado antes de depender do fluxo em produção.

Voltar: [[08 - Qualidade, Dados e Release]] · [[05 - Backlog]].
