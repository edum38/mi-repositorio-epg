import requests
import gzip
import re

# Usamos el CDN de jsDelivr para saltar el bloqueo de GitHub Actions
EPG_SOURCES = [
    # España
    "https://cdn.jsdelivr.net/gh/davidmuma/EPG_dobleM@master/guia.xml",
    # Latinoamérica
    "https://cdn.jsdelivr.net/gh/sonidariel/EPG-LATAM@master/guide.xml",
    # Europa (Italia, Francia, etc)
    "https://cdn.jsdelivr.net/gh/freetown/epg@master/vvg_guide.xml",
    # Brasil
    "https://cdn.jsdelivr.net/gh/LITUATUI/LITUATUI.github.io@master/epg/guia.xml"
]

def main():
    print("Iniciando descarga con Bypass de CDN...")
    final_xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv generator-info-name="MiAppIPTV">']
    
    # User-Agent más real
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }

    for url in EPG_SOURCES:
        try:
            print(f"Petición a: {url}")
            r = requests.get(url, headers=headers, timeout=60)
            
            if r.status_code == 200:
                # Verificamos si es GZIP por los primeros bytes (mágico)
                if r.content[:2] == b'\x1f\x8b':
                    print("  --> Detectado formato comprimido GZ")
                    content = gzip.decompress(r.content).decode('utf-8', errors='ignore')
                else:
                    content = r.content.decode('utf-8', errors='ignore')
                
                # Búsqueda manual de bloques
                channels = re.findall(r'<channel.*?</channel>', content, re.DOTALL | re.IGNORECASE)
                programmes = re.findall(r'<programme.*?</programme>', content, re.DOTALL | re.IGNORECASE)
                
                if channels:
                    final_xml.extend(channels)
                    final_xml.extend(programmes)
                    print(f"  --> ÉXITO: {len(channels)} canales encontrados.")
                else:
                    # Si falla el regex, imprimimos los primeros 200 caracteres para ver qué llegó
                    print(f"  --> ERROR: No se hallaron etiquetas. Inicio del texto: {content[:200]}")
            else:
                print(f"  --> Error HTTP: {r.status_code}")
        except Exception as e:
            print(f"  --> Error crítico: {e}")

    final_xml.append('</tv>')
    full_text = "\n".join(final_xml)

    with open("guia_completa.xml", "w", encoding="utf-8") as f:
        f.write(full_text)
    with gzip.open("guia_completa.xml.gz", "wt", encoding="utf-8") as f:
        f.write(full_text)
    
    print(f"\nProceso terminado. Caracteres totales: {len(full_text)}")

if __name__ == "__main__":
    main()



