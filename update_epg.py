import requests
import gzip
import re
from datetime import datetime, timedelta

# La única fuente que GitHub no bloquea
URL_OPEN = "http://www.teleguide.info/download/new3/xmltv.xml.gz"

# Ajuste para España (Ahora mismo -2)
DESFASE = -2

# Diccionario de traducción
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

def main():
    print(f"Descargando de fuente rusa... Ajuste: {DESFASE}h")
    final_xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv generator-info-name="MiGuia-Espana">']
    
    try:
        r = requests.get(URL_OPEN, timeout=60)
        if r.status_code == 200:
            content = gzip.decompress(r.content).decode('utf-8', errors='ignore')
            
            # 1. Extraer Canales
            ids_validados = []
            canales = re.findall(r'<channel.*?</channel>', content, re.DOTALL)
            for c in canales:
                match_id = re.search(r'id="(.*?)"', c)
                if match_id:
                    cid = match_id.group(1)
                    for clave, nombre in TRADUCCIONES.items():
                        if clave.lower() in cid.lower():
                            # Limpieza de nombre
                            c = re.sub(r'<display-name.*?>.*?</display-name>', f'<display-name>{nombre}</display-name>', c)
                            final_xml.append(c)
                            ids_validados.append(cid)
                            break

            # 2. Extraer Programas y ajustar hora (Método Simple)
            programas = re.findall(r'<programme.*?</programme>', content, re.DOTALL)
            for p in programas:
                # Verificar si el canal nos interesa
                match_chan = re.search(r'channel="(.*?)"', p)
                if match_chan and match_chan.group(1) in ids_validados:
                    
                    # AJUSTE HORARIO SIMPLIFICADO
                    # Buscamos las fechas (ej: 20240310120000)
                    times = re.findall(r'(\d{14})', p)
                    for t in times:
                        try:
                            dt = datetime.strptime(t, "%Y%m%d%H%M%S")
                            dt_corr = dt + timedelta(hours=DESFASE)
                            p = p.replace(t, dt_corr.strftime("%Y%m%d%H%M%S"))
                        except:
                            continue
                    
                    # Forzamos la etiqueta de zona horaria a España (+0100)
                    p = re.sub(r'\+\d{4}', '+0100', p)
                    final_xml.append(p)

            print(f"¡ÉXITO! Canales procesados: {len(ids_validados)}")
        
    except Exception as e:
        print(f"Error en el proceso: {e}")

    final_xml.append('</tv>')
    resultado = "\n".join(final_xml)

    with open("guia_completa.xml", "w", encoding="utf-8") as f:
        f.write(resultado)
    with gzip.open("guia_completa.xml.gz", "wt", encoding="utf-8") as f:
        f.write(resultado)

if __name__ == "__main__":
    main()









