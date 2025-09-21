import google.generativeai as genai
import json
import time
import os
import re # Importamos a biblioteca de Expressões Regulares para processar a resposta

# --- CONFIGURAÇÃO ---
# Coloque sua chave da API do Google AI Studio aqui
GOOGLE_API_KEY = "AIzaSyDs7iaQpQqFX48opXu_YPJv7_BCrXcMppE"
genai.configure(api_key=GOOGLE_API_KEY)

# Nome dos arquivos
ARQUIVO_ENTRADA = 'textos_para_traduzir.json'
ARQUIVO_SAIDA = 'textos_traduzidos.json'

# --- PARÂMETRO CHAVE ---
# Quantos itens enviar para a IA de uma só vez. 100 é um bom número.
TAMANHO_DO_LOTE = 100

# Configuração do Modelo Gemini
model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")


def traduzir_lote(lote_de_texto):
    """Envia um grande bloco de texto formatado para a IA e retorna a resposta."""
    
    prompt = f"""Aja como um tradutor técnico especializado em localização de jogos.
A seguir está um bloco de textos para tradução, cada um com um ID único.
Traduza o conteúdo de cada item do inglês para o português do Brasil.
Sua resposta DEVE manter EXATAMENTE o mesmo formato de [ID: ...] e separadores ---, substituindo apenas o texto em inglês pelo traduzido.

---INÍCIO DO BLOCO---
{lote_de_texto}
---FIM DO BLOCO---
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"  !! Erro na API durante o processamento do lote: {e}")
        return None

# Carrega o arquivo JSON com os textos originais
try:
    with open(ARQUIVO_ENTRADA, 'r', encoding='utf-8') as f:
        dados_originais = json.load(f)
except FileNotFoundError:
    print(f"ERRO: Arquivo '{ARQUIVO_ENTRADA}' não encontrado.")
    exit()

# Dicionário para guardar todas as traduções
dados_traduzidos = {}
lista_de_itens = list(dados_originais.items())
total_itens = len(lista_de_itens)

print(f"Iniciando tradução de {total_itens} itens em lotes de {TAMANHO_DO_LOTE}...")

# Loop principal que processa o arquivo em lotes
for i in range(0, total_itens, TAMANHO_DO_LOTE):
    lote_atual = lista_de_itens[i:i + TAMANHO_DO_LOTE]
    
    # Formata o lote em um único bloco de texto
    texto_para_prompt = ""
    for xpath, texto in lote_atual:
        texto_para_prompt += f"[ID: {xpath}]\n{texto}\n---\n"
    
    num_lote = (i // TAMANHO_DO_LOTE) + 1
    total_lotes = (total_itens + TAMANHO_DO_LOTE - 1) // TAMANHO_DO_LOTE
    
    print(f"\n--- Processando Lote {num_lote}/{total_lotes} ({len(lote_atual)} itens) ---")
    
    # Envia o lote para a IA
    resposta_do_lote = traduzir_lote(texto_para_prompt)
    
    if resposta_do_lote:
        # Processa a resposta da IA para extrair cada tradução
        # A expressão regular procura por blocos [ID: ...] texto ---
        traducoes_encontradas = re.findall(r'\[ID: (.*?)\]\n(.*?)\n---', resposta_do_lote, re.DOTALL)
        
        for xpath, texto_traduzido in traducoes_encontradas:
            dados_traduzidos[xpath.strip()] = texto_traduzido.strip()
        
        print(f"Lote {num_lote} concluído. {len(traducoes_encontradas)} traduções processadas.")
    else:
        print(f"Lote {num_lote} falhou. Pulando para o próximo.")

    # Pausa entre os lotes para não sobrecarregar a API
    time.sleep(5)

# Salva o dicionário final em um arquivo JSON
with open(ARQUIVO_SAIDA, 'w', encoding='utf-8') as f:
    json.dump(dados_traduzidos, f, indent=4, ensure_ascii=False)

print(f"\nTradução concluída! {len(dados_traduzidos)}/{total_itens} itens salvos em '{ARQUIVO_SAIDA}'.")