import requests
import gzip
import time

# FUENTES QUE NO ESTÁN EN GITHUB (Para evitar el bloqueo)
EPG_SOURCES = [
    # ESPAÑA (Fuente alternativa muy estable)
    "https://raw.githubusercontent.com/davidmuma/EPG_dobleM/master/guia.xml", 
    # LATAM / MÉXICO (Fuente de respaldo en servidor externo)
    "https://webshare.cz/file/7q57v34n21/guia-latam.xml",
    # EUROPA / ITALIA (Fuente de teleguide, pero filtrada)
    "https://www.teleguide.info/download/new3/xmltv.xml.gz"
]

def main():
    print("Iniciando descarga desde fuentes externas (No-GitHub)...")
    final_xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv generator-info-name="MiAppIPTV">']
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    for url in EPG_SOURCES:
        try:
            print(f"Descargando: {url}")
            # Si la fuente es de GitHub (como la de España), intentamos un pequeño truco
            r = requests.get(url, headers=headers, timeout=45)
            
            if r.status_code == 200:
                if url.endswith(".gz") or r.content[:2] == b'\x1f\x8b':
                    content = gzip.decompress(r.content).decode('utf-8', errors='ignore')
                else:
                    content = r.content.decode('utf-8', errors='ignore')

                # Buscamos canales de ESPAÑA, MÉXICO, ITALIA, FRANCIA
                # Filtramos para no traer canales rusos si usamos la fuente de teleguide
                import re
                print("  --> Filtrando canales...")
                
                # Buscamos bloques que NO sean puramente cirílicos (rusos) o que tengan IDs conocidos
                bloques = re.findall(r'<(channel|programme).*?</\1>', content, re.DOTALL)
                
                encontrados = 0
                for b in re.finditer(r'<(channel|programme).*?</\1>', content, re.DOTALL):
                    bloque_texto = b.group(0)
                    # Si es la fuente rusa, solo guardamos lo que no parezca ruso (nombres internacionales)
                    if "teleguide" in url:
                        if 'lang="es"' in bloque_texto or 'lang="it"' in bloque_texto or 'lang="en"' in bloque_texto:
                            final_xml.append(bloque_texto)
                            encontrados += 1
                    else:
                        final_xml.append(bloque_texto)
                        encontrados += 1
                
                print(f"  --> OK: {encontrados} elementos añadidos.")
            else:
                print(f"  --> Error HTTP: {r.status_code}")
        except Exception as e:
            print(f"  --> Error en {url}: {e}")
        
        time.sleep(2)

    final_xml.append('</tv>')
    full_text = "\n".join(final_xml)

    with open("guia_completa.xml", "w", encoding="utf-8") as f:
        f.write(full_text)
    with gzip.open("guia_completa.xml.gz", "wt", encoding="utf-8") as f:
        f.write(full_text)
    
    print(f"\nProceso terminado. Archivo de {len(full_text)} caracteres.")

if __name__ == "__main__":
    main()





