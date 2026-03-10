import requests
import gzip
import re

# FUENTES DE RESPALDO (Servidores que no bloquean a GitHub Actions)
EPG_SOURCES = [
    # LATAM (Fuente de GatoTV procesada por terceros)
    "https://raw.githubusercontent.com/fshvinc/EPG/main/guia.xml",
    # LATAM 2 (Alternativa México/Argentina/Chile)
    "https://raw.githubusercontent.com/clover-guia/epg/master/guia.xml",
    # EUROPA (Italia, Francia, etc.)
    "https://raw.githubusercontent.com/bitsr0/xmltv/master/guide.xml"
]

def main():
    print("Iniciando descarga de fuentes de respaldo...")
    final_xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv generator-info-name="MiGuia-Latam-Europa">']
    
    headers = {'User-Agent': 'Mozilla/5.0'}

    for url in EPG_SOURCES:
        try:
            print(f"Descargando: {url}")
            r = requests.get(url, headers=headers, timeout=60)
            
            if r.status_code == 200:
                # Detección de GZIP
                if r.content[:2] == b'\x1f\x8b':
                    content = gzip.decompress(r.content).decode('utf-8', errors='ignore')
                else:
                    content = r.text

                # Buscamos los bloques de canales y programas
                canales = re.findall(r'<channel.*?</channel>', content, re.DOTALL)
                programas = re.findall(r'<programme.*?</programme>', content, re.DOTALL)
                
                if canales:
                    final_xml.extend(canales)
                    final_xml.extend(programas)
                    print(f"  --> OK: {len(canales)} canales añadidos.")
                else:
                    print("  --> No se encontraron canales en este archivo.")
            else:
                print(f"  --> Error HTTP: {r.status_code}")
        except Exception as e:
            print(f"  --> Fallo en {url}: {e}")

    final_xml.append('</tv>')
    full_text = "\n".join(final_xml)

    with open("guia_completa.xml", "w", encoding="utf-8") as f:
        f.write(full_text)
    with gzip.open("guia_completa.xml.gz", "wt", encoding="utf-8") as f:
        f.write(full_text)
    
    print(f"\nProceso terminado. Caracteres totales: {len(full_text)}")

if __name__ == "__main__":
    main()







