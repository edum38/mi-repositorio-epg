import requests
import gzip
import re

# FUENTES SELECCIONADAS PARA TUS PAÍSES
EPG_SOURCES = [
    # España
    "https://raw.githubusercontent.com/davidmuma/EPG_dobleM/master/guia.xml",
    # Latinoamérica (México, Argentina, Colombia, Perú)
    "https://raw.githubusercontent.com/sonidariel/EPG-LATAM/master/guide.xml",
    # Italia, Francia, Alemania, UK (Fuente Europea estable)
    "https://raw.githubusercontent.com/freetown/epg/master/vvg_guide.xml",
    # Brasil
    "https://raw.githubusercontent.com/LITUATUI/LITUATUI.github.io/master/epg/guia.xml"
]

def main():
    print("Iniciando descarga de EPG por países...")
    # Cabecera XMLTV
    final_xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv generator-info-name="MiAppIPTV-Multinacional">']
    
    headers = {'User-Agent': 'Mozilla/5.0'}

    for url in EPG_SOURCES:
        try:
            print(f"Descargando: {url}")
            r = requests.get(url, headers=headers, timeout=50)
            
            if r.status_code == 200:
                # Detectar si es GZ o XML plano
                if url.endswith(".gz") or r.content[:2] == b'\x1f\x8b':
                    content = gzip.decompress(r.content).decode('utf-8', errors='ignore')
                else:
                    content = r.content.decode('utf-8', errors='ignore')
                
                # Extraer canales y programas
                channels = re.findall(r'<channel.*?</channel>', content, re.DOTALL | re.IGNORECASE)
                programmes = re.findall(r'<programme.*?</programme>', content, re.DOTALL | re.IGNORECASE)
                
                if channels:
                    final_xml.extend(channels)
                    final_xml.extend(programmes)
                    print(f"  --> OK: {len(channels)} canales añadidos.")
                else:
                    print("  --> No se encontraron canales en esta URL.")
            else:
                print(f"  --> Error HTTP: {r.status_code}")
        except Exception as e:
            print(f"  --> Error en {url}: {e}")

    final_xml.append('</tv>')
    full_text = "\n".join(final_xml)

    # Guardar archivos
    with open("guia_completa.xml", "w", encoding="utf-8") as f:
        f.write(full_text)
    with gzip.open("guia_completa.xml.gz", "wt", encoding="utf-8") as f:
        f.write(full_text)
    
    print(f"\n¡LISTO! EPG generada correctamente.")

if __name__ == "__main__":
    main()


