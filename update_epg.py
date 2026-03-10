import requests
import gzip
import re

# FUENTES DE OPEN EPG Y RESPALDO (Servidores de alta disponibilidad)
EPG_SOURCES = [
    # LATAM (México, Argentina, Colombia - Open EPG Mirror)
    "https://openepg.org/xmltv/latin.xml.gz",
    # ESPAÑA / EUROPA (Open EPG Mirror)
    "https://openepg.org/xmltv/spain.xml.gz",
    "https://openepg.org/xmltv/italy.xml.gz",
    # Fuente de respaldo de GatoTV (Servidor externo)
    "http://www.xmltv.co/xmltv/guides/mexico.xml.gz"
]

def main():
    print("Iniciando descarga desde Open EPG...")
    final_xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv generator-info-name="MiAppIPTV-OpenEPG">']
    
    # Cabeceras para que parezca una descarga de navegador real
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }

    for url in EPG_SOURCES:
        try:
            print(f"Conectando a: {url}")
            # Quitamos la verificación de SSL por si los certificados de Open EPG fallan
            r = requests.get(url, headers=headers, timeout=60, verify=False)
            
            if r.status_code == 200:
                print(f"  --> Descargado ({len(r.content)} bytes). Procesando...")
                
                # Descomprimir (Open EPG siempre manda .gz)
                try:
                    content = gzip.decompress(r.content).decode('utf-8', errors='ignore')
                except:
                    content = r.text

                # Extraer canales y programas
                canales = re.findall(r'<channel.*?</channel>', content, re.DOTALL)
                programas = re.findall(r'<programme.*?</programme>', content, re.DOTALL)
                
                if canales:
                    final_xml.extend(canales)
                    final_xml.extend(programas)
                    print(f"  --> OK: {len(canales)} canales añadidos.")
                else:
                    # Si el regex falla, intentamos capturar todo lo que esté dentro de <tv>
                    tv_content = re.search(r'<tv.*?>(.*?)</tv>', content, re.DOTALL | re.IGNORECASE)
                    if tv_content:
                        final_xml.append(tv_content.group(1))
                        print("  --> OK: Contenido masivo añadido.")
                    else:
                        print("  --> Error: El archivo bajó pero no tiene formato XMLTV.")
            else:
                print(f"  --> Error HTTP: {r.status_code}")
        except Exception as e:
            print(f"  --> Fallo en la conexión: {e}")

    final_xml.append('</tv>')
    full_text = "\n".join(final_xml)

    # Guardar archivos
    with open("guia_completa.xml", "w", encoding="utf-8") as f:
        f.write(full_text)
    with gzip.open("guia_completa.xml.gz", "wt", encoding="utf-8") as f:
        f.write(full_text)
    
    print(f"\nProceso terminado. Caracteres totales guardados: {len(full_text)}")

if __name__ == "__main__":
    main()








