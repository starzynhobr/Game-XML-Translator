import customtkinter as ctk
from tkinter import filedialog, ttk, messagebox
import os, json, threading, time, sys, csv, re, queue
from core.tradutor_api import translate_text, AVAILABLE_SERVICES
from dotenv import load_dotenv
import google.generativeai as genai

# Importa as funções dos nossos outros scripts
from core.extrator import extrair_textos
#from core.tradutor_api import traduzir_texto_unico
from core.injetor import injetar_traducoes
from core.i18n import I18nManager

TRANSLATION_TARGETS = {
    "pt": {"code": "pt", "deepl": "PT-BR", "label": "Portuguese (Brazil)"},
    "en": {"code": "en", "deepl": "EN-US", "label": "English"},
    "es": {"code": "es", "deepl": "ES", "label": "Spanish"},
    "fr": {"code": "fr", "deepl": "FR", "label": "French"},
    "ja": {"code": "ja", "deepl": "JA", "label": "Japanese"},
}

def resource_path(relative_path):
    """Resolve paths for bundled data in script and frozen modes."""
    base_path = getattr(sys, "_MEIPASS", None)  # PyInstaller
    if base_path:
        return os.path.join(base_path, relative_path)

    if getattr(sys, "frozen", False):  # Nuitka, cx_Freeze, etc.
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)

# Define a aparência padrão do aplicativo
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- NOVO: Janela de Gerenciamento do Glossário ---
class GlossaryWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.transient(master)
        self.i18n = self.master.i18n
        self.title(self.i18n.get("glossary_window_title"))
        self.geometry("600x400")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.glossary_path = resource_path(os.path.join("scripts", "glossario.json"))
        self.glossary_data = self.load_glossary()
        self.entries = []

        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text=self.i18n.get("glossary_terms_label"))
        self.scrollable_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.rebuild_ui()

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        self.add_button = ctk.CTkButton(button_frame, text=self.i18n.get("glossary_add_button"), command=self.add_row)
        self.add_button.pack(side="left", padx=5)

        self.save_button = ctk.CTkButton(button_frame, text=self.i18n.get("glossary_save_button"), command=self.save_and_close)
        self.save_button.pack(side="right", padx=5)

    def load_glossary(self):
        if os.path.exists(self.glossary_path):
            with open(self.glossary_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def rebuild_ui(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.entries = []
        for i, (key, value) in enumerate(self.glossary_data.items()):
            self.create_row(i, key, value)

    def create_row(self, index, key, value):
        key_entry = ctk.CTkEntry(self.scrollable_frame)
        key_entry.insert(0, key)
        key_entry.grid(row=index, column=0, padx=5, pady=5, sticky="ew")
        
        value_entry = ctk.CTkEntry(self.scrollable_frame)
        value_entry.insert(0, value)
        value_entry.grid(row=index, column=1, padx=5, pady=5, sticky="ew")
        
        delete_button = ctk.CTkButton(self.scrollable_frame, text="X", width=20, fg_color="red", hover_color="darkred", command=lambda i=index: self.delete_row(i))
        delete_button.grid(row=index, column=2, padx=5, pady=5)
        
        self.entries.append((key_entry, value_entry))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=1)

    def add_row(self):
        self.create_row(len(self.entries), "", "")

    def delete_row(self, index):
        self.glossary_data.pop(list(self.glossary_data.keys())[index])
        self.rebuild_ui()

    def save_and_close(self):
        new_glossary = {}
        for key_entry, value_entry in self.entries:
            key = key_entry.get().strip()
            value = value_entry.get().strip()
            if key and value:
                new_glossary[key] = value
        
        with open(self.glossary_path, 'w', encoding='utf-8') as f:
            json.dump(new_glossary, f, indent=4, ensure_ascii=False)
        
        self.master.log(self.i18n.get("log_glossary_saved"))
        self.destroy()

    def on_close(self):
        # Poderia adicionar um aviso de "Salvar antes de fechar?" aqui
        self.destroy()

class TranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.i18n = I18nManager(language="pt_BR") # Começa em português
        self.source_language_label = "English"
        self._carregar_idiomas_disponiveis()
        nome_amigavel_inicial = [name for name, code in self.idiomas_disponiveis.items() if code == self.i18n.language][0]
        self.language_variable = ctk.StringVar(value=nome_amigavel_inicial) 
        self.translation_target = self._resolve_translation_target(self.i18n.language)
        self.api_key = self._carregar_api_key_existente()
        
        self.title("Game XML Translator v1.1")
        self.geometry("1200x700")
        self.minsize(1000, 600)  # Define tamanho mínimo da janela

        # Configura grid: colunas laterais fixas, central expansível
        self.grid_columnconfigure(0, weight=0)  # Coluna esquerda FIXA
        self.grid_columnconfigure(1, weight=1, minsize=400)  # Coluna central EXPANSÍVEL
        self.grid_columnconfigure(2, weight=0)  # Coluna direita FIXA (sem minsize)
        self.grid_rowconfigure(0, weight=1)

        self.arquivo_xml_path = ""; self.dados_traducao = {}
        self.cancel_event = threading.Event()
        self.translation_queue = queue.Queue()

        self.modelos_disponiveis = {
            "Gemini 1.5 Flash (Rápido)": ("models/gemini-1.5-flash-latest", 5),
            "Gemini 2.5 Pro (Qualidade)": ("models/gemini-2.5-pro", 31)
        }
        self.modelo_selecionado = ctk.StringVar(value=list(self.modelos_disponiveis.keys())[0])

        # Cria os três painéis principais
        self.left_sidebar_frame = ctk.CTkFrame(self, corner_radius=0, width=320)
        self.left_sidebar_frame.grid(row=0, column=0, sticky="nsw", padx=(5, 2), pady=5)
        self.left_sidebar_frame.grid_rowconfigure(14, weight=1)
        self.left_sidebar_frame.grid_propagate(False)  # Mantém largura fixa

        self.center_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.center_frame.grid(row=0, column=1, sticky="nsew", padx=2, pady=5)
        self.center_frame.grid_columnconfigure(0, weight=1)
        self.center_frame.grid_rowconfigure(0, weight=1)

        self.right_sidebar_frame = ctk.CTkFrame(self, corner_radius=0, width=330)
        self.right_sidebar_frame.grid(row=0, column=2, sticky="nsew", padx=(2, 5), pady=5)
        self.right_sidebar_frame.grid_rowconfigure(8, weight=1)
        self.right_sidebar_frame.grid_columnconfigure(0, weight=1)  # Coluna única com peso
        self.right_sidebar_frame.grid_propagate(False)  # Mantém largura fixa
        
        # PAINEL ESQUERDO
        # A linha da "mola" foi REMOVIDA. Agora todos os widgets ficarão juntos.
        
        self.project_label = ctk.CTkLabel(self.left_sidebar_frame, text=self.i18n.get("project_panel_title"), font=ctk.CTkFont(size=20, weight="bold"))
        self.project_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.load_xml_button = ctk.CTkButton(self.left_sidebar_frame, text=self.i18n.get("load_xml_button"), command=self.selecionar_arquivo_xml)
        self.load_xml_button.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.glossary_button = ctk.CTkButton(self.left_sidebar_frame, text=self.i18n.get("manage_glossary_button"), command=self.open_glossary_window)
        self.glossary_button.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.io_frame = ctk.CTkFrame(self.left_sidebar_frame)
        self.io_frame.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        self.io_frame.grid_columnconfigure((0, 1), weight=1) # 2 colunas com peso igual

        # Botões de Exportação (Primeira Linha)
        self.export_json_button = ctk.CTkButton(self.io_frame, text="Exportar JSON", command=self.exportar_json_para_traducao)
        self.export_json_button.grid(row=0, column=0, padx=(5, 2), pady=(5, 2), sticky="ew")

        self.export_csv_button = ctk.CTkButton(self.io_frame, text="Exportar CSV", command=self.exportar_para_csv)
        self.export_csv_button.grid(row=0, column=1, padx=(2, 5), pady=(5, 2), sticky="ew")

        # Botões de Importação (Segunda Linha)
        self.import_json_button = ctk.CTkButton(self.io_frame, text="Importar JSON", command=self.importar_json_traduzido)
        self.import_json_button.grid(row=1, column=0, padx=(5, 2), pady=(2, 5), sticky="ew")

        self.import_csv_button = ctk.CTkButton(self.io_frame, text="Importar CSV", command=self.importar_de_csv)
        self.import_csv_button.grid(row=1, column=1, padx=(2, 5), pady=(2, 5), sticky="ew")

        # IMPORTANTE: Ajuste o número da linha (row) dos widgets que vêm depois!
        # Por exemplo, o lang_optionmenu agora deve estar na row=4, o caminho_arquivo_entry na row=5, etc.

        self.lang_optionmenu = ctk.CTkOptionMenu(self.left_sidebar_frame, variable=self.language_variable, values=list(self.idiomas_disponiveis.keys()), command=self.change_language)
        self.lang_optionmenu.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        
        self.caminho_arquivo_entry = ctk.CTkEntry(self.left_sidebar_frame, placeholder_text=self.i18n.get("loaded_file_placeholder"))
        self.caminho_arquivo_entry.grid(row=5, column=0, padx=20, pady=(10, 10), sticky="ew")

        self.tag_alvo_label = ctk.CTkLabel(self.left_sidebar_frame, text=self.i18n.get("target_tag_label"))
        self.tag_alvo_label.grid(row=6, column=0, padx=20, pady=(10, 2))
        
        self.tag_alvo_entry = ctk.CTkEntry(self.left_sidebar_frame)
        self.tag_alvo_entry.insert(0, "bio")
        self.tag_alvo_entry.grid(row=7, column=0, padx=40, pady=(0, 20))

        self.parent_tag_label = ctk.CTkLabel(self.left_sidebar_frame, text="Tag Pai (ex: item):")
        self.parent_tag_label.grid(row=8, column=0, padx=20, pady=(10, 2))

        # O Campo de texto para a "Tag Pai"
        self.parent_tag_entry = ctk.CTkEntry(self.left_sidebar_frame)
        self.parent_tag_entry.insert(0, "baseVillain")
        self.parent_tag_entry.grid(row=9, column=0, padx=40, pady=(0, 10)) # Aumentei um pouco o pady

        self.reload_button = ctk.CTkButton(self.left_sidebar_frame, text="Recarregar", command=self.recarregar_dados_xml, state="disabled")
        self.reload_button.grid(row=10, column=0, padx=40, pady=(0, 20), sticky="ew")

        # --- SEÇÃO DE PROGRESSO (AGORA MAIS JUNTA) ---
        self.progress_label = ctk.CTkLabel(self.left_sidebar_frame, text=self.i18n.get("progress_label"))
        self.progress_label.grid(row=11, column=0, padx=20, pady=(10, 2)) # pady diminuído
        
        self.progressbar = ctk.CTkProgressBar(self.left_sidebar_frame, height=15)
        self.progressbar.grid(row=12, column=0, padx=40, pady=(0, 2)) # pady diminuído
        
        self.stats_label = ctk.CTkLabel(self.left_sidebar_frame, text=self.i18n.get("stats_template", done=0, total=0))
        self.stats_label.grid(row=13, column=0, padx=20, pady=(0, 20)) # pady diminuído
        
        # O botão de exportar agora fica na sequência, na linha 10
        self.export_button = ctk.CTkButton(self.left_sidebar_frame, text=self.i18n.get("export_button"), command=self.exportar_xml_traduzido)
        self.export_button.grid(row=15, column=0, padx=20, pady=10, sticky="ew")


        # PAINEL CENTRAL
        style = ttk.Style(); style.theme_use("default"); style.configure("Treeview", background="#2a2d2e", foreground="white", fieldbackground="#2a2d2e", borderwidth=0, rowheight=25); style.configure("Treeview.Heading", background="#565b5e", foreground="white", font=("Arial", 10, "bold")); style.map('Treeview.Heading', background=[('active', '#3484F0')])
        self.tree = ttk.Treeview(self.center_frame, columns=("Original", "Traducao"), show="headings"); self.tree.heading("Original", text=self.i18n.get("original_text_label")); self.tree.heading("Traducao", text=self.i18n.get("translation_label")); self.tree.grid(row=0, column=0, sticky="nsew"); self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.tag_configure('traduzido', background='#1E4436'); self.tree.tag_configure('traduzindo', background='#565b5e')
        scrollbar = ctk.CTkScrollbar(self.center_frame, command=self.tree.yview); scrollbar.grid(row=0, column=1, sticky='ns'); self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Mini-Terminal de Log
        self.log_textbox = ctk.CTkTextbox(self.center_frame, height=100); self.log_textbox.grid(row=1, column=0, columnspan=2, padx=0, pady=(5,0), sticky="ew"); self.log_textbox.configure(state="disabled", font=("Inter", 15))

        # PAINEL DIREITO
        self.tools_label = ctk.CTkLabel(self.right_sidebar_frame, text=self.i18n.get("tools_panel_title"), font=ctk.CTkFont(size=20, weight="bold"))
        self.tools_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Seleção de Modelo
        self.model_label = ctk.CTkLabel(self.right_sidebar_frame, text=self.i18n.get("ai_model_label"), anchor="w")
        self.model_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")

        self.model_optionmenu = ctk.CTkOptionMenu(self.right_sidebar_frame, variable=self.modelo_selecionado, values=list(self.modelos_disponiveis.keys()))
        self.model_optionmenu.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.traduzir_tudo_button = ctk.CTkButton(self.right_sidebar_frame, text="Traduzir Itens Pendentes (IA)", command=self.iniciar_traducao_em_massa_resumivel)
        self.traduzir_tudo_button.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.original_textbox = ctk.CTkTextbox(self.right_sidebar_frame, height=100)
        self.original_textbox.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.original_textbox.configure(state="disabled")

        self.traducao_textbox = ctk.CTkTextbox(self.right_sidebar_frame, height=100)
        self.traducao_textbox.grid(row=5, column=0, padx=20, pady=(0, 20), sticky="ew")

        self.sugestao_button = ctk.CTkButton(self.right_sidebar_frame, text=self.i18n.get("generate_suggestion_button"), command=self.iniciar_traducao_linha_selecionada)
        self.sugestao_button.grid(row=6, column=0, padx=20, pady=10, sticky="ew")

        self.aprovar_button = ctk.CTkButton(self.right_sidebar_frame, text=self.i18n.get("approve_button"), fg_color="green", hover_color="darkgreen", command=self.aprovar_traducao)
        self.aprovar_button.grid(row=9, column=0, padx=20, pady=10, sticky="s")
        
        self.update_ui_texts()
        self.log(self.i18n.get("log_welcome"))

    def log(self, message):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_textbox.configure(state="disabled")
        self.log_textbox.see("end")

    def _carregar_api_key_existente(self):
        """Apenas tenta carregar a chave de um arquivo config.json existente."""
        config_path = "config.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return config.get("api_key")
            except (FileNotFoundError, json.JSONDecodeError):
                return None
        return None

    def importar_de_csv(self):
        """Lê um arquivo CSV e atualiza as traduções na tabela."""
        if not self.tree.get_children():
            messagebox.showwarning("Atenção", "Carregue um arquivo XML primeiro para popular a tabela.")
            return
            
        filepath = filedialog.askopenfilename(
            title="Selecione o arquivo CSV com as traduções",
            filetypes=(("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*"))
        )
        if not filepath:
            self.log("Importação de CSV cancelada.")
            return

        try:
            itens_atualizados = 0
            with open(filepath, 'r', newline='', encoding='utf-8') as f:
                # Usamos DictReader para ler o CSV como um dicionário, usando o cabeçalho
                reader = csv.DictReader(f)
                
                for row in reader:
                    # Pega os dados das colunas 'xpath' e 'translated_text'
                    xpath = row.get('xpath')
                    nova_traducao = row.get('translated_text')

                    if xpath and nova_traducao is not None:
                        # Verifica se uma linha com aquele ID (xpath) existe na tabela
                        if self.tree.exists(xpath):
                            original_text, _ = self.tree.item(xpath, 'values')
                            # Atualiza a linha com a nova tradução
                            self.tree.item(xpath, values=(original_text, nova_traducao), tags=('traduzido',))
                            itens_atualizados += 1
            
            self.log(f"{itens_atualizados} itens foram atualizados a partir do arquivo CSV.")
            self.atualizar_estatisticas()
            
            if itens_atualizados > 0:
                messagebox.showinfo("Sucesso", f"{itens_atualizados} traduções foram importadas com sucesso do CSV!")
            else:
                messagebox.showwarning("Atenção", "Nenhuma tradução correspondente foi encontrada no arquivo CSV.")

        except Exception as e:
            messagebox.showerror("Erro de Leitura", f"Não foi possível ler ou processar o arquivo CSV.\nVerifique se o formato está correto e se possui as colunas 'xpath' e 'translated_text'.\n\nDetalhes: {e}")
            self.log(f"Falha ao importar de CSV: {e}")

    def _processar_e_carregar_xml(self):
        """Função central que lê as tags, extrai os textos e atualiza a interface."""
        tag_alvo = self.tag_alvo_entry.get().strip()
        tag_pai = self.parent_tag_entry.get().strip()

        if not tag_alvo or not tag_pai:
            messagebox.showwarning("Atenção", "Por favor, especifique uma Tag Alvo e uma Tag Pai.")
            return

        sucesso, mapa_de_dados = extrair_textos(
            arquivo_xml=self.arquivo_xml_path,
            parent_tag=tag_pai,
            target_tag=tag_alvo
        )

        for i in self.tree.get_children():
            self.tree.delete(i)

        if sucesso:
            self.dados_traducao = mapa_de_dados
            
            # --- LÓGICA CORRIGIDA AQUI ---
            # 1. Renomeamos as variáveis do loop para clareza: xpath e texto_original.
            #    O método .items() retorna (chave, valor).
            for xpath, texto_original in self.dados_traducao.items():
                # 2. Usamos 'texto_original' para a primeira coluna (Texto Original).
                # 3. Deixamos a segunda coluna (Tradução) vazia inicialmente.
                # 4. Usamos o 'xpath' como ID da linha (iid), que é um identificador único perfeito.
                self.tree.insert("", "end", iid=xpath, values=(texto_original, ""), tags=('nao_traduzido',))
            
            self.log(f"Arquivo '{os.path.basename(self.arquivo_xml_path)}' carregado com {len(self.dados_traducao)} itens.")
            self.reload_button.configure(state="normal")
        else:
            self.dados_traducao = {}
            if mapa_de_dados: # Verifica se há uma mensagem de erro para exibir
                self.log(mapa_de_dados)

        self.atualizar_estatisticas()

    def exportar_para_csv(self):
        """Exporta os dados da tabela (XPath, Original, Tradução) para um arquivo CSV."""
        if not self.tree.get_children():
            messagebox.showwarning("Atenção", "Não há dados na tabela para exportar.")
            return

        caminho_saida = filedialog.asksaveasfilename(
            title="Salvar como CSV",
            defaultextension=".csv",
            filetypes=(("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")),
            initialfile="traducoes.csv"
        )

        if not caminho_saida:
            self.log("Exportação para CSV cancelada.")
            return

        try:
            # Prepara os dados para salvar
            dados_para_salvar = []
            # Adiciona o cabeçalho das colunas
            dados_para_salvar.append(['xpath', 'original_text', 'translated_text'])

            # Itera sobre cada linha da tabela
            for xpath_id in self.tree.get_children():
                original, traducao = self.tree.item(xpath_id, 'values')
                dados_para_salvar.append([xpath_id, original, traducao])
            
            # Escreve os dados no arquivo CSV
            with open(caminho_saida, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(dados_para_salvar)
            
            messagebox.showinfo("Sucesso", f"Arquivo CSV salvo com sucesso em:\n{caminho_saida}")
            self.log(f"Dados exportados para o arquivo CSV: {os.path.basename(caminho_saida)}")

        except Exception as e:
            messagebox.showerror("Erro de Gravação", f"Não foi possível salvar o arquivo CSV.\n\nDetalhes: {e}")
            self.log(f"Falha ao exportar para CSV: {e}")

    def selecionar_arquivo_xml(self):
        """Abre o seletor de arquivos e dispara o processamento."""
        filepath = filedialog.askopenfilename(title=self.i18n.get("select_xml_file"), filetypes=(("Arquivos XML", "*.xml"), ("Todos os arquivos", "*.*")))
        if not filepath:
            return

        self.arquivo_xml_path = filepath
        filename = os.path.basename(filepath)
        self.caminho_arquivo_entry.configure(state="normal")
        self.caminho_arquivo_entry.delete(0, "end")
        self.caminho_arquivo_entry.insert(0, filename)
        self.caminho_arquivo_entry.configure(state="disabled")
        
        # Chama a função central para fazer o trabalho
        self._processar_e_carregar_xml()

    def recarregar_dados_xml(self):
        """Recarrega o arquivo XML atual usando as tags da interface."""
        if not self.arquivo_xml_path or not os.path.exists(self.arquivo_xml_path):
            self.log("Nenhum arquivo válido carregado para recarregar.")
            return
        
        self.log("Recarregando dados com as novas tags...")
        # Chama a mesma função central!
        self._processar_e_carregar_xml()

    def change_language(self, language_choice: str):
        lang_code = self.idiomas_disponiveis.get(language_choice)
        if lang_code:
            self.i18n.load_language(lang_code)
            self.translation_target = self._resolve_translation_target(lang_code)
            self.update_ui_texts()
            self.log(self.i18n.get("changed_language", lang_name=language_choice))

    def exportar_json_para_traducao(self):
        if not self.arquivo_xml_path:
            messagebox.showwarning(self.i18n.get("warn_no_xml_title"), self.i18n.get("warn_no_xml_message"))
            return

        caminho_saida = filedialog.asksaveasfilename(
            title="Salvar JSON para Tradução",
            defaultextension=".json",
            filetypes=(("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")),
            initialfile="textos_para_traduzir.json"
        )

        if not caminho_saida:
            self.log("Extração de JSON cancelada.")
            return

        tag_alvo = self.tag_alvo_entry.get().strip()
        tag_pai = self.parent_tag_entry.get().strip()

        # --- LÓGICA CORRIGIDA AQUI ---

        # 1. Chamamos a função para pegar os dados em memória (ela retorna uma tupla)
        sucesso, dados_extraidos = extrair_textos(
            arquivo_xml=self.arquivo_xml_path,
            parent_tag=tag_pai,
            target_tag=tag_alvo
        )

        # 2. Verificamos se a extração foi bem-sucedida
        if sucesso:
            try:
                # 3. Se sim, agora nós salvamos o dicionário no arquivo escolhido pelo usuário
                with open(caminho_saida, 'w', encoding='utf-8') as f:
                    json.dump(dados_extraidos, f, indent=4, ensure_ascii=False)
                
                messagebox.showinfo("Sucesso", f"Arquivo JSON extraído com sucesso para:\n{caminho_saida}")
                self.log("Arquivo JSON com textos originais foi extraído.")
            except Exception as e:
                messagebox.showerror("Erro de Gravação", f"Não foi possível salvar o arquivo JSON.\n\nDetalhes: {e}")
                self.log(f"Falha ao salvar o JSON extraído: {e}")
        else:
            # 4. Se a extração falhou, 'dados_extraidos' contém a mensagem de erro
            messagebox.showerror("Erro na Extração", f"Não foi possível extrair os textos do XML.\n\nDetalhes: {dados_extraidos}")
            self.log(f"Falha na extração de textos: {dados_extraidos}")


    def importar_json_traduzido(self):
        if not self.tree.get_children():
            messagebox.showwarning("Atenção", "Carregue um arquivo XML primeiro para popular a tabela.")
            return
            
        filepath = filedialog.askopenfilename(
            title="Selecione o arquivo JSON com as traduções",
            filetypes=(("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*"))
        )
        if not filepath:
            self.log("Importação de JSON cancelada.")
            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                mapa_traducoes = json.load(f)
        except Exception as e:
            messagebox.showerror(self.i18n.get("error_file_read_title"), self.i18n.get("error_json_read_message", details=e))
            return

        self.log(self.i18n.get("log_json_importing", count=len(mapa_traducoes), filename=os.path.basename(filepath)))
        
        itens_atualizados = 0
        
        # --- LÓGICA TOTALMENTE NOVA E CORRIGIDA ---
        # 1. Iteramos sobre o dicionário importado, pegando o xpath e a nova tradução.
        for xpath, nova_traducao in mapa_traducoes.items():
            
            # 2. Verificamos se uma linha com aquele ID (xpath) existe na nossa tabela.
            if self.tree.exists(xpath):
                # 3. Se existe, pegamos o texto original que já está lá.
                original_text, _ = self.tree.item(xpath, 'values')
                
                # 4. Atualizamos a linha usando seu ID (xpath) com a nova tradução.
                self.tree.item(xpath, values=(original_text, nova_traducao), tags=('traduzido',))
                
                itens_atualizados += 1
        
        self.log(self.i18n.get("log_items_updated", count=itens_atualizados))
        self.atualizar_estatisticas() # Atualiza a barra de progresso
        
        if itens_atualizados > 0:
            messagebox.showinfo(self.i18n.get("info_success_title"), self.i18n.get("info_translations_imported", count=itens_atualizados))
        else:
            messagebox.showwarning(self.i18n.get("warn_no_xml_title"), self.i18n.get("warn_no_matches_found"))

    def _carregar_idiomas_disponiveis(self):
        self.idiomas_disponiveis = {}
        locales_path = resource_path("locales")
        if not os.path.exists(locales_path): return

        for filename in os.listdir(locales_path):
            if filename.endswith(".json"):
                lang_code = filename.replace(".json", "")
                try:
                    with open(os.path.join(locales_path, filename), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        lang_name = data.get("_language_name", lang_code) # Usa o nome amigável ou o código do arquivo
                        self.idiomas_disponiveis[lang_name] = lang_code
                except Exception as e:
                    print(f"Erro ao carregar o idioma {filename}: {e}")

    def _resolve_translation_target(self, locale_code):
        """Map UI locale to translation target metadata."""
        base = (locale_code or "").split("_")[0].lower()
        meta = TRANSLATION_TARGETS.get(base)
        if meta:
            return dict(meta)
        fallback = base or "en"
        return {"code": fallback, "deepl": fallback.upper(), "label": fallback.title()}

    def update_ui_texts(self):
        """
        Esta função é o "coração" da troca de idioma. Ela passa por todos
        os widgets e atualiza seus textos com base no novo idioma carregado.
        """
        # --- Título da Janela ---
        self.title(self.i18n.get("window_title"))
        
        # --- Painel Esquerdo ---
        self.project_label.configure(text=self.i18n.get("project_panel_title"))
        self.load_xml_button.configure(text=self.i18n.get("load_xml_button"))
        self.glossary_button.configure(text=self.i18n.get("manage_glossary_button"))
        
        # Botões de I/O
        self.import_json_button.configure(text=self.i18n.get("import_json_button"))
        self.import_csv_button.configure(text=self.i18n.get("import_csv_button"))
        self.export_json_button.configure(text=self.i18n.get("export_json_button"))
        self.export_csv_button.configure(text=self.i18n.get("export_csv_button"))
        
        self.caminho_arquivo_entry.configure(placeholder_text=self.i18n.get("loaded_file_placeholder"))
        self.tag_alvo_label.configure(text=self.i18n.get("target_tag_label"))
        self.parent_tag_label.configure(text=self.i18n.get("parent_tag_label"))
        self.reload_button.configure(text=self.i18n.get("reload_button"))
        self.progress_label.configure(text=self.i18n.get("progress_label"))
        self.export_button.configure(text=self.i18n.get("export_button"))
        
        # --- Painel Central ---
        self.tree.heading("Original", text=self.i18n.get("original_text_label"))
        self.tree.heading("Traducao", text=self.i18n.get("translation_label"))
        
        # --- Painel Direito ---
        self.tools_label.configure(text=self.i18n.get("tools_panel_title"))
        self.model_label.configure(text=self.i18n.get("ai_model_label"))
        
        # Lógica para não sobrescrever o botão se ele estiver em modo "Cancelar" ou "Traduzindo"
        current_button_text = self.traduzir_tudo_button.cget("text")
        cancel_texts = [self.i18n.get("cancel_button"), self.i18n.get("cancelling_button"), self.i18n.get("translating_button")]
        if current_button_text not in cancel_texts:
            self.traduzir_tudo_button.configure(text=self.i18n.get("translate_all_button"))
            
        self.sugestao_button.configure(text=self.i18n.get("generate_suggestion_button"))
        self.aprovar_button.configure(text=self.i18n.get("approve_button"))
        
        # Atualiza o texto do contador (ex: "Traduzidos: 0 / 95")
        self.atualizar_estatisticas()

    def on_tree_select(self, event):
        if not self.tree.selection(): return
        selected_item_id = self.tree.selection()[0]
        values = self.tree.item(selected_item_id, 'values'); original_text = values[0]; translation_text = values[1]
        self.original_textbox.configure(state="normal"); self.original_textbox.delete("1.0", "end"); self.original_textbox.insert("1.0", original_text); self.original_textbox.configure(state="disabled")
        self.traducao_textbox.delete("1.0", "end"); self.traducao_textbox.insert("1.0", translation_text)

    def iniciar_traducao_linha_selecionada(self):
        # --- GUARDIÃO DA API ---
        if not self._ensure_api_key():
            return # Para a execução se não houver chave

        if not self.tree.selection(): 
            self.log(self.i18n.get("log_no_selection"))
            return
        threading.Thread(target=self._worker_traduzir_linha, daemon=True).start()

    def _worker_traduzir_linha(self):
        selected_item_id = self.tree.selection()[0]
        original_text = self.tree.item(selected_item_id, 'values')[0]
        
        self.after(0, lambda: self.tree.item(selected_item_id, tags=('traduzindo',)))
        
        modelo_escolhido, _ = self.modelos_disponiveis[self.modelo_selecionado.get()]
        meta = self.translation_target or {"code": "pt", "deepl": "PT-BR", "label": "Portuguese (Brazil)"}
        config = {
            "api_key": self.api_key,
            "model": modelo_escolhido,
            "target_lang": meta.get("code", "pt"),
            "target_label": meta.get("label", "Portuguese (Brazil)"),
            "deepl_lang": meta.get("deepl", "PT-BR"),
            "source_label": self.source_language_label,
        }
        traducao_sugerida = translate_text("Gemini", original_text, config)
        
        self.after(0, lambda: self._update_ui_com_traducao(selected_item_id, traducao_sugerida))
        self.after(0, lambda: self.aprovar_traducao(id_item=selected_item_id, salvar_texto=False))

    def iniciar_traducao_em_massa_resumivel(self):
        """Inicia ou cancela a thread de tradução em massa."""
        
        # Se o texto do botão for "Cancelar", significa que queremos parar o processo
        if self.traduzir_tudo_button.cget("text") == "Cancelar":
            self.log("Solicitando cancelamento do processo de tradução...")
            self.cancel_event.set() # Levanta a "bandeira" de cancelamento
            self.traduzir_tudo_button.configure(state="disabled", text="Cancelando...")
            return

        # Se não, iniciamos o processo normalmente
        if not self._ensure_api_key():
            return
            
        self.cancel_event.clear() # Garante que a "bandeira" de cancelamento esteja abaixada
        
        # Muda o botão para o modo "Cancelar"
        self.traduzir_tudo_button.configure(state="normal", text="Cancelar", fg_color="red", hover_color="darkred")
        
        # Inicia a thread "operária"
        thread = threading.Thread(target=self._worker_traducao_resumivel, daemon=True)
        thread.start()
        
        # Inicia o processador da fila para atualizar a interface
        self.processar_fila_de_traducao()

    def _worker_traducao_resumivel(self):
        """Esta é a nossa função 'operária'. Ela roda em segundo plano, é resumível e pode ser cancelada."""
        
        ARQUIVO_SAIDA = "textos_traduzidos_checkpoint.json"
        TAMANHO_DO_LOTE = 120

        # Carrega o progresso anterior, se houver
        dados_traduzidos = {}
        if os.path.exists(ARQUIVO_SAIDA):
            with open(ARQUIVO_SAIDA, 'r', encoding='utf-8') as f:
                try: 
                    dados_traduzidos = json.load(f)
                except json.JSONDecodeError: 
                    pass # Ignora o arquivo se estiver corrompido e começa do zero
        
        # Pega todos os xpaths da tabela e filtra os que já foram traduzidos
        todos_xpaths = self.tree.get_children()
        xpaths_pendentes = [xpath for xpath in todos_xpaths if xpath not in dados_traduzidos]
        
        if not xpaths_pendentes:
            self.log("Todos os itens já parecem estar traduzidos no arquivo de checkpoint.")
            self.traduzir_tudo_button.configure(state="normal", text="Traduzir Itens Pendentes (IA)")
            self.translation_queue.put(("DONE", "DONE")) # Avisa a UI para resetar o botão
            return

        lista_de_itens_pendentes = [(xpath, self.tree.item(xpath, 'values')[0]) for xpath in xpaths_pendentes]
        total_pendentes = len(lista_de_itens_pendentes)
        
        self.log(self.i18n.get("log_batch_complete", count=total_pendentes))

        for i in range(0, total_pendentes, TAMANHO_DO_LOTE):
            
            # Antes de processar o lote, verifica se o cancelamento foi solicitado
            if self.cancel_event.is_set():
                self.log(self.i18n.get("log_mass_translation_cancelled"))
                self.translation_queue.put(("DONE", "DONE")) # Avisa a UI que terminamos
                return

            lote_atual = lista_de_itens_pendentes[i:i + TAMANHO_DO_LOTE]
            texto_para_prompt = ""
            xpaths_enviados_neste_lote = []
            for xpath, texto in lote_atual:
                texto_para_prompt += f"[ID: {xpath}]\n{texto}\n---\n"
                xpaths_enviados_neste_lote.append(xpath)
            
            resposta_do_lote = self._traduzir_lote_api(texto_para_prompt)
            
            if resposta_do_lote:
                traducoes_encontradas = re.findall(r'\[ID: (.*?)\]\n(.*?)\n---', resposta_do_lote, re.DOTALL)
                
                xpaths_recebidos_neste_lote = []
                for xpath, texto_traduzido in traducoes_encontradas:
                    xpath_limpo = xpath.strip()
                    dados_traduzidos[xpath_limpo] = texto_traduzido.strip()
                    self.translation_queue.put((xpath_limpo, texto_traduzido.strip()))
                    xpaths_recebidos_neste_lote.append(xpath_limpo)
                
                # Lógica para detectar e avisar sobre itens pulados
                xpaths_pulados = set(xpaths_enviados_neste_lote) - set(xpaths_recebidos_neste_lote)
                if xpaths_pulados:
                    self.log(f"AVISO: {len(xpaths_pulados)} item(ns) foram pulados pela IA neste lote.")

                # CHECKPOINT: Salva o progresso total
                with open(ARQUIVO_SAIDA, 'w', encoding='utf-8') as f:
                    json.dump(dados_traduzidos, f, indent=4, ensure_ascii=False)
                self.log(self.i18n.get("log_batch_complete", count=len(dados_traduzidos)))
            else:
                self.log(self.i18n.get("log_batch_fail"))
                break # Interrompe o processo se houver uma falha na API

            time.sleep(5)
            
        self.log(self.i18n.get("log_mass_translation_done"))
        # Sinaliza para a interface que o trabalho acabou
        self.translation_queue.put(("DONE", "DONE"))

    def _traduzir_lote_api(self, lote_de_texto):
        """Funcao auxiliar que efetivamente chama a API Gemini."""
        try:
            genai.configure(api_key=self.api_key)
            modelo_nome, _ = self.modelos_disponiveis.get(
                self.modelo_selecionado.get(),
                ("models/gemini-1.5-flash-latest", 0),
            )
            model = genai.GenerativeModel(model_name=modelo_nome)
            meta = self.translation_target or {"label": "Portuguese (Brazil)"}
            target_label = meta.get("label", "Portuguese (Brazil)")
            prompt = (
                "Act as a game localization specialist.\n"
                "Each entry below is formatted as [ID: ...] followed by text.\n"
                f"Translate every entry to {target_label}. Keep the IDs and separators exactly as provided.\n\n"
                "---BEGIN BLOCK---\n"
                f"{lote_de_texto}\n"
                "---END BLOCK---\n"
            )
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            self.log(f"ERRO na API: {e}")
            return None

    def processar_fila_de_traducao(self):
        """Verifica a fila de traduções e atualiza a interface gráfica."""
        try:
            # Pega um item da fila sem bloquear
            xpath, traducao = self.translation_queue.get_nowait()
            
            if xpath == "DONE":
                # O trabalho acabou, reabilita o botão
                self.traduzir_tudo_button.configure(state="normal", text=self.i18n.get("translate_all_button"))
                return

            # Atualiza a tabela
            if self.tree.exists(xpath):
                original_text, _ = self.tree.item(xpath, 'values')
                self.tree.item(xpath, values=(original_text, traducao), tags=('traduzido',))
                self.atualizar_estatisticas()
            
            # Chama a si mesma novamente para continuar processando a fila
            self.after(100, self.processar_fila_de_traducao)

        except queue.Empty:
            # A fila está vazia, mas a thread ainda pode estar trabalhando.
            # Continua checando a cada 100ms.
            self.after(100, self.processar_fila_de_traducao)

    def aprovar_traducao(self, id_item=None, salvar_texto=True):
        selected_item_id = id_item if id_item else (self.tree.selection()[0] if self.tree.selection() else None)
        if not selected_item_id: return
        
        tags_atuais = self.tree.item(selected_item_id, 'tags')
        original_text, traducao_antiga = self.tree.item(selected_item_id, 'values')
        
        nova_traducao = traducao_antiga
        if salvar_texto:
            nova_traducao = self.traducao_textbox.get("1.0", "end-1c").strip()
        
        # Atualiza a tabela com o novo valor e a nova tag
        self.tree.item(selected_item_id, values=(original_text, nova_traducao), tags=('traduzido',))
        
        # Só atualiza as estatísticas se o item era 'nao_traduzido' antes.
        # Isso evita contar o mesmo item duas vezes.
        if 'nao_traduzido' in tags_atuais:
            self.atualizar_estatisticas()
        
    def _update_textbox_com_feedback(self, item_id, texto):
        if self.tree.selection() and self.tree.selection()[0] == item_id:
            self.traducao_textbox.delete("1.0", "end")
            self.traducao_textbox.insert("1.0", texto)

    def _update_ui_com_traducao(self, item_id, traducao_sugerida):
        original_text = self.tree.item(item_id, 'values')[0]
        self.tree.item(item_id, values=(original_text, traducao_sugerida))
        if self.tree.selection() and self.tree.selection()[0] == item_id:
            self.traducao_textbox.delete("1.0", "end"); self.traducao_textbox.insert("1.0", traducao_sugerida)
    
    def atualizar_estatisticas(self):
        # Lógica 100% baseada na contagem de tags, muito mais confiável.
        total_itens = len(self.tree.get_children())
        itens_traduzidos = len(self.tree.tag_has('traduzido'))
        
        self.stats_label.configure(text=self.i18n.get("stats_template", done=itens_traduzidos, total=total_itens))
        progresso = itens_traduzidos / total_itens if total_itens > 0 else 0
        self.progressbar.set(progresso)


    def _ensure_api_key(self):
        """Verifica se a chave API existe. Se não, pede ao usuário. Retorna True se a chave estiver disponível."""
        if self.api_key:
            return True

        # Se não houver chave, agora sim pedimos ao usuário
        dialog = ctk.CTkInputDialog(text=self.i18n.get("api_gemini_key"), title=self.i18n.get("api_key_config"))
        key = dialog.get_input()

        if key:
            self.api_key = key
            # Salva a chave para futuras sessões
            with open("config.json", 'w') as f:
                json.dump({"api_key": key}, f)
            self.log("Chave de API configurada com sucesso.")
            return True
        else:
            self.log(self.i18n.get("log_api_key_needed")) # Você precisará adicionar essa string no seu i18n
            return False

    def exportar_xml_traduzido(self):
        if not self.arquivo_xml_path:
            messagebox.showwarning(self.i18n.get("warn_no_xml_title"), self.i18n.get("warn_no_xml_message"))
            return

        # Pega a tag alvo da interface (não é mais necessária para a injeção, mas mantemos por consistência)
        tag_alvo = self.tag_alvo_entry.get().strip()
        if not tag_alvo:
            messagebox.showwarning(self.i18n.get("warn_tags_title"), self.i18n.get("warn_tags_message"))
            return

        # --- LÓGICA CORRIGIDA AQUI ---

        # FIX 1: Montando o dicionário da forma correta (XPath -> Tradução)
        mapa_final_traducoes = {}
        for xpath_id in self.tree.get_children():
            # O ID de cada linha (child_id) É o próprio XPath
            _original, traducao = self.tree.item(xpath_id, 'values')
            
            # Só adicionamos ao mapa se houver uma tradução
            if traducao.strip():
                mapa_final_traducoes[xpath_id] = traducao
        
        if not mapa_final_traducoes:
            messagebox.showwarning(self.i18n.get("warn_no_xml_title"), self.i18n.get("warn_no_translations_to_export"))
            return

        caminho_saida = filedialog.asksaveasfilename(
            title=self.i18n.get("save_as"),
            defaultextension=".xml",
            filetypes=(("Arquivos XML", "*.xml"), ("Todos os arquivos", "*.*")),
            initialfile=f"{os.path.basename(self.arquivo_xml_path).replace('.xml', '')}_traduzido.xml"
        )

        if not caminho_saida:
            self.log(self.i18n.get("export_cancelled"))
            return
            
        # FIX 2: Chamando a função injetar_traducoes com os parâmetros corretos
        sucesso = injetar_traducoes(
            arquivo_xml_original=self.arquivo_xml_path,
            mapa_traducoes=mapa_final_traducoes,
            arquivo_xml_final=caminho_saida
        )

        if sucesso:
            messagebox.showinfo("Sucesso", f"Arquivo XML traduzido salvo com sucesso em:\n{caminho_saida}")
            self.log("Exportação bem-sucedida.")
        else:
            messagebox.showerror("Erro", self.i18n.get("export_fail"))
            self.log("Falha na exportação.")

    def open_glossary_window(self):
        if hasattr(self, 'glossary_win') and self.glossary_win.winfo_exists():
            self.glossary_win.focus()
        else:
            self.glossary_win = GlossaryWindow(self)

# --- Ponto de Entrada da Aplicação ---
if __name__ == "__main__":
    app = TranslatorApp()
    app.mainloop()
