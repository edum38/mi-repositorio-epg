import requests
import gzip
import re

# LA ÚNICA PUERTA ABIERTA (La fuente rusa que sí te descargó archivos grandes)
URL_OPEN = "http://www.teleguide.info/download/new3/xmltv.xml.gz"

# Filtros de búsqueda para rescatar canales de España e Hispanoamérica
# Buscamos IDs o nombres que contengan estas siglas internacionales
FILTROS = [
    ".es", ".mx", ".ar", ".co", ".cl", ".it", ".fr", # Países
    "Discovery", "Disney", "HBO", "FOX", "CNN", "MTV", # Marcas
    "History", "National", "Eurosport", "Nick", "Warner", "Sony"
]

def main():
    print(f"Iniciando descarga de la fuente permitida: {URL_OPEN}")
    final_xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv generator-info-name="MiGuia-Filtro-Mundial">']
    
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        r = requests.get(URL_OPEN, headers=headers, timeout=60)
        if r.status_code == 200:
            print(f"¡CONEXIÓN EXITOSA! Tamaño: {len(r.content)} bytes.")
            content = gzip.decompress(r.content).decode('utf-8', errors='ignore')
            
            # Extraemos TODOS los canales y programas
            canales = re.findall(r'<channel.*?</channel>', content, re.DOTALL)
            programas = re.findall(r'<programme.*?</programme>', content, re.DOTALL)
            
            ids_interes = set()
            count_canales = 0

            # 1. Filtramos CANALES de interés (Latam, España, Europa)
            for c in canales:
                # Si el canal tiene alguna de nuestras marcas o países, lo guardamos
                if any(f.lower() in c.lower() for f in FILTROS):
                    final_xml.append(c)
                    count_canales += 1
                    # Guardamos el ID para traer su programación luego
                    match = re.search(r'id="(.*?)"', c)
                    if match:
                        ids_interes.add(match.group(1))

            # 2. Filtramos PROGRAMAS que pertenezcan a esos canales
            count_progs = 0
            for p in programas:
                match = re.search(r'channel="(.*?)"', p)
                if match and match.group(1) in ids_interes:
                    final_xml.append(p)
                    count_progs += 1

            print(f"  --> Filtrado terminado: {count_canales} canales y {count_progs} programas rescatados.")
        else:
            print(f"Error HTTP: {r.status_code}")
            
    except Exception as e:
        print(f"Fallo en el proceso: {e}")

    final_xml.append('</tv>')
    resultado = "\n".join(final_xml)

    with open("guia_completa.xml", "w", encoding="utf-8") as f:
        f.write(resultado)
    with gzip.open("guia_completa.xml.gz", "wt", encoding="utf-8") as f:
        f.write(resultado)
    
    print(f"Archivo final guardado. Caracteres: {len(resultado)}")

if __name__ == "__main__":
    main()








