import google.generativeai as genai
import json
import time
import os

def carregar_glossario(caminho_glossario):
    """Carrega o glossário de um arquivo JSON, se ele existir."""
    if os.path.exists(caminho_glossario):
        with open(caminho_glossario, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {} # Retorna um dicionário vazio se o arquivo não existir

def traduzir_arquivo_json(arquivo_json_entrada, arquivo_json_saida, api_key):
    # --- CONFIGURAÇÃO ---
    genai.configure(api_key=api_key)
    # Use o nome do modelo que funcionou para você
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest') 
    
    # Carrega nosso novo glossário
    caminho_do_glossario = os.path.join(os.path.dirname(__file__), 'glossario.json')
    glossario = carregar_glossario(caminho_do_glossario)
    if glossario:
        print("✅ Glossário carregado com sucesso!")
    
    # Ordena as chaves do glossário da mais longa para a mais curta
    # para evitar substituições parciais (ex: "Kinetic Blade" antes de "Blade")
    glossario_ordenado = sorted(glossario.items(), key=lambda item: len(item[0]), reverse=True)

    try:
        with open(arquivo_json_entrada, 'r', encoding='utf-8') as f:
            mapa_traducoes = json.load(f)
            
        mapa_final = {}
        for original, traducao in mapa_traducoes.items():
            if original == traducao: # Só traduz se não foi traduzido ainda
                print(f"Traduzindo: '{original}'...", end='')
                
                texto_pre_traduzido = original
                termos_usados = False
                
                # --- LÓGICA DO GLOSSÁRIO ---
                for termo_en, termo_pt in glossario_ordenado:
                    if termo_en in texto_pre_traduzido:
                        texto_pre_traduzido = texto_pre_traduzido.replace(termo_en, termo_pt)
                        termos_usados = True
                
                if termos_usados:
                    print(" -> [Usando Glossário]...", end='')
                    prompt = f"""Corrija a gramática, gênero, número e a ordem das palavras para o português do Brasil na frase abaixo.
                    - Mantenha as palavras que já estão corretamente em português.
                    - Responda APENAS com o texto corrigido, sem nenhuma explicação.

                    Frase pré-traduzida: "{texto_pre_traduzido}"
                    Correção:"""
                else:
                    # Se nenhum termo do glossário foi usado, usa o prompt original
                    prompt = f"""Traduza o seguinte nome de item de jogo do inglês para o português do Brasil.
                    - Mantenha a capitalização de nomes próprios e termos como 'Mk II'.
                    - Responda APENAS com o texto traduzido, sem nenhuma explicação.
                    
                    Texto original: "{original}"
                    Tradução:"""
                
                # --- CHAMADA DA API ---
                response = model.generate_content(prompt)
                traducao_nova = response.text.strip()
                mapa_final[original] = traducao_nova
                print(f" -> '{traducao_nova}'")
                
                # Use a pausa que funcionou para você
                time.sleep(5) 
            else:
                mapa_final[original] = traducao

        with open(arquivo_json_saida, 'w', encoding='utf-8') as f:
            json.dump(mapa_final, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"\nErro ao traduzir {arquivo_json_entrada}: {e}")
        return False