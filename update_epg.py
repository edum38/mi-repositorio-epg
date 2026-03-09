import requests
import gzip
import re

# FUENTES QUE NO SON DE GITHUB (Para saltar el bloqueo total)
EPG_SOURCES = [
    # Fuente 1: OSDN (Servidor independiente - Muy estable)
    "https://osdn.net/projects/xmltv/storage/xmltv.xml.gz",
    # Fuente 2: Teleguide (La que te funcionó, pero filtrada para que no sea solo rusa)
    "https://www.teleguide.info/download/new3/xmltv.xml.gz",
    # Fuente 3: Servidor de respaldo alternativo (Latam/España)
    "http://www.proyectotv.com/guia.xml.gz"
]

def main():
    print("Iniciando descarga desde servidores independientes (No-GitHub)...")
    final_xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv generator-info-name="MiAppIPTV">']
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    for url in EPG_SOURCES:
        try:
            print(f"Conectando a: {url}")
            r = requests.get(url, headers=headers, timeout=60)
            
            if r.status_code == 200:
                print(f"  --> Descargado. Procesando...")
                # Descomprimir si es GZ
                if url.endswith(".gz") or r.content[:2] == b'\x1f\x8b':
                    content = gzip.decompress(r.content).decode('utf-8', errors='ignore')
                else:
                    content = r.content.decode('utf-8', errors='ignore')

                # Buscamos canales de España, México, Italia, etc.
                # Filtro: Buscamos IDs que contengan .es, .mx, .it, .ar, .co o lenguaje español/italiano
                encontrados = 0
                # Extraer bloques de canales y programas
                bloques = re.findall(r'<(channel|programme).*?</\1>', content, re.DOTALL | re.IGNORECASE)
                
                for b in bloques:
                    texto_bloque = b[0] # El contenido del regex
                    # Solo guardamos si es de nuestros países o tiene idioma latino/europeo
                    if any(p in texto_bloque for p in ['.es"', '.mx"', '.it"', '.ar"', '.co"', 'lang="es"', 'lang="it"']):
                        final_xml.append(f"<{b[0]}{texto_bloque}</{b[0]}>")
                        encontrados += 1
                
                print(f"  --> ÉXITO: {encontrados} elementos de interés añadidos.")
            else:
                print(f"  --> Error de servidor: {r.status_code}")
        except Exception as e:
            print(f"  --> El servidor no respondió: {e}")

    final_xml.append('</tv>')
    full_text = "\n".join(final_xml)

    with open("guia_completa.xml", "w", encoding="utf-8") as f:
        f.write(full_text)
    with gzip.open("guia_completa.xml.gz", "wt", encoding="utf-8") as f:
        f.write(full_text)
    
    print(f"\nProceso terminado. Archivo final creado.")

if __name__ == "__main__":
    main()





