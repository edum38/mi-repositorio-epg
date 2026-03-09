import requests
import gzip
import re

# Fuentes: La rusa (que funciona) + Una de España en servidor externo (no GitHub)
EPG_SOURCES = [
    "http://www.teleguide.info/download/new3/xmltv.xml.gz",
    "http://www.proyectotv.com/guia.xml.gz" 
]

def main():
    print("Iniciando aspiradora de canales (Filtro Internacional)...")
    final_xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv generator-info-name="MiAppIPTV">']
    headers = {'User-Agent': 'Mozilla/5.0'}

    for url in EPG_SOURCES:
        try:
            print(f"Conectando a: {url}")
            r = requests.get(url, headers=headers, timeout=60)
            if r.status_code == 200:
                print("  --> Descargado. Filtrando idiomas...")
                content = gzip.decompress(r.content).decode('utf-8', errors='ignore')
                
                # Extraemos canales y programas
                # FILTRO: Solo guardamos si tienen etiquetas de idioma español (es), italiano (it) o inglés (en)
                # O si el ID del canal contiene prefijos internacionales.
                bloques = re.findall(r'<(channel|programme).*?</\1>', content, re.DOTALL)
                
                encontrados = 0
                for b in bloques:
                    cuerpo = b[0] # El contenido del bloque
                    # Si el bloque contiene 'lang="es"' o 'lang="it"' o no parece tener letras rusas
                    if 'lang="es"' in cuerpo or 'lang="it"' in cuerpo or '.es"' in cuerpo or '.mx"' in cuerpo:
                        final_xml.append(f"<{b[0]}{cuerpo}</{b[0]}>")
                        encontrados += 1
                
                print(f"  --> ÉXITO: {encontrados} elementos no-rusos añadidos.")
        except Exception as e:
            print(f"  --> Error: {e}")

    final_xml.append('</tv>')
    resultado = "\n".join(final_xml)

    with open("guia_completa.xml", "w", encoding="utf-8") as f:
        f.write(resultado)
    with gzip.open("guia_completa.xml.gz", "wt", encoding="utf-8") as f:
        f.write(resultado)
    
    print(f"¡TERMINADO! Archivo filtrado generado.")

if __name__ == "__main__":
    main()







