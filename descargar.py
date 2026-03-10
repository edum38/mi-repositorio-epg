import requests
import gzip

def main():
    url = "http://www.teleguide.info/download/new3/xmltv.xml.gz"
    print("Paso 1: Descargando archivo original...")
    try:
        r = requests.get(url, timeout=60)
        if r.status_code == 200:
            with open("original.xml.gz", "wb") as f:
                f.write(r.content)
            print("Archivo original guardado con éxito.")
        else:
            print(f"Error de descarga: {r.status_code}")
    except Exception as e:
        print(f"Fallo crítico: {e}")

if __name__ == "__main__":
    main()