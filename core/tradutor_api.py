import os
import json
import requests # Novo import
import deepl
from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential
import google.generativeai as genai

# --- Classe Base (Boa Prática) ---
class TranslationService:
    def translate(self, text, config):
        raise NotImplementedError

# --- Carregador de Glossário ---
def carregar_glossario():
    glossary_path = os.path.join(os.path.dirname(__file__), 'glossario.json')
    if os.path.exists(glossary_path):
        with open(glossary_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# --- Adaptador para o Gemini ---
class GeminiService:
    def translate(self, text, config):
        genai.configure(api_key=config.get("api_key"))
        model = genai.GenerativeModel(config.get("model", "models/gemini-1.5-flash-latest"))
        
        # (A lógica de prompt e glossário que já tínhamos)
        glossario = carregar_glossario()
        glossario_ordenado = sorted(glossario.items(), key=lambda item: len(item[0]), reverse=True)
        texto_pre_traduzido = text
        termos_usados = False
        for termo_en, termo_pt in glossario_ordenado:
            if termo_en in texto_pre_traduzido:
                texto_pre_traduzido = texto_pre_traduzido.replace(termo_en, termo_pt)
                termos_usados = True
        
        if termos_usados:
            prompt = f"Corrija a gramática e a ordem das palavras para o português do Brasil na frase pré-traduzida, mantendo as palavras que já estão em português: \"{texto_pre_traduzido}\"\n\nResponda APENAS com o texto final."
        else:
            prompt = f"Aja como um localizador de jogos e traduza o seguinte nome de item do inglês para o português do Brasil: \"{text}\"\n\nResponda APENAS com o texto final."

        response = model.generate_content(prompt)
        return response.text.strip()

# --- Adaptador para o DeepL ---
class DeepLService(TranslationService):
    def translate(self, text, config):
        # ... (código do DeepLService continua o mesmo)
        translator = deepl.Translator(config.get("api_key"))
        result = translator.translate_text(text, target_lang="PT-BR")
        return result.text

# --- Adaptador para o Microsoft Azure ---
class AzureService(TranslationService):
    def translate(self, text, config):
        # ... (código do AzureService continua o mesmo)
        credential = AzureKeyCredential(config.get("api_key"))
        endpoint = f"https://api.cognitive.microsofttranslator.com"
        text_translator = TextTranslationClient(endpoint=endpoint, credential=credential)
        response = text_translator.translate(content=[text], to_language=["pt"])
        return response[0].translations[0].text

# --- NOVO: Adaptador para o Ollama (Llama 3 Local) ---
class OllamaService(TranslationService):
    def translate(self, text, config):
        url = "http://localhost:11434/api/generate"
        
        # --- NOVO PROMPT MAIS DIRETO E BASEADO EM EXEMPLOS ---
        prompt = f"""[INST] Aja como um serviço de tradução que converte valores de um JSON. Traduza apenas o valor do JSON a seguir do inglês para o português do Brasil. Mantenha a chave em inglês. Sua resposta deve ser SOMENTE o JSON traduzido, sem nenhum outro texto.

        Entrada:
        {{
            "{text}": "{text}"
        }}

        Saída: [/INST]"""

        data = {
            "model": config.get("model", "llama3"),
            "prompt": prompt,
            "stream": False,
            "format": "json" # Instrução explícita para o Ollama retornar JSON
        }
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        response_json_text = response.json()['response']
        
        # Extrai apenas o valor traduzido do JSON retornado
        translated_dict = json.loads(response_json_text)
        return list(translated_dict.values())[0]

# --- Dicionário de Provedores ATUALIZADO ---
AVAILABLE_SERVICES = {
    "Gemini": GeminiService(),
    "DeepL": DeepLService(),
    "Microsoft Azure": AzureService(),
    "Llama 3 (Local)": OllamaService(), # ADICIONADO!
}

def translate_text(servico_escolhido, texto, config):
    if servico_escolhido in AVAILABLE_SERVICES:
        try:
            service = AVAILABLE_SERVICES[servico_escolhido]
            return service.translate(texto, config)
        except Exception as e:
            # Retorna uma mensagem de erro clara para o log
            error_message = str(e)
            if "Connection refused" in error_message:
                return "ERRO: Não foi possível conectar ao servidor local do Ollama. Verifique se ele está rodando."
            return f"ERRO na API ({servico_escolhido}): {e}"
    return f"Serviço '{servico_escolhido}' não reconhecido."