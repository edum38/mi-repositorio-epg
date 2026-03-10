import requests
import gzip
import re

# FUENTES DE ALTA DISPONIBILIDAD (No bloquean a GitHub Actions)
EPG_SOURCES = [
    # GatoTV (Latam: México, Argentina, Colombia...)
    "https://raw.githubusercontent.com/HelmerLuzo/GatoTV/main/epg.xml.gz",
    # Europa Mirror (Italia, Francia, Alemania) - Servidor de respaldo
    "http://www.xmltv.co/xmltv/guides/italy.xml.gz",
    "http://www.xmltv.co/xmltv/guides/france.xml.gz"
]

def main():
    print("Iniciando fusión GatoTV + Europa...")
    final_xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv generator-info-name="MiAppIPTV-GatoTV">']
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    for url in EPG_SOURCES:
        try:
            print(f"Descargando: {url}")
            r = requests.get(url, headers=headers, timeout=60)
            
            if r.status_code == 200:
                # Descomprimir si es necesario
                if url.endswith(".gz") or r.content[:2] == b'\x1f\x8b':
                    print("  --> Descomprimiendo archivo GZ...")
                    content = gzip.decompress(r.content).decode('utf-8', errors='ignore')
                else:
                    content = r.text

                # Extraer bloques (canales y programas)
                # Buscamos todo lo que esté dentro de las etiquetas <tv>
                match = re.search(r'<tv.*?>(.*?)</tv>', content, re.DOTALL | re.IGNORECASE)
                if match:
                    inner_data = match.group(1)
                    final_xml.append(inner_data)
                    # Contamos canales para el log
                    canales = len(re.findall(r'<channel', inner_data))
                    print(f"  --> ÉXITO: {canales} canales añadidos de esta fuente.")
                else:
                    print("  --> Error: No se encontró estructura <tv>.")
            else:
                print(f"  --> Error HTTP {r.status_code}")
        except Exception as e:
            print(f"  --> Error crítico: {e}")

    final_xml.append('</tv>')
    full_text = "\n".join(final_xml)

    # Guardar localmente (el archivo YAML se encargará del resto)
    with open("guia_completa.xml", "w", encoding="utf-8") as f:
        f.write(full_text)
    
    with gzip.open("guia_completa.xml.gz", "wt", encoding="utf-8") as f:
        f.write(full_text)
    
    print(f"\n¡LISTO! Archivo generado con {len(full_text)} caracteres.")

if __name__ == "__main__":
    main()







