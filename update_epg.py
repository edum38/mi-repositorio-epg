import requests
import gzip
import re
from datetime import datetime, timedelta

# Configuración
URL_OPEN = "http://www.teleguide.info/download/new3/xmltv.xml.gz"
DESFASE = -2

# Diccionario de mapeo EXACTO para evitar traducciones locas
# Formato: "ID_Ruso": "Nombre_Espanol"
TRADUCCIONES = {
    "discovery": "Discovery Channel",
    "disney": "Disney Channel",
    "hbo": "HBO",
    "mtv": "MTV España",
    "cnn": "CNN International",
    "eurosport": "Eurosport",
    "nat_geo": "National Geographic",
    "nickelodeon": "Nickelodeon",
    "fox": "FOX",
    "axn": "AXN",
    "history": "Historia"
}

def limpiar_xml(texto):
    # Elimina el atributo lang="XX" de cualquier etiqueta
    texto = re.sub(r'\slang=".*?"', '', texto)
    return texto

def ajustar_hora(match):
    t = match.group(1)
    try:
        dt = datetime.strptime(t, "%Y%m%d%H%M%S") + timedelta(hours=DESFASE)
        return dt.strftime("%Y%m%d%H%M%S")
    except:
        return t

def main():
    print("Iniciando proceso...")
    try:
        r = requests.get(URL_OPEN, timeout=30)
        if r.status_code != 200: return
        
        content = gzip.decompress(r.content).decode('utf-8', errors='ignore')
        content = limpiar_xml(content)

        # Procesar Canales
        canales = re.findall(r'<channel.*?</channel>', content, re.DOTALL)
        ids_interes = set()
        canales_finales = []

        for c in canales:
            match_id = re.search(r'id="(.*?)"', c)
            if match_id:
                cid = match_id.group(1).lower()
                encontrado = False
                for clave, nombre_fix in TRADUCCIONES.items():
                    if clave in cid:
                        # Si hay traducción, creamos la etiqueta limpia sin cirílico
                        nuevo_canal = f'<channel id="{match_id.group(1)}">\n    <display-name>{nombre_fix}</display-name>\n  </channel>'
                        canales_finales.append(nuevo_canal)
                        ids_interes.add(match_id.group(1))
                        encontrado = True
                        break
        
        # Procesar Programas
        programas = re.findall(r'<programme.*?</programme>', content, re.DOTALL)
        programas_finales = []
        for p in programas:
            m_chan = re.search(r'channel="(.*?)"', p)
            if m_chan and m_chan.group(1) in ids_interes:
                # Ajustar horas en los 14 dígitos
                p = re.sub(r'(\d{14})', ajustar_hora, p)
                # Forzar zona horaria España
                p = re.sub(r'\+\d{4}', '+0100', p)
                programas_finales.append(p)

        # Construir XML final
        resultado = '<?xml version="1.0" encoding="UTF-8"?>\n<tv>'
        resultado += "\n".join(canales_finales)
        resultado += "\n".join(programas_finales)
        resultado += "\n</tv>"

        with open("guia_completa.xml", "w", encoding="utf-8") as f:
            f.write(resultado)
        print(f"Hecho: {len(ids_interes)} canales filtrados.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()









