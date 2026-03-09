import requests
import gzip

# Estas son las URLs de la API oficial de IPTV-org (Son las más estables)
EPG_SOURCES = [
    "https://iptv-org.github.io/epg/guides/es/movistarplus.es.xml", # España
    "https://iptv-org.github.io/epg/guides/it/sky.it.xml",           # Italia
    "https://iptv-org.github.io/epg/guides/mx/mi.tv.xml",           # México
    "https://iptv-org.github.io/epg/guides/ar/mi.tv.xml",           # Argentina
    "https://iptv-org.github.io/epg/guides/co/mi.tv.xml",           # Colombia
    "https://iptv-org.github.io/epg/guides/pe/mi.tv.xml",           # Perú
    "https://iptv-org.github.io/epg/guides/fr/programme-tv.net.xml", # Francia
    "https://iptv-org.github.io/epg/guides/de/tvtoday.de.xml",       # Alemania
    "https://iptv-org.github.io/epg/guides/uk/sky.com.xml",         # UK
    "https://iptv-org.github.io/epg/guides/br/meuguia.tv.xml"       # Brasil
]

def main():
    print("Iniciando descarga desde la API oficial...")
    
    # Creamos el archivo final manualmente para evitar errores de parseo
    # Empezamos con el encabezado XMLTV
    full_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<tv generator-info-name="MiAppIPTV">\n'
    
    headers = {'User-Agent': 'Mozilla/5.0'}

    for url in EPG_SOURCES:
        try:
            print(f"Descargando: {url}")
            # Usamos stream=True para manejar mejor archivos grandes
            response = requests.get(url, headers=headers, timeout=60)
            
            if response.status_code == 200:
                content = response.text
                
                # Extraemos lo que hay entre <tv> y </tv>
                # Esto es más rápido y evita problemas con la raíz del XML
                try:
                    start = content.find('<tv')
                    # Buscamos dónde termina la etiqueta de apertura del primer <tv...>
                    start = content.find('>', start) + 1
                    end = content.rfind('</tv>')
                    
                    if start > 0 and end > 0:
                        inner_content = content[start:end]
                        full_xml += inner_content
                        print(f"  --> OK: Datos añadidos correctamente.")
                    else:
                        print("  --> Error: Estructura XML no reconocida.")
                except:
                    print("  --> Error procesando el texto del XML.")
            else:
                print(f"  --> Error HTTP: {response.status_code}")
        except Exception as e:
            print(f"  --> Fallo en {url}: {e}")

    full_xml += '\n</tv>'

    # Guardar los resultados
    print("Guardando archivos...")
    with open("guia_completa.xml", "w", encoding="utf-8") as f:
        f.write(full_xml)
        
    with gzip.open("guia_completa.xml.gz", "wt", encoding="utf-8") as f:
        f.write(full_xml)
    
    print(f"¡PROCESO COMPLETADO! Tamaño del archivo: {len(full_xml)} bytes.")

if __name__ == "__main__":
    main()




