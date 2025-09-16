import xml.etree.ElementTree as ET
import json

def injetar_traducoes(arquivo_xml_original: str, mapa_traducoes: dict, arquivo_xml_final: str):
    """
    Lê um dicionário com traduções e as aplica a um arquivo XML,
    gerando um novo XML traduzido.
    """
    try:
        tree = ET.parse(arquivo_xml_original)
        root = tree.getroot()
        
        itens_modificados = 0
        for item in root.findall('.//item'):
            disp_name = item.find('dispName')
            if disp_name is not None and disp_name.text:
                texto_original = disp_name.text.strip()
                if texto_original in mapa_traducoes:
                    # Pega a tradução do dicionário que passamos
                    disp_name.text = mapa_traducoes[texto_original]
                    itens_modificados += 1

        tree.write(arquivo_xml_final, encoding='utf-8', xml_declaration=True)
        print(f"Injeção concluída! {itens_modificados} textos foram substituídos.")
        return True
    except Exception as e:
        print(f"Erro ao injetar traduções em {arquivo_xml_original}: {e}")
        return False