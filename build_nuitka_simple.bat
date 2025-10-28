@echo off
REM Script simplificado para compilar com Nuitka usando Python do sistema

echo ========================================
echo  Build Simplificado com Nuitka
echo ========================================
echo.

echo Instalando Nuitka no Python do sistema...
python -m pip install --user --upgrade nuitka ordered-set zstandard

echo.
echo ========================================
echo  Compilando...
echo ========================================
echo.

REM Verifica se o ícone existe
set ICON_PARAM=
if exist "assets\icon.ico" (
    echo Icone encontrado...
    set ICON_PARAM=--windows-icon-from-ico=assets/icon.ico
)

python -m nuitka ^
    --standalone ^
    --onefile ^
    --enable-plugin=tk-inter ^
    %ICON_PARAM% ^
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
    main.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo  Compilacao concluida!
    echo ========================================
    echo.
    echo Executavel: dist\GameXMLTranslator.exe
    echo.
) else (
    echo.
    echo ========================================
    echo  ERRO!
    echo ========================================
    echo.
)

pause
