---
tipo: qualidade
status: ativo
atualizado: 2026-09-06
---

# Qualidade, Dados e Release

## Estratégia de testes

### Unidade

- Extração de uma e várias tags alvo.
- Contexto restrito à ocorrência correta da tag pai.
- Tags ausentes, vazias, repetidas e aninhadas.
- XPath único e estável.
- Validação de sobreposição alvo/contexto.
- Migração de presets e checkpoints.
- Construção de prompts e adaptação por provedor.
- Propagação somente para duplicatas exatas.
- Transições válidas da futura máquina de estados.

### Integração

- Carregar → traduzir → checkpoint → reabrir → exportar.
- Selecionar várias tags → traduzir subconjunto → aplicar duplicatas.
- Glossário + contexto na mesma tradução.
- Importar JSON/CSV no projeto multi-tag.
- Cancelar lote e retomar sem perder estados.

### Segurança do XML

Para cada fixture, comparar entrada e saída:

- mesmos elementos e mesma ordem;
- mesmos atributos e namespaces;
- valores de contexto inalterados;
- apenas XPaths alvo traduzidos foram modificados;
- XML final continua válido;
- encoding e declaração XML tratados conscientemente.

## Matriz mínima dos provedores

| Provedor | Lote | Glossário | Contexto separado | Teste sem credencial | Teste real antes da release |
|---|---:|---:|---:|---:|---:|
| Google Translate gratuito | Sim | A confirmar | Não implementado com segurança | Mock | Sim |
| Gemini | Sim | Sim | Prompt delimitado por entrada | Mock | Sim |
| DeepL | Sim | Sim | Parâmetro `context` do SDK | Mock | Sim |
| Azure | Sim | A confirmar | Não implementado com segurança | Mock | Sim |
| Ollama | Sim | Sim | JSON estruturado por entrada | Fake local | Sim |

Não marcar uma capacidade como confirmada apenas porque a assinatura da biblioteca a aceita; registrar uma chamada real ou documentação oficial correspondente.

## Comandos de validação local

Após `uv venv`, o fluxo recomendado é:

```powershell
uv pip install -e ".[dev]"
uv run pytest
uv run ruff check .
uv run python main_qt.py
```

Se o ambiente já estiver sincronizado, normalmente basta:

```powershell
uv run python main_qt.py
```

## QA visual e de interação

- Instanciar a janela QML sem erros.
- Testar redimensionamento, DPI e textos localizados.
- Verificar teclado, Ctrl/Shift, foco e scroll.
- Conferir empty, loading, success, error e disabled.
- Comparar captura renderizada com [[07 - Design e Interface]], não apenas ler o QML.

## Dados e migração

- Nunca reescrever preset antigo durante leitura.
- Criar cópia de segurança antes de uma migração destrutiva futura.
- Checkpoint novo deve poder consultar legado de forma controlada.
- Importadores devem ignorar XPaths ausentes e reportar contagem.
- Não persistir chaves de API em vault, testes, logs ou fixtures.

## Gate de release

- [ ] Backlog da versão sem P0 aberto: somente GLO-002 aguarda smoke real DeepL; automação aprovada.
- [x] `pytest` completo aprovado.
- [x] Ruff aprovado.
- [x] QML iniciado e fluxos críticos testados manualmente.
- [ ] Smoke test real dos provedores declarados como suportados: Gemini e Google aprovados; DeepL ainda pendente neste corte.
- [x] Exportação validada em cópia, nunca no único XML do teste.
- [ ] Versão consistente no app, metadados, Setup, nome do asset, tag e release: código/contrato aprovados em 1.4.0; Setup, tag e release ainda não publicados.
- [x] Build Nuitka usa flags estáticas em `main_qt.py`.
- [ ] Build Inno Setup recebe `1.4.0`, editor `STZ Labs` e preserva o `AppId`: contrato testado; compilação local pendente por ausência do Inno Setup.
- [x] Workflow publica Setup, ZIP portátil e SHA-256 sem exigir certificado próprio.
- [x] Atualizador exige asset exato e digest SHA-256 antes de abrir o Setup.
- [x] Notas de release incluem migrações, limitações e rollback: [[16 - Release 1.4.0]].

### Corte mínimo para a próxima produção

1. ~~Fechar UIR-006, BULK-001/002, DUP-001 e GLO-001.~~
2. ~~Implementar e testar italiano, russo, dinamarquês e turco.~~
3. ~~Unificar a versão em 1.4.0 a partir de `APP_VERSION`.~~
4. ~~Revisar textos/locales e atualizar o Quick Start.~~
5. Concluir o smoke real do glossário DeepL (GLO-002).
6. Gerar o Setup, instalar em ambiente limpo, testar atualização desde 1.3.0 e rollback; então criar a tag e publicar.

### Evidência do candidato 1.4.0

- Nuitka: build standalone concluído; `FileVersion` e `ProductVersion` em `1.4.0.0`.
- O MSIX assinado foi validado antes da decisão DEC-018, mas foi substituído como canal de distribuição por exigir certificado e PowerShell do usuário.
- Contrato atual: `STZXMLTranslator-Setup-1.4.0.exe` como principal e `STZXMLTranslator-Portable-1.4.0.zip` como alternativa.
- Atualizador: comparação SemVer, consulta diária, seleção exata do asset, download atômico, SHA-256, ignorar/adiar e lançamento do Setup cobertos por testes.
- QA renderizado inclui o banner em Clássica/Nova, temas claro/escuro e 1024/1600 px.

API-001 melhora a comunicação de capacidades e incompatibilidades dos provedores, mas pode entrar nas notas da release caso não seja implementado neste corte. UX-001, TM-001, LANG-005 e STAT-001 são evoluções P2 e não bloqueiam produção.

## Rollback

- Preservar compatibilidade de leitura com presets antigos.
- Não remover suporte ao campo singular até uma release de migração estar validada.
- Para dados do usuário, preferir migração aditiva e reversível.
- Antes de salvar no XML atual, manter o fluxo de confirmação e recomendar backup.

Anterior: [[07 - Design e Interface]] · Próximo: [[09 - Diário de Implementação]].
