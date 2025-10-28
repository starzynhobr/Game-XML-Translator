import xml.etree.ElementTree as ET
from collections import Counter

def criar_impressao_digital(arquivo_xml):
    """
    Lê um arquivo XML e retorna um dicionário com a contagem de cada tag.
    """
    try:
        tree = ET.parse(arquivo_xml)
        root = tree.getroot()
        
        # Encontra TODAS as tags no documento e as coloca em uma lista
        todas_as_tags = [elem.tag for elem in root.iter()]
        
        # Usa o 'Counter' para contar a ocorrência de cada tag
        contagem_de_tags = Counter(todas_as_tags)
        
        return contagem_de_tags
    except ET.ParseError as e:
        print(f"ERRO: Não foi possível ler o arquivo '{arquivo_xml}'. Não é um XML válido. Detalhes: {e}")
        return None
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{arquivo_xml}' não encontrado.")
        return None

def comparar_estruturas(arquivo_original, arquivo_modificado):
    """
    Compara a "impressão digital" de dois arquivos XML.
    """
    print("--- Iniciando Validação de Estrutura XML ---")
    
    impressao_original = criar_impressao_digital(arquivo_original)
    impressao_modificada = criar_impressao_digital(arquivo_modificado)

    if impressao_original is None or impressao_modificada is None:
        print("\nValidação falhou devido a um erro de leitura de arquivo.")
        return

    print(f"\n[i] Impressão Digital do Arquivo Original ({os.path.basename(arquivo_original)}):")
    print(impressao_original)
    
    print(f"\n[i] Impressão Digital do Arquivo Modificado ({os.path.basename(arquivo_modificado)}):")
    print(impressao_modificada)

    # A comparação mágica acontece aqui. Dicionários são iguais se têm as mesmas chaves e valores.
    if impressao_original == impressao_modificada:
        print("\n[OK] SUCESSO! A estrutura dos arquivos é idêntica.")
    else:
        print("\n[FALHA] ATENÇÃO! A estrutura dos arquivos é DIFERENTE.")
        
        # Encontra as diferenças para um relatório mais detalhado
        chaves_originais = set(impressao_original.keys())
        chaves_modificadas = set(impressao_modificada.keys())

        chaves_faltando = chaves_originais - chaves_modificadas
        if chaves_faltando:
            print(f" -> Tags que existem no original mas faltam no modificado: {chaves_faltando}")

        chaves_extras = chaves_modificadas - chaves_originais
        if chaves_extras:
            print(f" -> Tags que existem no modificado mas não no original: {chaves_extras}")
        
        for chave in chaves_originais.intersection(chaves_modificadas):
            if impressao_original[chave] != impressao_modificada[chave]:
                print(f" -> Contagem diferente para a tag <{chave}>: Original={impressao_original[chave]}, Modificado={impressao_modificada[chave]}")
    
    print("\n--- Validação Concluída ---")

# --- COMO USAR ---
import os

# 1. Defina o caminho para o seu arquivo XML original
caminho_original = r"C:\Users\stz\Desktop\Traducao MAA REDUX\XMLs Traduzidas\characters.xml" # <-- MUDE AQUI

# 2. Defina o caminho para o arquivo XML que seu programa gerou
caminho_traduzido = r"C:\Users\stz\Desktop\Traducao MAA REDUX\XMLs Traduzidas\characters_traduzido.xml" # <-- MUDE AQUI

comparar_estruturas(caminho_original, caminho_traduzido)