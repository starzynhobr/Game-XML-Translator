import os
import json
import deepl
from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential
import google.generativeai as genai
from google.cloud import translate_v2 as translate

# --- Carregador de Glossário (continua o mesmo) ---
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
class DeepLService:
    def translate(self, text, config):
        translator = deepl.Translator(config.get("api_key"))
        result = translator.translate_text(text, target_lang="PT-BR")
        return result.text

# --- Adaptador para o Microsoft Azure ---
class AzureService:
    def translate(self, text, config):
        credential = AzureKeyCredential(config.get("api_key"))
        text_translator = TextTranslationClient(endpoint=f"https://api.cognitive.microsofttranslator.com", credential=credential)
        
        response = text_translator.translate(content=[text], to_language=["pt"])
        return response[0].translations[0].text

# --- Adaptador para o Google Cloud Translate ---
class GoogleCloudService:
    def translate(self, text, config):
        # Esta API requer um arquivo de credenciais JSON. A configuração é mais complexa.
        # Por simplicidade, vamos deixar um placeholder.
        # os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'caminho/para/sua/chave.json'
        # translate_client = translate.Client()
        # result = translate_client.translate(text, target_language='pt')
        # return result['translatedText']
        print("Google Cloud Translate requer configuração avançada de credenciais.")
        return f"[Google Cloud indisponível] {text}"

# --- Dicionário de Provedores (O Coração do Adaptador) ---
AVAILABLE_SERVICES = {
    "Gemini": GeminiService(),
    "DeepL": DeepLService(),
    "Microsoft Azure": AzureService(),
    # "Google Cloud": GoogleCloudService(), # Desabilitado por ser mais complexo
}

def translate_text(servico_escolhido, texto, config):
    if servico_escolhido in AVAILABLE_SERVICES:
        try:
            service = AVAILABLE_SERVICES[servico_escolhido]
            return service.translate(texto, config)
        except Exception as e:
            return f"ERRO na API ({servico_escolhido}): {e}"
    return f"Serviço '{servico_escolhido}' não reconhecido."