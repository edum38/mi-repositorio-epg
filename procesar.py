import gzip
import re
from datetime import datetime, timedelta

DESFASE = -2
TRADUCCIONES = {
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

def main():
    print("Paso 2: Procesando y ajustando hora...")
    try:
        with gzip.open("original.xml.gz", "rb") as f:
            content = f.read().decode('utf-8', errors='ignore')
        
        final_xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv generator-info-name="MiApp-Espana">']
        
        # Filtro de canales e IDs
        ids_validos = set()
        canales = re.findall(r'<channel.*?</channel>', content, re.DOTALL)
        for c in canales:
            match_id = re.search(r'id="(.*?)"', c)
            if match_id:
                cid = match_id.group(1)
                for clave, nombre in TRADUCCIONES.items():
                    if clave.lower() in cid.lower():
                        c = re.sub(r'<display-name.*?>.*?</display-name>', f'<display-name>{nombre}</display-name>', c)
                        final_xml.append(c)
                        ids_validos.add(cid)
                        break

        # Filtro de programas y ajuste de hora
        programas = re.findall(r'<programme.*?</programme>', content, re.DOTALL)
        for p in programas:
            m_chan = re.search(r'channel="(.*?)"', p)
            if m_chan and m_chan.group(1) in ids_validos:
                # Ajuste de hora simple
                tiempos = re.findall(r'(\d{14})', p)
                for t in tiempos:
                    dt = datetime.strptime(t, "%Y%m%d%H%M%S") + timedelta(hours=DESFASE)
                    p = p.replace(t, dt.strftime("%Y%m%d%H%M%S"))
                p = re.sub(r'\+\d{4}', '+0100', p)
                final_xml.append(p)

        final_xml.append('</tv>')
        
        with open("guia_completa.xml", "w", encoding="utf-8") as f:
            f.write("\n".join(final_xml))
        print(f"Proceso finalizado. {len(ids_validos)} canales listos.")
        
    except Exception as e:
        print(f"Error en el paso 2: {e}")

if __name__ == "__main__":
    main()