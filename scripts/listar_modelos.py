import google.generativeai as genai
import os
from dotenv import load_dotenv

# Carrega a API Key do arquivo .env
print("Carregando chave da API...")
load_dotenv(dotenv_path='./.env')
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("FALHA: Não foi possível encontrar a GOOGLE_API_KEY no arquivo .env")
else:
    genai.configure(api_key=API_KEY)
    print("\n✅ Chave encontrada. Buscando modelos disponíveis que suportam 'generateContent'...\n")
    
    try:
        for m in genai.list_models():
            # Vamos listar apenas os modelos que podem gerar conteúdo, que é o que precisamos
            if 'generateContent' in m.supported_generation_methods:
                print(f" - {m.name}")
    except Exception as e:
        print(f"Ocorreu um erro ao listar os modelos: {e}")