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
    ftp_folder = os.getenv('ARDON_FTP_FOLDER', 'data')

    # 📂 Skonfiguruj pliki w katalogu tymczasowym
    tmp_dir = tempfile.gettempdir()
    xml_file = os.path.join(tmp_dir, 'ardon.xml')
    excel_file = os.path.join(tmp_dir, 'ardon.xlsx')

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
        item_codes = []
        amounts_in_stock = []
        for item in root.findall('.//SHOPITEM'):
            item_codes.append(item.find('ITEM_CODE').text)
            amounts_in_stock.append(item.find('AMOUNT_IN_STOCK').text)

        # DataFrame i zapis do Excela
        df = pd.DataFrame({
            'Kod': item_codes,
            'SoH': [int(x) > 0 for x in amounts_in_stock]
        })
        df.to_excel(excel_file, index=False, engine='openpyxl')

        # FTP - połączenie i wysyłka
        ftp = FTP(ftp_server)
        ftp.login(ftp_login, ftp_password)
        ftp.cwd(ftp_folder)

        with open(excel_file, 'rb') as f:
            ftp.storbinary(f'STOR {os.path.basename(excel_file)}', f)

        ftp.quit()
        print("Ardon - Przesyłanie zakończone sukcesem.")
        return {"status": "success", "message": "Przesyłanie zakończone sukcesem."}

    except Exception as e:
        print(f'Ardon - Błąd: {e}')
        return {"status": "error", "message": str(e)}

    finally:
        # Sprzątanie po sobie
        for path in [xml_file, excel_file]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    print(f"Ardon - Usunięto plik tymczasowy: {path}")
                except Exception as cleanup_err:
                    print(f"Ardon - Błąd przy usuwaniu pliku: {cleanup_err}")
