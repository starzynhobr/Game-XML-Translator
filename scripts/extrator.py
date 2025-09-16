import xml.etree.ElementTree as ET
import json

def extrair_textos(arquivo_xml, arquivo_json_saida, target_tag="dispName"):
    textos_unicos = set()
    try:
        tree = ET.parse(arquivo_xml)
        root = tree.getroot()
        for item in root.findall('.//item'):
            target_element = item.find(target_tag) # Usa o parâmetro em vez de 'dispName'
            if target_element is not None and target_element.text:
                textos_unicos.add(target_element.text.strip())
        
        dicionario_traducao = {texto: texto for texto in sorted(list(textos_unicos))}
        
        with open(arquivo_json_saida, 'w', encoding='utf-8') as f:
            json.dump(dicionario_traducao, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Erro ao extrair de {arquivo_xml}: {e}")
        return False