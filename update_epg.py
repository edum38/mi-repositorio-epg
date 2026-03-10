import requests
import gzip
import re
from datetime import datetime, timedelta
import time

# Fuente permitida por GitHub
URL_OPEN = "http://www.teleguide.info/download/new3/xmltv.xml.gz"

# 1. DICCIONARIO DE TRADUCCIÓN (IDs de la fuente rusa -> Nombres en España)
TRADUCCIONES = {
    "Discovery": "Discovery Channel",
    "Disney": "Disney Channel",
    "Disney Junior": "Disney Junior",
    "Animal Planet": "Animal Planet",
    "HBO": "HBO España",
    "MTV": "MTV España",
    "CNN": "CNN International",
    "Eurosport 1": "Eurosport 1",
    "Eurosport 2": "Eurosport 2",
    "National Geographic": "National Geographic",
    "Nat Geo Wild": "Nat Geo Wild",
    "Nickelodeon": "Nickelodeon",
    "Nick Jr": "Nick Jr",
    "History": "Canal Historia",
    "FOX": "FOX España",
    "AXN": "AXN",
    "TCM": "TCM",
    "Cartoon Network": "Cartoon Network"
}

def obtener_desplazamiento_espana():
    """Calcula automáticamente el desfase entre Moscú (UTC+3) y España."""
    # Moscú es UTC+3 fijo
    # España es UTC+1 (invierno) o UTC+2 (verano)
    ahora = datetime.now()
    # Determinar si es horario de verano en España (Marzo a Octubre aprox)
    # Una forma simple es usar time.localtime() que detecta el DST del sistema
    es_verano = time.localtime().tm_isdst > 0
    utc_espana = 2 if es_verano else 1
    
    # Diferencia: España - Moscú -> (2 - 3) = -1 o (1 - 3) = -2
    return utc_espana - 3

def ajustar_hora(xml_string, horas_desfase):
    def shift_time(match):
        tag = match.group(1) # start o stop
        time_str = match.group(2) # YYYYMMDDHHMMSS
        try:
            dt = datetime.strptime(time_str, "%Y%m%d%H%M%S")
            dt_ajustada = dt + timedelta(hours=horas_desfase)
            # Devolvemos con el offset +0100 o +0200 visualmente para la App
            offset = "+0200" if horas_desfase == -1 else "+0100"
            return f'{tag}="{dt_ajustada.strftime("%Y%m%d%H%M%S")} {offset}"'
        except:
            return match.group(0)

    # Regex para capturar fechas en atributos start o stop
    return re.sub(r'(start|stop)="(\d{14})\s\+\d{4}"', shift_time, xml_string)

def main():
    desfase = obtener_desplazamiento_espana()
    print(f"Detectado horario España. Ajuste respecto a Moscú: {desfase} horas.")
    
    final_xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv generator-info-name="MiGuia-Espana-Auto">']
    
    try:
        r = requests.get(URL_OPEN, timeout=60)
        if r.status_code == 200:
            content = gzip.decompress(r.content).decode('utf-8', errors='ignore')
            
            canales = re.findall(r'<channel.*?</channel>', content, re.DOTALL)
            programas = re.findall(r'<programme.*?</programme>', content, re.DOTALL)
            
            ids_interes = set()
            
            # Procesar y Traducir Canales
            for c in canales:
                match_id = re.search(r'id="(.*?)"', c)
                if match_id:
                    cid = match_id.group(1)
                    for clave, nombre_real in TRADUCCIONES.items():
                        if clave.lower() in cid.lower():
                            c = re.sub(r'<display-name.*?>.*?</display-name>', f'<display-name>{nombre_real}</display-name>', c)
                            final_xml.append(c)
                            ids_interes.add(cid)
                            break

            # Procesar y Sincronizar Programas
            for p in programas:
                match_chan = re.search(r'channel="(.*?)"', p)
                if match_chan and match_chan.group(1) in ids_interes:
                    p_corregido = ajustar_hora(p, desfase)
                    final_xml.append(p_corregido)

            print(f"Proceso completado: {len(ids_interes)} canales sincronizados con hora de España.")
            
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








