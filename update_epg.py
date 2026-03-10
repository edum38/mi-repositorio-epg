import requests
import gzip
import re
from datetime import datetime, timedelta

def main():
    url = "http://www.teleguide.info/download/new3/xmltv.xml.gz"
    print("Conectando...")
    
    try:
        r = requests.get(url, timeout=30)
        # Si la descarga falla, creamos un XML de error para que el flujo no se rompa
        if r.status_code != 200:
            content = '<?xml version="1.0" encoding="UTF-8"?><tv><channel id="error"><display-name>Error de Servidor</display-name></channel></tv>'
        else:
            content = gzip.decompress(r.content).decode('utf-8', errors='ignore')
            
            # Ajuste de hora para España (-2 horas respecto a Moscú)
            # Buscamos fechas de 14 dígitos
            def shift(m):
                t = m.group(1)
                dt = datetime.strptime(t, "%Y%m%d%H%M%S") - timedelta(hours=2)
                return dt.strftime("%Y%m%d%H%M%S")
            
            content = re.sub(r'(\d{14})', shift, content)
            # Forzamos el nombre de algunos canales para España
            content = content.replace("Discovery", "Discovery Channel Spain")
            content = content.replace("Disney", "Disney Channel Spain")
            content = content.replace("+0300", "+0100")

        # Guardar resultados
        with open("guia_completa.xml", "w", encoding="utf-8") as f:
            f.write(content)
        print("Hecho.")

    except Exception as e:
        print(f"Fallo: {e}")
        with open("guia_completa.xml", "w") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?><tv><channel id="error"><display-name>Fallo Critico</display-name></channel></tv>')

if __name__ == "__main__":
    main()









