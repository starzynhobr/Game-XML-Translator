@echo off
REM Script para compilar o aplicativo com Nuitka
REM Resolve problemas de DLL do Python

echo ========================================
echo  Compilando com Nuitka
echo ========================================
echo.

REM Ativa o ambiente virtual se existir
if exist ".venv\Scripts\activate.bat" (
    echo Ativando ambiente virtual...
    call .venv\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    echo Ativando ambiente virtual...
    call venv\Scripts\activate.bat
)

echo.
echo Instalando/Atualizando Nuitka...
pip install --upgrade nuitka ordered-set zstandard

echo.
echo ========================================
echo  Iniciando compilacao...
echo ========================================
echo.

python -m nuitka ^
    --standalone ^
    --onefile ^
    --enable-plugin=tk-inter ^
    --windows-icon-from-ico=assets/icon.ico ^
    --windows-console-mode=disable ^
    --include-data-dir=locales=locales ^
    --include-data-dir=assets=assets ^
    --nofollow-import-to=tkinter.test ^
    --nofollow-import-to=test ^
    --assume-yes-for-downloads ^
    --output-filename=GameXMLTranslator.exe ^
    --output-dir=dist ^
    --company-name="Game XML Translator" ^
    --product-name="Game XML Translator" ^
    --file-version=1.2.0.0 ^
    --product-version=1.2.0.0 ^
    --file-description="Tradutor de arquivos XML de jogos" ^
    --windows-uac-admin=no ^
    main.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo  Compilacao concluida com sucesso!
    echo ========================================
    echo.
    echo O executavel foi gerado em: dist\GameXMLTranslator.exe
    echo.
    pause
) else (
    echo.
    echo ========================================
    echo  ERRO na compilacao!
    echo ========================================
    echo.
    pause
)
