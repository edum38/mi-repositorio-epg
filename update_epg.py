import requests
import gzip
import xml.etree.ElementTree as ET

# Lista de fuentes
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
    # Creamos el nodo raíz
    root = ET.Element("tv", {"generator-info-name": "MiAppIPTV-Global-EPG"})

    # Cabecera para engañar a servidores que bloquean scripts
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    count_channels = 0
    count_progs = 0

    for url in EPG_SOURCES:
        try:
            print(f"Intentando descargar: {url}")
            r = requests.get(url, headers=headers, timeout=60)

            if r.status_code == 200:
                # Usamos fromstring directamente sobre el contenido
                tree = ET.fromstring(r.content)

                # Buscamos elementos
                found_in_this_url = 0
                for item in tree:
                    if item.tag in ["channel", "programme"]:
                        root.append(item)
                        found_in_this_url += 1
                        if item.tag == "channel": count_channels += 1
                        if item.tag == "programme": count_progs += 1

                print(f" OK: Se encontraron {found_in_this_url} elementos.")
            else:
                print(f" ERROR: Código de estado {r.status_code}")
        except Exception as e:
            print(f" FALLO CRÍTICO en {url}: {e}")

    print(f"\n--- RESUMEN FINAL ---")
    print(f"Canales totales: {count_channels}")
    print(f"Programas totales: {count_progs}")

    # Guardar archivos
    xml_data = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    with open("guia_completa.xml", "wb") as f:
        f.write(xml_data)

    with gzip.open("guia_completa.xml.gz", "wb") as f:
        f.write(xml_data)

if __name__ == "__main__":
    main()

