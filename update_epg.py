import requests
import gzip
import re
from datetime import datetime, timedelta

# La fuente que sabemos que GitHub NO bloquea
URL_OPEN = "http://www.teleguide.info/download/new3/xmltv.xml.gz"

# Ajuste manual para España (Invierno: -2, Verano: -1)
# Como estamos en marzo, usamos -2
DESFASE = -2

# Diccionario de traducción (IDs que vienen en el XML ruso)
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
    "FOX": "FOX",
    "AXN": "AXN"
}

def ajustar_hora(xml_linea, horas):
    # Esta función busca la hora y le resta las horas de desfase
    def cambiar(match):
        prefix = match.group(1) # start=" o stop="
        fecha = match.group(2) # 20240520103000
        try:
            dt = datetime.strptime(fecha, "%Y%m%d%H%M%S")
            dt = dt + timedelta(hours=horas)
            return f'{prefix}="{dt.strftime("%Y%m%d%H%M%S")} +0100"'
        except:
            return match.group(0)
    return re.sub(r'(start|stop)="(\d{14})\s\+\d{4}"', cambiar, xml_linea)

def main():
    print(f"Conectando a fuente rusa... Ajuste España: {DESFASE}h")
    final_xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv generator-info-name="MiGuia-Espana">']
    
    try:
        r = requests.get(URL_OPEN, timeout=60)
        if r.status_code == 200:
            content = gzip.decompress(r.content).decode('utf-8', errors='ignore')
            
            # Cortamos el archivo en trozos de canales y programas
            canales = re.findall(r'<channel.*?</channel>', content, re.DOTALL)
            programas = re.findall(r'<programme.*?</programme>', content, re.DOTALL)
            
            ids_validados = set()

            # 1. Filtramos y traducimos canales
            for c in canales:
                match_id = re.search(r'id="(.*?)"', c)
                if match_id:
                    cid = match_id.group(1)
                    # Buscamos si el ID ruso contiene alguna de nuestras palabras clave
                    for clave, nombre_limpio in TRADUCCIONES.items():
                        if clave.lower() in cid.lower():
                            # Cambiamos el nombre cirílico por el nuestro
                            c = re.sub(r'<display-name.*?>.*?</display-name>', f'<display-name>{nombre_limpio}</display-name>', c)
                            final_xml.append(c)
                            ids_validados.add(cid)
                            break

            # 2. Filtramos programas y ajustamos su hora
            for p in programas:
                match_chan = re.search(r'channel="(.*?)"', p)
                if match_chan and match_chan.group(1) in ids_validados:
                    # Aplicamos la resta de horas
                    p_nueva_hora = ajustar_hora(p, DESFASE)
                    final_xml.append(p_nueva_hora)

            print(f"¡ÉXITO! Se han procesado {len(ids_validados)} canales para España.")
        
    except Exception as e:
        print(f"Error: {e}")

    final_xml.append('</tv>')
    resultado = "\n".join(final_xml)

    with open("guia_completa.xml", "w", encoding="utf-8") as f:
        f.write(resultado)
    with gzip.open("guia_completa.xml.gz", "wt", encoding="utf-8") as f:
        f.write(resultado)

if __name__ == "__main__":
    main()








