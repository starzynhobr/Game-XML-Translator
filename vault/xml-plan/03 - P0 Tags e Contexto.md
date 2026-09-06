---
tipo: especificacao
prioridade: P0
status: pronto-para-implementacao
atualizado: 2026-09-04
---

# P0 — Tags de Tradução e Contexto

## Problema

Hoje só uma tag alvo pode ser carregada. Em XMLs nos quais um mesmo registro contém `dispName`, `bio`, `description` e outros campos, isso remove contexto e obriga o usuário a repetir o trabalho.

## Resultado desejado

Para uma tag pai, permitir:

- selecionar **uma ou mais tags a traduzir**;
- selecionar **zero ou mais tags de contexto**;
- visualizar quantas linhas serão criadas antes de recarregar;
- identificar na tabela de qual tag veio cada linha;
- enviar contexto junto à tradução sem editar essas tags;
- salvar a configuração em presets.

## Modelo proposto

### Seleção de estrutura

```text
parent_tag: baseVillain
target_tags: [bio, description]
context_tags: [dispName, archetype]
```

### Entrada extraída

```text
xpath: /root/baseVillain[4]/bio[1]
container_xpath: /root/baseVillain[4]
source_tag: bio
original: An extraordinarily gifted technician...
context:
  dispName: WHIPLASH
  archetype: Villain
```

Cada tag alvo continua sendo uma linha independente. Isso preserva edição, status, checkpoint e injeção por XPath.

## Regras funcionais

1. Deve existir ao menos uma tag alvo.
2. Uma mesma tag não pode ser alvo e contexto ao mesmo tempo no mesmo preset.
3. Contexto é coletado somente dentro da ocorrência da tag pai correspondente.
4. Tag de contexto ausente não impede a extração.
5. Valores vazios não são enviados como contexto.
6. O nome da tag alvo acompanha o texto para os provedores de IA.
7. O XML final modifica apenas XPaths de tags alvo com tradução não vazia.
8. A tabela mostra a tag de origem da linha, ao menos como coluna compacta ou metadado visível.
9. Antes de recarregar, a interface mostra uma prévia: registros encontrados, linhas traduzíveis e campos de contexto.
10. Provedor incapaz de receber contexto separadamente traduz sem contexto e informa essa limitação; nunca concatenar contexto de modo que possa voltar no resultado.

## Estratégia por camada

### Extrator

- Introduzir um registro tipado de extração em vez de retornar apenas `{xpath: texto}`.
- Receber `target_tags: list[str]` e `context_tags: list[str]`.
- Iterar cada ocorrência do elemento pai uma única vez.
- Montar o contexto daquela ocorrência e gerar uma entrada para cada alvo preenchido.
- Preservar uma função de compatibilidade para chamadas com uma única `target_tag` durante a migração.
- Tratar namespaces de forma explícita antes de declarar a entrega concluída.

### Domínio

- Trocar `target_tag` por `target_tags` e adicionar `context_tags`.
- Acrescentar `source_tag`, `container_xpath` e `context` a `TranslationEntry`.
- Manter XPath como identidade da tradução.
- Centralizar a validação de sobreposição entre alvo e contexto.

### Presets

Novo formato:

```json
{
  "label": "Vilões",
  "parent_tag": "baseVillain",
  "target_tags": ["bio", "description"],
  "context_tags": ["dispName"]
}
```

Migração:

- ao ler um preset antigo, converter `target_tag: "bio"` em `target_tags: ["bio"]`;
- assumir `context_tags: []`;
- salvar novamente apenas no novo formato após edição explícita;
- não apagar nem reescrever automaticamente o arquivo do usuário no carregamento.

### Checkpoints

- Incluir uma assinatura estável de `parent_tag + target_tags + context_tags` na identidade do checkpoint.
- Ordenar as listas antes de calcular a assinatura.
- Procurar checkpoint legado apenas quando o novo não existir.
- Aplicar dados apenas a XPaths presentes na seleção atual.

### Provedores

- Evoluir o contrato interno para aceitar `context: dict[str, str] | None`.
- Gemini e Ollama: contexto em seção claramente delimitada do prompt e saída contendo somente a tradução.
- DeepL: usar o campo de contexto separado do SDK quando disponível.
- Google gratuito e Azure: confirmar suporte seguro; caso não exista, ignorar contexto com aviso único por execução.
- Glossário e contexto são recursos independentes e devem funcionar juntos.

### Interface

- Manter `Tag Pai` como seleção única.
- Substituir `Tag Alvo` por seletor multi-tag com chips.
- Adicionar seletor multi-tag separado para contexto.
- Chips precisam de remoção clara, foco de teclado e estado vazio legível.
- Exibir resumo como `2 tags → 436 linhas · 1 campo de contexto`.
- Mostrar contexto do item no painel direito, somente leitura.

## Fases internas

- [x] TAG-001 — modelo tipado e contrato do extrator.
- [x] TAG-002 — extração multi-alvo com contexto local ao pai.
- [x] TAG-003 — domínio e carregamento do projeto.
- [x] TAG-004 — presets novos e migração legada.
- [x] TAG-005 — identidade e migração de checkpoints.
- [x] TAG-006 — contrato de contexto nos provedores.
- [x] TAG-007 — seletor QML por chips e prévia.
- [x] TAG-008 — tabela e painel de contexto.
- [x] TAG-009 — testes, QA visual e fixture real.

## Critérios de aceite

- [x] Selecionar `bio` e `description` cria linhas das duas tags em uma única carga.
- [x] Selecionar `dispName` como contexto melhora o prompt sem alterar esse nó.
- [x] Tags repetidas em pais diferentes recebem apenas o contexto do próprio pai.
- [x] A seleção continua funcionando após salvar e reabrir um preset.
- [x] Um preset antigo abre com a mesma tag alvo de antes.
- [x] Cancelar e retomar não mistura checkpoints de configurações diferentes.
- [x] Exportar e salvar no arquivo atual preservam tags de contexto byte-a-byte quando o serializador permitir; no mínimo, preservam seu valor e estrutura semântica.
- [x] A interface funciona em largura estreita, regular e ampla, sem perder acesso aos campos.
- [x] Testes automatizados, lint e inicialização QML passam.

## Decisões ainda abertas

- Limite de caracteres de contexto por entrada e forma de indicar truncamento.
- Tratamento de contexto aninhado e de múltiplas ocorrências da mesma tag.
- Estratégia definitiva de namespaces.
- Se a coluna `Tag` fica sempre visível ou pode ser ocultada.

Relacionados: [[05 - Backlog#P0 — Dor principal]] · [[06 - Decisões]] · [[07 - Design e Interface]].

Anterior: [[02 - Estado Atual e Evidências]] · Próximo: [[04 - Roadmap]].
