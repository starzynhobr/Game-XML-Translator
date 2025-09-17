import xml.etree.ElementTree as ET
import json

def injetar_traducoes(arquivo_xml_original: str, mapa_traducoes: dict, arquivo_xml_final: str, target_tag="dispName"):
    """
    Lê um dicionário com traduções e as aplica a um arquivo XML,
    gerando um novo XML traduzido.
    """
    try:
        tree = ET.parse(arquivo_xml_original)
        root = tree.getroot()
        
        itens_modificados = 0
        for item in root.findall('.//item'):
            target_element = item.find(target_tag)
            if target_element is not None and target_element.text:
                # CORREÇÃO AQUI: Usa a variável correta 'target_element'
                texto_original = target_element.text.strip()
                if texto_original in mapa_traducoes:
                    # CORREÇÃO AQUI: Usa a variável correta 'target_element'
                    target_element.text = mapa_traducoes[texto_original]
                    itens_modificados += 1

        tree.write(arquivo_xml_final, encoding='utf-8', xml_declaration=True)
        print(f"Injeção concluída! {itens_modificados} textos foram substituídos.")
        return True
    except Exception as e:
        print(f"Erro ao injetar traduções em {arquivo_xml_original}: {e}")
        return False