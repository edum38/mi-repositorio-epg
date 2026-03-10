import requests
import gzip
import re
from datetime import datetime, timedelta

URL_OPEN = "http://www.teleguide.info/download/new3/xmltv.xml.gz"

# Ajuste para España (Moscú UTC+3 -> España UTC+1 = -2 horas)
DESFASE = -2

TRADUCCIONES = {
    "Discovery": "Discovery Channel",
    "Disney": "Disney Channel",
    "Animal Planet": "Animal Planet",
    "HBO": "HBO",
    "MTV": "MTV España",
    "CNN": "CNN International",
    "Eurosport": "Eurosport",
    "National Geographic": "Nat Geo",
    "Nickelodeon": "Nickelodeon",
    "History": "Historia",
    "FOX": "FOX España",
    "AXN": "AXN España"
}

def forzar_hora(texto, horas):
    """Busca cualquier bloque de 14 números y le resta las horas."""
    def reemplazar(match):
        fecha_original = match.group(1)
        try:
            # Convertimos a fecha, restamos y devolvemos texto
            dt = datetime.strptime(fecha_original, "%Y%m%d%H%M%S")
            dt_nueva = dt + timedelta(hours=horas)
            return dt_nueva.strftime("%Y%m%d%H%M%S")
        except:
            return fecha_original
    
    # Busca 14 dígitos seguidos (el formato de fecha de XMLTV)
    return re.sub(r'(\d{14})', reemplazar, texto)

def main():
    print("Iniciando descarga...")
    final_xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv generator-info-name="MiApp-Espana-Fija">']
    
    try:
        r = requests.get(URL_OPEN, timeout=60)
        if r.status_code == 200:
            content = gzip.decompress(r.content).decode('utf-8', errors='ignore')
            
            canales = re.findall(r'<channel.*?</channel>', content, re.DOTALL)
            programas = re.findall(r'<programme.*?</programme>', content, re.DOTALL)
            
            ids_activos = set()

            # 1. Procesar Canales
            for c in canales:
                m = re.search(r'id="(.*?)"', c)
                if m:
                    cid = m.group(1)
                    for clave, nombre in TRADUCCIONES.items():
                        if clave.lower() in cid.lower():
                            c = re.sub(r'<display-name.*?>.*?</display-name>', f'<display-name>{nombre}</display-name>', c)
                            final_xml.append(c)
                            ids_activos.add(cid)
                            break

            # 2. Procesar Programas con Cirugía Horaria
            for p in programas:
                m_chan = re.search(r'channel="(.*?)"', p)
                if m_chan and m_chan.group(1) in ids_activos:
                    # Aplicamos el cambio de hora directamente al texto del programa
                    p_corregido = forzar_hora(p, DESFASE)
                    # Forzamos que la App vea el offset de España (+0100)
                    p_corregido = re.sub(r'\+\d{4}', '+0100', p_corregido)
                    final_xml.append(p_corregido)

            print(f"Procesados {len(ids_activos)} canales con hora ajustada.")
        
    except Exception as e:
        print(f"Error: {e}")

    final_xml.append('</tv>')
    
    # Guardar
    with open("guia_completa.xml", "w", encoding="utf-8") as f:
        f.write("\n".join(final_xml))
    with gzip.open("guia_completa.xml.gz", "wt", encoding="utf-8") as f:
        f.write("\n".join(final_xml))

if __name__ == "__main__":
    main()









