import requests
import gzip
import xml.etree.ElementTree as ET

# Lista maestra de fuentes para tu App IPTV
EPG_SOURCES = [
    "https://iptv-org.github.io/epg/guides/es/movistarplus.es.xml", # España
    "https://iptv-org.github.io/epg/guides/it/sky.it.xml",           # Italia (NUEVO)
    "https://iptv-org.github.io/epg/guides/fr/programme-tv.net.xml", # Francia
    "https://iptv-org.github.io/epg/guides/de/tvtoday.de.xml",       # Alemania
    "https://iptv-org.github.io/epg/guides/uk/sky.com.xml",         # Inglaterra (UK)
    "https://iptv-org.github.io/epg/guides/br/meuguia.tv.xml",      # Brasil
    "https://iptv-org.github.io/epg/guides/ar/mi.tv.xml",          # Argentina
    "https://iptv-org.github.io/epg/guides/pe/mi.tv.xml",          # Perú
    "https://iptv-org.github.io/epg/guides/co/mi.tv.xml",          # Colombia
    "https://iptv-org.github.io/epg/guides/mx/mi.tv.xml"           # México
]

def main():
    # Nodo raíz del XMLTV
    root = ET.Element("tv", {"generator-info-name": "MiAppIPTV-Global-EPG"})
    
    for url in EPG_SOURCES:
        try:
            print(f"Obteniendo datos de: {url}")
            r = requests.get(url, timeout=45)
            if r.status_code == 200:
                # Parseamos el contenido XML
                tree = ET.fromstring(r.content)
                # Extraemos canales y programas
                for item in tree:
                    if item.tag in ["channel", "programme"]:
                        root.append(item)
            else:
                print(f"Error {r.status_code} en {url}")
        except Exception as e:
            print(f"Fallo crítico en {url}: {e}")

    # Convertir a bytes con declaración XML
    xml_output = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    # 1. Guardar XML normal (para pruebas rápidas)
    with open("guia_completa.xml", "wb") as f:
        f.write(xml_output)

    # 2. Guardar XML Comprimido (el que usará tu App)
    with gzip.open("guia_completa.xml.gz", "wb") as f:
        f.write(xml_output)
    
    print("¡Proceso finalizado! EPG global generada.")

if __name__ == "__main__":
    main()
