import json
import os
import requests
import deepl
from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential
import google.generativeai as genai
from google.api_core.exceptions import NotFound as GoogleNotFound


class TranslationService:
    def translate(self, text, config):
        raise NotImplementedError


def carregar_glossario(target_lang=None):
    """Load glossary entries; tries language specific file first."""
    base_dir = os.path.dirname(__file__)
    candidate_files = []
    if target_lang:
        candidate_files.append(os.path.join(base_dir, f"glossario_{target_lang}.json"))
    candidate_files.append(os.path.join(base_dir, "glossario.json"))

    for path in candidate_files:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as stream:
                return json.load(stream)
    return {}




def _candidate_model_names(model_name: str):
    names = []
    if model_name:
        names.append(model_name)
        base = model_name.split("/")[-1]
        if base not in names:
            names.append(base)
        if base and not base.endswith("-latest"):
            names.append(base + "-latest")
            names.append(f"models/{base}-latest")
        if model_name.startswith("models/") and not model_name.endswith("-latest"):
            names.append(model_name + "-latest")
    names.extend(["models/gemini-1.5-flash", "gemini-1.5-flash"])
    seen = []
    for name in names:
        if name and name not in seen:
            seen.append(name)
    return seen


def get_gemini_model(model_name: str):
    last_error = None
    for candidate in _candidate_model_names(model_name):
        try:
            return genai.GenerativeModel(candidate)
        except GoogleNotFound as exc:
            last_error = exc
        except Exception as exc:
            last_error = exc
    if last_error:
        raise last_error
    raise RuntimeError("Nao foi possivel instanciar o modelo Gemini.")

class GeminiService(TranslationService):
    def translate(self, text, config):
        target_lang = (config.get("target_lang") or "pt").lower()
        target_label = config.get("target_label", "Portuguese (Brazil)")
        source_label = config.get("source_label", "English")

        genai.configure(api_key=config.get("api_key"))
        model = get_gemini_model(config.get("model", "gemini-1.5-flash"))

        # Only reuse glossary when translating to Brazilian Portuguese.
        glossary = carregar_glossario(target_lang if target_lang == "pt" else None)
        glossary_pairs = sorted(glossary.items(), key=lambda item: len(item[0]), reverse=True)
        pretranslated_text = text
        glossary_used = False

        for original_term, target_term in glossary_pairs:
            if original_term in pretranslated_text:
                pretranslated_text = pretranslated_text.replace(original_term, target_term)
                glossary_used = True

        if glossary_used and target_lang == "pt":
            prompt = (
                "Refine the following pre-translated sentence so it sounds natural in "
                f"{target_label}, keeping the words that are already in Portuguese untouched. "
                f'Text: "{pretranslated_text}". Reply with the final text only.'
            )
        else:
            prompt = (
                "Act as a game localization specialist. "
                f"Translate the following text from {source_label} to {target_label}: "
                f'"{text}". Reply with the final text only.'
            )

        response = model.generate_content(prompt)
        return response.text.strip()


class DeepLService(TranslationService):
    def translate(self, text, config):
        translator = deepl.Translator(config.get("api_key"))
        target_code = config.get("deepl_lang", "PT-BR")
        result = translator.translate_text(text, target_lang=target_code)
        return result.text


class AzureService(TranslationService):
    def translate(self, text, config):
        credential = AzureKeyCredential(config.get("api_key"))
        endpoint = "https://api.cognitive.microsofttranslator.com"
        text_translator = TextTranslationClient(endpoint=endpoint, credential=credential)
        target_code = config.get("target_lang", "pt")
        response = text_translator.translate(content=[text], to_language=[target_code])
        return response[0].translations[0].text


class OllamaService(TranslationService):
    def translate(self, text, config):
        url = "http://localhost:11434/api/generate"
        target_label = config.get("target_label", "Portuguese (Brazil)")

        prompt = (
            "[INST]Act as a translation service that converts JSON values only. "
            f"Translate the value below to {target_label}. Keep the key exactly the same. "
            "Respond with JSON only.\n\n"
            "Input:\n"
            "{\n"
            f'    "text": "{text}"\n'
            "}\n\n"
            "Output:[/INST]"
        )

        data = {
            "model": config.get("model", "llama3"),
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }

        response = requests.post(url, json=data, timeout=config.get("timeout", 120))
        response.raise_for_status()

        response_json_text = response.json()["response"]
        translated_dict = json.loads(response_json_text)
        return next(iter(translated_dict.values()))


AVAILABLE_SERVICES = {
    "Gemini": GeminiService(),
    "DeepL": DeepLService(),
    "Microsoft Azure": AzureService(),
    "Llama 3 (Local)": OllamaService(),
}


def translate_text(servico_escolhido, texto, config):
    if servico_escolhido in AVAILABLE_SERVICES:
        try:
            service = AVAILABLE_SERVICES[servico_escolhido]
            return service.translate(texto, config)
        except Exception as exc:
            error_message = str(exc)
            if "Connection refused" in error_message:
                return "ERRO: Nao foi possivel conectar ao servidor local do Ollama. Verifique se ele esta rodando."
            return f"ERRO na API ({servico_escolhido}): {exc}"
    return f"Servico '{servico_escolhido}' nao reconhecido."


__all__ = ["AVAILABLE_SERVICES", "translate_text", "get_gemini_model"]
