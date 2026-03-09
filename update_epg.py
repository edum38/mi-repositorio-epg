import requests
import gzip
import time # Para las pausas

# Direcciones individuales (las más ligeras)
EPG_SOURCES = [
    "https://iptv-org.github.io/epg/guides/es/movistarplus.es.xml",
    "https://iptv-org.github.io/epg/guides/it/sky.it.xml",
    "https://iptv-org.github.io/epg/guides/mx/mi.tv.xml",
    "https://iptv-org.github.io/epg/guides/ar/mi.tv.xml",
    "https://iptv-org.github.io/epg/guides/co/mi.tv.xml",
    "https://iptv-org.github.io/epg/guides/pe/mi.tv.xml",
    "https://iptv-org.github.io/epg/guides/br/meuguia.tv.xml",
    "https://iptv-org.github.io/epg/guides/fr/programme-tv.net.xml"
]

def main():
    print("Iniciando descarga individual con pausas de seguridad...")
    
    # Encabezado manual para evitar fallos de memoria con objetos grandes
    final_xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv generator-info-name="MiAppIPTV">']
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/110.0.0.0'}

    for url in EPG_SOURCES:
        try:
            print(f"Descargando: {url} ...")
            r = requests.get(url, headers=headers, timeout=30)
            
            if r.status_code == 200:
                text = r.text
                # Extraemos el contenido quitando las etiquetas <tv> de cada archivo
                start = text.find('>') + 1
                tv_open = text.find('<tv', start)
                content_start = text.find('>', tv_open) + 1
                content_end = text.rfind('</tv>')
                
                if content_start > 0 and content_end > 0:
                    final_xml_parts.append(text[content_start:content_end])
                    print(f"  --> OK: Datos añadidos.")
                else:
                    print("  --> Error: Formato XML no válido.")
            else:
                print(f"  --> Falló: Código {r.status_code}")
            
            # EL TRUCO: Esperar 5 segundos antes de la siguiente petición
            print("  --> Esperando 5 segundos para evitar bloqueo...")
            time.sleep(5)
            
        except Exception as e:
            print(f"  --> Error en {url}: {e}")

    final_xml_parts.append('</tv>')
    full_xml = "\n".join(final_xml_parts)

    # Guardar
    with open("guia_completa.xml", "w", encoding="utf-8") as f:
        f.write(full_xml)
    with gzip.open("guia_completa.xml.gz", "wt", encoding="utf-8") as f:
        f.write(full_xml)
    
    print(f"¡TERMINADO! Archivo generado con {len(full_xml)} caracteres.")

if __name__ == "__main__":
    main()





