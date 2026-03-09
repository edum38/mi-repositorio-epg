import requests
import gzip
import re

EPG_SOURCES = [
    "https://iptv-org.github.io/epg/guides/es/movistarplus.es.xml",
    "https://iptv-org.github.io/epg/guides/it/sky.it.xml",
    "https://iptv-org.github.io/epg/guides/fr/programme-tv.net.xml",
    "https://iptv-org.github.io/epg/guides/de/tvtoday.de.xml",
    "https://iptv-org.github.io/epg/guides/uk/sky.com.xml",
    "https://iptv-org.github.io/epg/guides/br/meuguia.tv.xml",
    "https://iptv-org.github.io/epg/guides/ar/mi.tv.xml",
    "https://iptv-org.github.io/epg/guides/pe/mi.tv.xml",
    "https://iptv-org.github.io/epg/guides/co/mi.tv.xml",
    "https://iptv-org.github.io/epg/guides/mx/mi.tv.xml"
]

def main():
    print("Iniciando generación de EPG...")
    # Cabecera estándar de XMLTV
    final_xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv generator-info-name="MiAppIPTV">']
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    for url in EPG_SOURCES:
        try:
            print(f"Descargando: {url}")
            r = requests.get(url, headers=headers, timeout=30)
            if r.status_code == 200:
                # Convertimos a texto asegurando UTF-8
                content = r.content.decode('utf-8', errors='ignore')
                
                # Buscamos los bloques de canales y programas ignorando mayúsculas/minúsculas
                channels = re.findall(r'<channel.*?</channel>', content, re.DOTALL | re.IGNORECASE)
                programmes = re.findall(r'<programme.*?</programme>', content, re.DOTALL | re.IGNORECASE)
                
                if channels:
                    final_xml.extend(channels)
                    print(f"  --> OK: {len(channels)} canales encontrados.")
                if programmes:
                    final_xml.extend(programmes)
                
                if not channels and not programmes:
                    print("  --> Advertencia: No se encontraron etiquetas válidas en esta URL.")
            else:
                print(f"  --> Error HTTP: {r.status_code}")
        except Exception as e:
            print(f"  --> Error procesando {url}: {e}")

    final_xml.append('</tv>')
    full_text = "\n".join(final_xml)

    # Guardar archivos
    with open("guia_completa.xml", "w", encoding="utf-8") as f:
        f.write(full_text)

    with gzip.open("guia_completa.xml.gz", "wt", encoding="utf-8") as f:
        f.write(full_text)
    
    print(f"\nPROCESO FINALIZADO. Archivo guardado con {len(full_text)} caracteres.")

if __name__ == "__main__":
    main()


