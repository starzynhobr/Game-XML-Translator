# Game XML Translator

Desktop tool that helps modders and localization teams translate XML dialogue files. It provides a CustomTkinter interface to preview original strings, apply machine translations, review them faster, and export an updated XML without breaking the structure of the game file.

> **Status:** maintenance mode. No new features are planned, but the existing code and build instructions remain available for reference.

## Features

- XML extractor/injector that preserves node order and attributes.
- CustomTkinter UI with dark theme, progress tracking, and quick filters.
- Multiple translation providers (via `core/tradutor_api`), including support for API keys such as Google Gemini.
- Glossary manager (`scripts/glossario.json`) to enforce project terminology.
- Multi-language interface managed by JSON files in `locales/`.
- One-click export back to XML with structural validation helpers.

## Quick Start

Requirements:

- Python 3.11 (recommended)  
- Windows 10/11 with Visual C++ Build Tools (needed only for compilation)  
- A translation provider API key (optional, but required for automated translations)

Clone the repository and set up a virtual environment:

```powershell
git clone https://github.com/StarzynhoBR/Game-XML-Translator.git
cd Game-XML-Translator
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Run the app from source:

```powershell
python main.py
```

> Tip: the interface detects available locales from `locales/*.json`. Edit or add new files to localize the UI.

## Using the App

1. Open an XML file (`Arquivo XML Original`) and, if needed, choose the parent/target tags that contain the dialogue lines.  
2. Select the language for the UI and connect a translation provider (set your API key via the settings button).  
3. Click “Extrair texto” to populate the table. You can review or edit translations manually in the right pane.  
4. Use “Traduzir Selecionado” or “Traduzir Tudo” to call the chosen translation service; adjust wording directly in the table or textbox.  
5. Export with “Salvar XML traduzido”: pick the output path and the tool will inject the translations while keeping the original structure.

> Tested primarily with Marvel Avengers Alliance Redux assets, but the workflow handles generic XML files without namespaces. For other games, confirm the target tag names match their structure.

## Building a Standalone Executable

The project ships with a build script for Nuitka:

```powershell
build_nuitka.bat
```

This script activates `.venv`, installs or updates Nuitka, bundles the assets and locales, and produces `dist/GameXMLTranslator.exe` with the project icon.

Manual build example (same flags used by the script):

```powershell
python -m nuitka ^
    --standalone --onefile ^
    --enable-plugin=tk-inter ^
    --windows-console-mode=disable ^
    --windows-icon-from-ico=assets/icon.ico ^
    --include-data-dir=locales=locales ^
    main.py
```

If you need to distribute the executable, prefer creating a GitHub Release instead of committing the `.exe` file to version control.

## Project Layout

- `main.py` - GUI entry point with translation workflow.
- `core/` - XML extraction/injection logic, translation service adapters, and i18n manager.
- `locales/` - UI translations in JSON.
- `assets/` - Static assets such as the application icon.
- `scripts/` - Glossary JSON and additional helpers.
- `build_nuitka.bat` - Automated Nuitka build script.

## Troubleshooting

- **Module not found / customtkinter**: ensure the virtual environment is activated and dependencies are installed.
- **Large executable**: this is expected for `--onefile`. Switch to `--standalone` for a folder-based build.
- **Build failures on Windows**: install the "Desktop development with C++" workload from Visual Studio Build Tools.
- **Locale not loading**: verify the JSON filename matches the locale code (e.g., `pt_BR.json`) and contains valid JSON.

## Short Summary in Portuguese

Game XML Translator e uma ferramenta desktop para traduzir arquivos XML de jogos. O projeto inclui interface em CustomTkinter, suporte a servicos de traducao automatica, glossario personalizavel e scripts para gerar um executavel standalone com Nuitka. Veja `BUILD.md` para passos detalhados de compilacao.

## Author

Created by [StarzynhoBR](https://github.com/StarzynhoBR). Se voce reutilizar alguma parte deste projeto, mantenha os creditos.

## Contributing

Bug reports and pull requests are welcome! Please open an issue first to discuss major changes. For pull requests, run the application locally to verify that locale files and glossary loading still work.

## License

See `LICENSE`. All rights reserved; contact the author for reuse permissions.
