import requests
import gzip
import xml.etree.ElementTree as ET
import re

EPG_SOURCES = [
    "https://iptv-org.github.io/epg/guides/es/movistarplus.es.xml",
    "https://iptv-org.github.io/epg/guides/it/sky.it.xml",
    "https://iptv-org.github.io/epg/guides/fr/programme-tv.net.xml",
    "https://iptv-org.github.io/epg/guides/de/tvtoday.de.xml",
    "https://iptv-org.github.io/epg/guides/uk/sky.com.xml",
    "https://iptv-org.github.io/epg/guides/br/meuguia.tv.xml",
    "https://iptv-org.github.io/epg/guides/ar/mi.tv.xml",
    "https://iptv-org.github.io/epg/guides/pe/mi.tv.xml",
    "https://iptv-org.github.io/epg/guides/co/mi.tv.xml",
    "https://iptv-org.github.io/epg/guides/mx/mi.tv.xml"
]

def main():
    root = ET.Element("tv", {"generator-info-name": "MiAppIPTV-Global-EPG"})
    headers = {'User-Agent': 'Mozilla/5.0'}

    for url in EPG_SOURCES:
        try:
            print(f"Descargando: {url}")
            r = requests.get(url, headers=headers, timeout=30)
            if r.status_code == 200:
                # ELIMINAR NAMESPACES: Esto es clave si el XML viene con prefijos
                # Quitamos xmlns="..." para que el buscador encuentre 'channel' y 'programme'
                xml_content = re.sub(r'\sxmlns="[^"]+"', '', r.text, count=1)

                try:
                    tree = ET.fromstring(xml_content)
                    items_added = 0
                    for item in tree:
                        if item.tag in ["channel", "programme"]:
                            root.append(item)
                            items_added += 1
                    print(f"  --> Éxito: {items_added} elementos añadidos.")
                except Exception as parse_error:
                    print(f"  --> Error al procesar XML de {url}: {parse_error}")
            else:
                print(f"  --> Error HTTP {r.status_code}")
        except Exception as e:
            print(f"  --> Error de conexión en {url}: {e}")

    # Guardar resultados
    final_xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    with open("guia_completa.xml", "wb") as f:
        f.write(final_xml)

    with gzip.open("guia_completa.xml.gz", "wb") as f:
        f.write(final_xml)

    print("\nPROCESO COMPLETADO.")

if __name__ == "__main__":
    main()


