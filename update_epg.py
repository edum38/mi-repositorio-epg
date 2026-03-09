import requests
import gzip
import shutil
import os

# Fuente mundial (comprimida)
URL_GLOBAL = "https://iptv-org.github.io/epg/guides/world.xml.gz"
# Países que queremos filtrar (sus extensiones de ID)
PAISES = ('.es"', '.mx"', '.ar"', '.co"', '.pe"', '.it"', '.fr"', '.de"', '.uk"', '.br"')

def main():
    print("Descargando archivo mundial en modo flujo (ahorro de RAM)...")
    
    try:
        # 1. Descargar el archivo GZ a disco primero para no saturar la RAM
        r = requests.get(URL_GLOBAL, stream=True, timeout=120)
        if r.status_code != 200:
            print(f"Error descarga: {r.status_code}")
            return

        with open("temp_world.xml.gz", "wb") as f:
            shutil.copyfileobj(r.raw, f)
        
        print("Filtrando datos línea por línea...")
        
        # 2. Leer el GZ y escribir el nuevo XML al mismo tiempo
        ids_validos = set()
        
        with gzip.open("temp_world.xml.gz", "rt", encoding="utf-8", errors="ignore") as f_in:
            with open("guia_completa.xml", "w", encoding="utf-8") as f_out:
                
                f_out.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f_out.write('<tv generator-info-name="MiAppIPTV">\n')
                
                # Fase 1: Guardar canales de tus países
                for line in f_in:
                    if "<channel" in line:
                        if any(p in line for p in PAISES):
                            f_out.write(line)
                            # Extraer ID para los programas
                            import re
                            match = re.search(r'id="(.*?)"', line)
                            if match: ids_validos.add(match.group(1))
                    
                    # Fase 2: Si la línea es un programa, ver si pertenece a un canal guardado
                    elif "<programme" in line:
                        match = re.search(r'channel="(.*?)"', line)
                        if match and match.group(1) in ids_validos:
                            f_out.write(line)
                    
                    # Si la línea tiene info interna del programa (título, desc, etc) 
                    # y estamos dentro de un bloque válido, la escribimos
                    elif any(tag in line for tag in ["<title", "<desc", "<category", "<icon", "</programme", "</channel"]):
                        f_out.write(line)

                f_out.write("</tv>")

        # 3. Comprimir el resultado final
        with open("guia_completa.xml", "rb") as f_in:
            with gzip.open("guia_completa.xml.gz", "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        print(f"¡ÉXITO! Se han filtrado {len(ids_validos)} canales de tus 10 países.")
        
        # Limpieza de temporales
        if os.path.exists("temp_world.xml.gz"): os.remove("temp_world.xml.gz")

    except Exception as e:
        print(f"Fallo: {e}")

if __name__ == "__main__":
    main()





