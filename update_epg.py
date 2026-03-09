import requests
import gzip
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
    # Iniciamos el archivo con la cabecera obligatoria de XMLTV
    final_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    final_content += '<tv generator-info-name="MiAppIPTV-Global-EPG">\n'

    headers = {'User-Agent': 'Mozilla/5.0'}

    for url in EPG_SOURCES:
        try:
            print(f"Descargando: {url}")
            r = requests.get(url, headers=headers, timeout=30)
            if r.status_code == 200:
                text = r.text

                # Extraemos todos los bloques <channel ... </channel>
                channels = re.findall(r'<channel.*?</channel>', text, re.DOTALL)
                # Extraemos todos los bloques <programme ... </programme>
                programmes = re.findall(r'<programme.*?</programme>', text, re.DOTALL)

                for c in channels:
                    final_content += c + "\n"
                for p in programmes:
                    final_content += p + "\n"

                print(f"  --> OK: {len(channels)} canales y {len(programmes)} programas añadidos.")
            else:
                print(f"  --> Error HTTP {r.status_code}")
        except Exception as e:
            print(f"  --> Error en {url}: {e}")

    # Cerramos la etiqueta raíz
    final_content += '</tv>'

    # Guardar en XML normal
    with open("guia_completa.xml", "w", encoding="utf-8") as f:
        f.write(final_content)

    # Guardar en GZ comprimido
    with gzip.open("guia_completa.xml.gz", "wt", encoding="utf-8") as f:
        f.write(final_content)

    print("\nPROCESO FINALIZADO CON ÉXITO.")

if __name__ == "__main__":
    main()


