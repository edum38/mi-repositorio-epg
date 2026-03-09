import requests
import gzip
import io

# Solo UNA fuente que tiene TODO el mundo (más de 100MB)
FUENTE_GLOBAL = "https://iptv-org.github.io/epg/guides/world.xml.gz"

# Los países que queremos mantener (códigos de país)
PAISES_INTERES = ['es', 'it', 'mx', 'ar', 'co', 'pe', 'fr', 'de', 'uk', 'br']

def main():
    print("Iniciando descarga del archivo MUNDIAL (esto puede tardar)...")
    
    try:
        # 1. Descargar el archivo gigante
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(FUENTE_GLOBAL, headers=headers, timeout=120)
        
        if r.status_code == 200:
            print("Descarga completa. Descomprimiendo y filtrando...")
            
            # 2. Descomprimir en memoria
            with gzip.GzipFile(fileobj=io.BytesIO(r.content)) as f:
                content = f.read().decode('utf-8', errors='ignore')

            # 3. Preparar el nuevo archivo
            # Buscamos la cabecera original
            header_end = content.find('>') + 1
            tv_start = content.find('<tv', header_end)
            tv_end = content.find('>', tv_start) + 1
            
            final_xml = [content[:tv_end]] # Guardamos la cabecera y el tag <tv...>

            # 4. Filtrar por país (buscamos canales que terminen en .es, .mx, etc)
            print("Filtrando canales por país...")
            import re
            
            # Este regex busca canales y programas que coincidan con tus países
            paises_pattern = "|".join([rf"\.{p}\"" for p in PAISES_INTERES])
            
            # Extraer bloques
            channels = re.findall(r'<channel.*?</channel>', content, re.DOTALL)
            programmes = re.findall(r'<programme.*?</programme>', content, re.DOTALL)

            canales_guardados = []
            ids_guardados = set()

            for c in channels:
                if any(ext in c for ext in [f'.{p}"' for p in PAISES_INTERES]):
                    final_xml.append(c)
                    # Guardamos el ID para filtrar los programas luego
                    match = re.search(r'id="(.*?)"', c)
                    if match: ids_guardados.add(match.group(1))

            print(f"  --> {len(ids_guardados)} canales encontrados.")

            for p in programmes:
                match = re.search(r'channel="(.*?)"', p)
                if match and match.group(1) in ids_guardados:
                    final_xml.append(p)

            final_xml.append('</tv>')
            resultado = "\n".join(final_xml)

            # 5. Guardar
            with open("guia_completa.xml", "w", encoding="utf-8") as f:
                f.write(resultado)
            with gzip.open("guia_completa.xml.gz", "wt", encoding="utf-8") as f:
                f.write(resultado)
                
            print(f"¡LOGRADO! Archivo final generado con éxito.")
        else:
            print(f"Error al bajar el archivo mundial: {r.status_code}")

    except Exception as e:
        print(f"Error crítico: {e}")

if __name__ == "__main__":
    main()




