import requests
import gzip
import re

# FUENTES REGIONALES (Fuera de los bloqueos estándar)
EPG_SOURCES = [
    # LATAM MIX (México, Argentina, Colombia, etc.)
    "https://iptv-org.github.io/epg/guides/mx/mi.tv.xml",
    "https://iptv-org.github.io/epg/guides/ar/mi.tv.xml",
    # EUROPA MIX (Italia, Francia, Alemania)
    "https://iptv-org.github.io/epg/guides/it/sky.it.xml",
    "https://iptv-org.github.io/epg/guides/fr/programme-tv.net.xml"
]

def main():
    print("Iniciando descarga de fuentes regionales...")
    # Encabezado XMLTV
    final_xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv generator-info-name="MiAppIPTV-Regional">']
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    for url in EPG_SOURCES:
        try:
            print(f"Descargando: {url}")
            # Usamos un timeout largo por si el servidor está saturado
            r = requests.get(url, headers=headers, timeout=45)
            
            if r.status_code == 200:
                content = r.text
                
                # Extraemos canales y programas usando una técnica de recorte limpia
                # Buscamos todo lo que esté entre el primer <channel y el último </programme>
                try:
                    start_idx = content.find('<channel')
                    end_idx = content.rfind('</programme>') + 12
                    
                    if start_idx != -1 and end_idx != -1:
                        data = content[start_idx:end_idx]
                        final_xml.append(data)
                        print(f"  --> ÉXITO: Datos de {url.split('/')[-2].upper()} añadidos.")
                    else:
                        print("  --> No se encontró estructura XMLTV válida.")
                except:
                    print("  --> Error procesando el texto.")
            else:
                print(f"  --> Error HTTP {r.status_code}")
                
        except Exception as e:
            print(f"  --> Error de conexión: {e}")

    final_xml.append('</tv>')
    full_text = "\n".join(final_xml)

    # Guardar archivos
    with open("guia_completa.xml", "w", encoding="utf-8") as f:
        f.write(full_text)
    with gzip.open("guia_completa.xml.gz", "wt", encoding="utf-8") as f:
        f.write(full_text)
    
    print(f"\nProceso terminado. Archivo listo para tu aplicación.")

if __name__ == "__main__":
    main()








