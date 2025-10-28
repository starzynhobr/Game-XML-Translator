# Guia de Compilação

Este guia explica como compilar o **Game XML Translator** em um executável standalone.

## Pré-requisitos

1. **Python 3.8+** instalado
2. **Visual Studio Build Tools** (para Nuitka no Windows)
   - Baixe em: https://visualstudio.microsoft.com/downloads/
   - Instale "Desktop development with C++"

3. **Ambiente virtual** configurado:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Compilação com Nuitka (Recomendado)

### Método 1: Script Automático

Execute o script de build:
```bash
build_nuitka.bat
```

Este script:
- Ativa o ambiente virtual automaticamente
- Instala/atualiza o Nuitka
- Compila o aplicativo com todas as otimizações
- Gera o executável em `dist/GameXMLTranslator.exe`

### Método 2: Manual

```bash
python -m nuitka --standalone --onefile --enable-plugin=tk-inter --windows-icon-from-ico=assets/icon.ico --windows-console-mode=disable --include-data-dir=locales=locales --include-data-dir=assets=assets --output-filename=GameXMLTranslator.exe --output-dir=dist main.py
```

## Solução de Problemas

### Erro: "DLL load failed"

**Causa**: Python DLLs não foram incluídas corretamente.

**Solução**: Use o modo `--standalone` que já está configurado no script de build. Isso embute todas as DLLs necessárias.

### Erro: "Module not found"

**Causa**: Dependências não foram detectadas.

**Solução**:
1. Certifique-se de que todas as dependências estão instaladas: `pip install -r requirements.txt`
2. O Nuitka detecta automaticamente a maioria dos imports
3. Se necessário, adicione manualmente com `--include-module=nome_modulo`

### Erro: "Visual Studio Build Tools not found"

**Solução**: Instale o Visual Studio Build Tools com o workload "Desktop development with C++".

### Executável muito grande

**Causa**: O modo `--onefile` embute tudo em um único executável.

**Alternativa**: Use apenas `--standalone` (sem `--onefile`) para gerar uma pasta com o executável + DLLs. Será menor mas terá múltiplos arquivos.

## Tamanho do Executável

- **Onefile**: ~80-120 MB (tudo em um arquivo)
- **Standalone**: ~60-90 MB distribuído em vários arquivos

## Distribuição

Após a compilação, distribua apenas o arquivo `dist/GameXMLTranslator.exe`.

**Não é necessário** distribuir:
- Python
- Ambiente virtual
- Código fonte
- DLLs extras

O executável é completamente standalone!

## Notas Importantes

1. ⚠️ **Não commite o executável** no repositório Git (.gitignore já está configurado)
2. ✅ O executável funciona em qualquer Windows 10/11 sem Python instalado
3. ✅ Antivírus podem dar falso positivo - é normal para executáveis compilados
4. ⚠️ O primeiro build pode demorar 5-15 minutos (builds seguintes são mais rápidos)
