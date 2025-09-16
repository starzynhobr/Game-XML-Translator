import xml.etree.ElementTree as ET
import json

def injetar_traducoes(arquivo_xml_original, arquivo_json_aprovado, arquivo_xml_final):
    try:
        with open(arquivo_json_aprovado, 'r', encoding='utf-8') as f:
            mapa_traducoes = json.load(f)
        
        tree = ET.parse(arquivo_xml_original)
        root = tree.getroot()
        
        for item in root.findall('.//item'):
            disp_name = item.find('dispName')
            if disp_name is not None and disp_name.text:
                texto_original = disp_name.text.strip()
                if texto_original in mapa_traducoes:
                    disp_name.text = mapa_traducoes[texto_original]
        
        tree.write(arquivo_xml_final, encoding='utf-8', xml_declaration=True)
        return True
    except Exception as e:
        print(f"Erro ao injetar traduções em {arquivo_xml_original}: {e}")
        return False