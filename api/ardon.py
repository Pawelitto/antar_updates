import os
import tempfile
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from ftplib import FTP
from dotenv import load_dotenv

load_dotenv()

def run_ardon():
    print("Ardon - Rozpoczęto pracę nad Ardon...")

    xml_url = os.getenv('ARDON_XML_URL')
    ftp_server = os.getenv('FTP_HOST')
    ftp_login = os.getenv('ARDON_FTP_USER')
    ftp_password = os.getenv('ARDON_FTP_PASS')

    tmp_dir = tempfile.gettempdir()
    xml_file = os.path.join(tmp_dir, 'ardon.xml')
    output_file = os.path.join(tmp_dir, 'ardon.csv')

    try:
        # Pobranie pliku XML
        response = requests.get(xml_url)
        response.raise_for_status()
        with open(xml_file, 'wb') as f:
            f.write(response.content)

        # Parsowanie XML
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Wydobycie danych
        data = []
        for item in root.findall('.//SHOPITEM'):
            kod = item.find('ITEM_CODE').text
            amount_text = item.find('AMOUNT_IN_STOCK').text
            ilosc = int(amount_text) if amount_text.isdigit() else 0
            dostepnosc = "TAK" if ilosc > 0 else "NIE"
            data.append({'ARTYKUL': kod, 'DOSTEPNOSC': dostepnosc})

        df = pd.DataFrame(data)

        # Zapis do CSV
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('ARTYKUL|"DOSTEPNOSC"\n')
            for _, row in df.iterrows():
                f.write(f'{row["ARTYKUL"]}|"{row["DOSTEPNOSC"]}"\n')

        # FTP - połączenie i wysyłka
        ftp = FTP()
        ftp.connect(host=ftp_server, port=21)
        ftp.login(ftp_login, ftp_password)

        with open(output_file, 'rb') as f:
            ftp.storbinary(f'STOR {os.path.basename(output_file)}', f)

        ftp.quit()
        print("Ardon - Przesyłanie zakończone sukcesem.")
        return {"status": "success", "message": "Przesyłanie zakończone sukcesem."}

    except Exception as e:
        print(f'Ardon - Błąd: {e}')
        return {"status": "error", "message": str(e)}

    finally:
        for path in [xml_file, output_file]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    print(f"Ardon - Usunięto plik tymczasowy: {path}")
                except Exception as cleanup_err:
                    print(f"Ardon - Błąd przy usuwaniu pliku: {cleanup_err}")
