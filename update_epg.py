import requests
import gzip

# Fuente de España en un servidor que NO es GitHub y es muy ligero
URL = "http://www.teleguide.info/download/new3/xmltv.xml.gz"

def main():
    print(f"Intentando descarga directa de: {URL}")
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        r = requests.get(URL, headers=headers, timeout=60)
        if r.status_code == 200:
            print(f"¡CONEXIÓN EXITOSA! Tamaño recibido: {len(r.content)} bytes")
            
            # Guardamos el archivo tal cual, sin procesar, para ver si escribe algo
            with open("guia_completa.xml.gz", "wb") as f:
                f.write(r.content)
            
            # Descomprimimos para tener el XML plano también
            content = gzip.decompress(r.content)
            with open("guia_completa.xml", "wb") as f:
                f.write(content)
                
            print("Archivos guardados correctamente en el repositorio.")
        else:
            print(f"Error de conexión. Código: {r.status_code}")
            
    except Exception as e:
        print(f"Fallo crítico: {e}")

if __name__ == "__main__":
    main()






