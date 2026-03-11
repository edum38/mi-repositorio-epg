import requests
import gzip
import re
from datetime import datetime, timedelta

# Configuración
URL_OPEN = "http://www.teleguide.info/download/new3/xmltv.xml.gz"
DESFASE = -2

# Diccionario de traducción (IDs comunes)
TRADUCCIONES = {
    "discovery": "Discovery Channel",
    "disney": "Disney Channel",
    "hbo": "HBO",
    "mtv": "MTV España",
    "cnn": "CNN International",
    "eurosport": "Eurosport",
    "fox": "FOX",
    "axn": "AXN"
}

def ajustar_hora(match):
    t = match.group(1)
    try:
        dt = datetime.strptime(t, "%Y%m%d%H%M%S") + timedelta(hours=DESFASE)
        return dt.strftime("%Y%m%d%H%M%S")
    except:
        return t

def main():
    print("Iniciando descarga...")
    try:
        r = requests.get(URL_OPEN, timeout=45)
        if r.status_code != 200:
            print(f"Error de red: {r.status_code}")
            return
        
        # Descomprimir y limpiar 'lang' y atributos molestos
        content = gzip.decompress(r.content).decode('utf-8', errors='ignore')
        content = re.sub(r'\slang=".*?"', '', content)
        
        # 1. Procesar Canales
        canales = re.findall(r'<channel.*?</channel>', content, re.DOTALL)
        final_xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv>']
        
        ids_vistos = set()
        for c in canales:
            match_id = re.search(r'id="(.*?)"', c)
            if match_id:
                cid = match_id.group(1)
                cid_low = cid.lower()
                nombre_final = None
                
                # Buscar traducción
                for clave, trad in TRADUCCIONES.items():
                    if clave in cid_low:
                        nombre_final = trad
                        break
                
                if nombre_final:
                    # Si hay traducción, BORRAMOS el nombre original (cirílico)
                    c = f'<channel id="{cid}">\n    <display-name>{nombre_final}</display-name>\n  </channel>'
                
                final_xml.append(c)
                ids_vistos.add(cid)

        # 2. Procesar Programas
        programas = re.findall(r'<programme.*?</programme>', content, re.DOTALL)
        for p in programas:
            m_chan = re.search(r'channel="(.*?)"', p)
            if m_chan and m_chan.group(1) in ids_vistos:
                # Ajuste de hora
                p = re.sub(r'(\d{14})', ajustar_hora, p)
                # Forzar formato horario para España
                p = re.sub(r'\+\d{4}', '+0100', p)
                final_xml.append(p)

        final_xml.append('</tv>')
        
        with open("guia_completa.xml", "w", encoding="utf-8") as f:
            f.write("\n".join(final_xml))
        print(f"Éxito: {len(ids_vistos)} canales generados.")

    except Exception as e:
        print(f"Error crítico: {e}")

if __name__ == "__main__":
    main()









