import requests
import gzip
import re

# FUENTES ALTERNATIVAS (Más estables para Scripts)
EPG_SOURCES = [
    "https://osdn.net/projects/xmltv/storage/xmltv.xml.gz", # Fuente Global (Backup)
    "https://raw.githubusercontent.com/sonidariel/EPG-LATAM/master/guide.xml", # Latam (Arg, Mex, Col, Pe)
    "https://raw.githubusercontent.com/davidmuma/EPG_dobleM/master/guia.xml", # España
    "https://www.teleguide.info/download/new3/xmltv.xml.gz", # Europa (Fr, De, It, Uk)
]

def main():
    print("Iniciando descarga de fuentes alternativas...")
    final_xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv generator-info-name="MiAppIPTV">']
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    for url in EPG_SOURCES:
        try:
            print(f"Descargando: {url}")
            r = requests.get(url, headers=headers, timeout=45)
            
            if r.status_code == 200:
                # Si la URL termina en .gz, hay que descomprimirla primero
                if url.endswith(".gz"):
                    content = gzip.decompress(r.content).decode('utf-8', errors='ignore')
                else:
                    content = r.content.decode('utf-8', errors='ignore')
                
                # Buscamos bloques de canales y programas
                channels = re.findall(r'<channel.*?</channel>', content, re.DOTALL | re.IGNORECASE)
                programmes = re.findall(r'<programme.*?</programme>', content, re.DOTALL | re.IGNORECASE)
                
                if channels or programmes:
                    final_xml.extend(channels)
                    final_xml.extend(programmes)
                    print(f"  --> ÉXITO: {len(channels)} canales y {len(programmes)} programas.")
                else:
                    print("  --> No se encontraron datos en el texto descargado.")
            else:
                print(f"  --> Error HTTP: {r.status_code}")
        except Exception as e:
            print(f"  --> Error en {url}: {e}")

    final_xml.append('</tv>')
    full_text = "\n".join(final_xml)

    # Guardar archivos en el repo
    with open("guia_completa.xml", "w", encoding="utf-8") as f:
        f.write(full_text)
    with gzip.open("guia_completa.xml.gz", "wt", encoding="utf-8") as f:
        f.write(full_text)
    
    print(f"\nPROCESO FINALIZADO. Archivo generado con {len(full_text)} caracteres.")

if __name__ == "__main__":
    main()


