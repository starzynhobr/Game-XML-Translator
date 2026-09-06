---
tipo: produto
status: ativo
atualizado: 2026-09-03
---

# Visão do Produto

## Para quem

Modders, tradutores independentes e pequenas equipes de localização que trabalham diretamente com XMLs de jogos e precisam preservar a estrutura original.

## Trabalho principal

Carregar um XML, indicar quais campos contêm texto, fornecer contexto suficiente para uma tradução correta, revisar o resultado e gerar um XML utilizável sem editar o arquivo manualmente.

## Promessa

> Traduzir conteúdo XML com contexto, controle e segurança, sem exigir que a pessoa entenda APIs ou manipule a estrutura do arquivo à mão.

## Princípios

1. **Estrutura primeiro:** nunca alterar tags, atributos, namespaces ou ordem fora do escopo escolhido.
2. **Contexto sem contaminação:** contexto ajuda a tradução, mas não vira texto traduzido por acidente.
3. **Ações em massa com controle:** permitir lote e seleção múltipla, mostrando exatamente o alcance.
4. **Retomada segura:** progresso recuperável e falhas isoladas por item.
5. **Revisão explícita:** no futuro, diferenciar tradução gerada de tradução confirmada.
6. **Interface de ferramenta:** alta densidade organizada, atalhos e foco em leitura; decoração é secundária.
7. **Compatibilidade:** evoluir presets e checkpoints sem quebrar dados de usuários existentes.

## Fluxo principal desejado

```text
Carregar XML
  → escolher bloco repetido
  → escolher tags a traduzir e de contexto
  → revisar prévia do que será extraído
  → traduzir tudo ou uma seleção
  → revisar e confirmar
  → salvar/exportar
```

## Indicadores de sucesso

- Um XML com personagem, nome e biografia pode traduzir a biografia sabendo de qual personagem se trata.
- O usuário não precisa repetir o processo para cada tag traduzível do mesmo bloco.
- Frases idênticas podem receber a mesma tradução em massa.
- O usuário consegue localizar pendências e erros sem percorrer toda a tabela.
- Nenhuma tag de contexto é modificada no XML final.

## Fora de escopo imediato

- Colaboração multiusuário e autoria por tradutor.
- Paginação da tabela virtualizada.
- Memória de tradução aproximada ou fuzzy matching.
- Tradução de atributos XML.
- Reescrita completa da arquitetura QML.

Anterior: [[00 - Plano Mestre de Implementação]] · Próximo: [[02 - Estado Atual e Evidências]].
