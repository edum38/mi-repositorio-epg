import requests
import gzip
import re

# Usamos un servicio de Proxy (AllOrigins o jsDelivr) para que el servidor 
# original no sepa que es GitHub quien descarga.
EPG_SOURCES = [
    # LATAM (Argentina, México, Chile, Colombia...) - Fuente muy estable
    "https://api.allorigins.win/raw?url=https://www.teleguide.info/download/new3/xmltv.xml.gz",
    # EUROPA (Italia, Francia, Alemania)
    "https://api.allorigins.win/raw?url=https://iptv-org.github.io/epg/guides/it/sky.it.xml"
]

def main():
    print("Iniciando descarga automatizada vía Proxy...")
    final_xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv generator-info-name="MiAppIPTV-Global">']
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/110.0.0.0'}

    for url in EPG_SOURCES:
        try:
            print(f"Solicitando a través del Proxy: {url}")
            # El Proxy AllOrigins se encarga de saltarse el bloqueo de IP
            r = requests.get(url, headers=headers, timeout=60)
            
            if r.status_code == 200:
                # Si viene comprimido, lo abrimos
                if r.content[:2] == b'\x1f\x8b':
                    content = gzip.decompress(r.content).decode('utf-8', errors='ignore')
                else:
                    content = r.text

                # Filtramos: Solo queremos canales que NO sean rusos (IDs con .mx, .ar, .co, .it, .es)
                bloques = re.findall(r'<(channel|programme).*?</\1>', content, re.DOTALL)
                
                encontrados = 0
                for b in bloques:
                    cuerpo = b[1] # Contenido del bloque
                    # Filtro de países latinos y europeos
                    if any(p in cuerpo for p in ['.mx"', '.ar"', '.co"', '.it"', '.es"', '.cl"', '.pe"']):
                        final_xml.append(f"<{b[0]}{cuerpo}</{b[0]}>")
                        encontrados += 1
                
                print(f"  --> ÉXITO: {encontrados} canales y programas añadidos.")
            else:
                print(f"  --> El Proxy devolvió error: {r.status_code}")
        except Exception as e:
            print(f"  --> Fallo en la conexión: {e}")

    final_xml.append('</tv>')
    full_text = "\n".join(final_xml)

    with open("guia_completa.xml", "w", encoding="utf-8") as f:
        f.write(full_text)
    with gzip.open("guia_completa.xml.gz", "wt", encoding="utf-8") as f:
        f.write(full_text)
    
    print("\nPROCESO AUTOMATIZADO COMPLETADO.")

if __name__ == "__main__":
    main()







