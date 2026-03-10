import requests
import gzip
import re
import os
from datetime import datetime, timedelta

def procesar_datos(raw_content):
    """Función aislada para editar el XML sin romper la descarga."""
    desfase = -2
    traducciones = {
        "Discovery": "Discovery Channel",
        "Disney": "Disney Channel",
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
    
    try:
        final_xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv generator-info-name="MiApp-Espana">']
        ids_validos = set()
        
        # 1. Canales
        canales = re.findall(r'<channel.*?</channel>', raw_content, re.DOTALL)
        for c in canales:
            m = re.search(r'id="(.*?)"', c)
            if m:
                cid = m.group(1)
                for clave, nombre in traducciones.items():
                    if clave.lower() in cid.lower():
                        c = re.sub(r'<display-name.*?>.*?</display-name>', f'<display-name>{nombre}</display-name>', c)
                        final_xml.append(c)
                        ids_validos.add(cid)
                        break

        # 2. Programas
        programas = re.findall(r'<programme.*?</programme>', raw_content, re.DOTALL)
        for p in programas:
            m_chan = re.search(r'channel="(.*?)"', p)
            if m_chan and m_chan.group(1) in ids_validos:
                # Cambio de hora
                tiempos = re.findall(r'(\d{14})', p)
                for t in tiempos:
                    dt = datetime.strptime(t, "%Y%m%d%H%M%S") + timedelta(hours=desfase)
                    p = p.replace(t, dt.strftime("%Y%m%d%H%M%S"))
                p = re.sub(r'\+\d{4}', '+0100', p)
                final_xml.append(p)

        final_xml.append('</tv>')
        return "\n".join(final_xml)
    except Exception as e:
        print(f"Error en procesamiento: {e}")
        return raw_content # Si falla, devuelve el original para no dar 0

def main():
    url = "http://www.teleguide.info/download/new3/xmltv.xml.gz"
    print("Iniciando descarga...")
    
    try:
        r = requests.get(url, timeout=60)
        if r.status_code == 200:
            # Descomprimir
            raw = gzip.decompress(r.content).decode('utf-8', errors='ignore')
            print("Descarga completa. Editando...")
            
            # Procesar
            resultado = procesar_datos(raw)
            
            # Guardar ambos formatos
            with open("guia_completa.xml", "w", encoding="utf-8") as f:
                f.write(resultado)
            with gzip.open("guia_completa.xml.gz", "wt", encoding="utf-8") as f:
                f.write(resultado)
            print("Archivos guardados correctamente.")
        else:
            print(f"Error servidor: {r.status_code}")
    except Exception as e:
        print(f"Error crítico: {e}")

if __name__ == "__main__":
    main()









