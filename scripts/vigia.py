import time
import os
import shutil
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

# Importa nossas funções "mão na massa"
from extrator import extrair_textos
from tradutor_api import traduzir_arquivo_json
from injetor import injetar_traducoes

# --- CONFIGURAÇÃO INICIAL ---

# Carrega a API Key do arquivo .env
load_dotenv(dotenv_path='./.env')
API_KEY = os.getenv("GOOGLE_API_KEY")

# Configuração dos caminhos (baseado na raiz do projeto)
base_path = '.'
paths = {
    "originais": os.path.join(base_path, "01_ORIGINAIS"),
    "para_traduzir": os.path.join(base_path, "02_PARA_TRADUZIR_JSON"),
    "em_revisao": os.path.join(base_path, "03_EM_REVISAO_JSON"),
    "aprovados": os.path.join(base_path, "04_APROVADOS_JSON"),
    "traduzidos": os.path.join(base_path, "05_TRADUZIDOS_XML"),
    "logs": os.path.join(base_path, "LOGS")
}

# Configuração do Logging para registrar tudo que acontece
os.makedirs(paths["logs"], exist_ok=True)
log_file = os.path.join(paths["logs"], "pipeline.log")
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.FileHandler(log_file), logging.StreamHandler()])

class AutomationHandler(FileSystemEventHandler):
    """
    Esta classe define o que acontece quando o 'vigia' percebe
    uma mudança em uma das pastas.
    """
    def on_created(self, event):
        # Ignora se uma pasta for criada, só nos importamos com arquivos.
        if event.is_directory:
            return

        file_path = event.src_path
        filename = os.path.basename(file_path)
        
        # --- LÓGICA DO PIPELINE ---

        # ETAPA 1: Novo XML na pasta de ORIGINAIS
        if os.path.dirname(file_path) == paths["originais"] and filename.endswith('.xml'):
            logging.info(f"Detectado novo XML: {filename}. Iniciando extração.")
            json_saida = os.path.join(paths["para_traduzir"], filename.replace('.xml', '.json'))
            if extrair_textos(file_path, json_saida):
                logging.info(f"Extração concluída. JSON gerado em 02_PARA_TRADUZIR_JSON.")
            else:
                logging.error(f"Falha na extração de {filename}.")

        # ETAPA 2: Novo JSON na pasta PARA_TRADUZIR
        elif os.path.dirname(file_path) == paths["para_traduzir"] and filename.endswith('.json'):
            logging.info(f"Detectado JSON para tradução: {filename}. Acionando API Gemini.")
            json_revisao = os.path.join(paths["em_revisao"], filename)
            if traduzir_arquivo_json(file_path, json_revisao, API_KEY):
                logging.info(f"Tradução da API concluída. Arquivo movido para 03_EM_REVISAO_JSON.")
                os.remove(file_path) # Remove o arquivo da etapa anterior
            else:
                logging.error(f"Falha na tradução via API de {filename}.")

        # ETAPA 3: JSON movido para APROVADOS
        elif os.path.dirname(file_path) == paths["aprovados"] and filename.endswith('.json'):
            logging.info(f"Detectado JSON aprovado: {filename}. Injetando tradução no XML.")
            xml_original = os.path.join(paths["originais"], filename.replace('.json', '.xml'))
            xml_final = os.path.join(paths["traduzidos"], filename.replace('.json', '_TRADUZIDO.xml'))
            
            if os.path.exists(xml_original):
                if injetar_traducoes(xml_original, file_path, xml_final):
                    logging.info(f"PROCESSO CONCLUÍDO para {filename}! XML final salvo em 05_TRADUZIDOS_XML.")
                else:
                    logging.error(f"Falha ao injetar traduções para {filename}.")
            else:
                logging.warning(f"XML original para {filename} não encontrado na pasta 01_ORIGINAIS.")


if __name__ == "__main__":
    logging.info("Iniciando o Vigia da Automação...")
    
    # Garante que todas as pastas de destino existam
    for path in paths.values():
        os.makedirs(path, exist_ok=True)
        
    event_handler = AutomationHandler()
    observer = Observer()
    
    # Diz ao observer quais pastas ele deve vigiar
    observer.schedule(event_handler, paths["originais"], recursive=False)
    observer.schedule(event_handler, paths["para_traduzir"], recursive=False)
    observer.schedule(event_handler, paths["aprovados"], recursive=False)
    
    observer.start()
    logging.info("Vigia iniciado. Monitorando pastas...")
    
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    logging.info("Vigia encerrado.")