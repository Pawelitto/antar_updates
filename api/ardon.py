import os
import tempfile
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from ftplib import FTP, error_perm, all_errors
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

    ftp = None

    try:
        # Krok 1: Pobieranie pliku XML
        print("Ardon - Pobieranie pliku XML...")
        try:
            response = requests.get(xml_url, timeout=10)
            response.raise_for_status()
            with open(xml_file, 'wb') as f:
                f.write(response.content)
        except requests.RequestException as req_err:
            raise Exception(f"Błąd pobierania pliku XML: {req_err}")

        # Krok 2: Parsowanie XML
        print("Ardon - Parsowanie pliku XML...")
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
        except ET.ParseError as parse_err:
            raise Exception(f"Błąd parsowania XML: {parse_err}")

        # Krok 3: Ekstrakcja danych
        print("Ardon - Przetwarzanie danych XML...")
        data = []
        for item in root.findall('.//SHOPITEM'):
            kod = item.find('ITEM_CODE').text if item.find('ITEM_CODE') is not None else ''
            amount_text = item.find('AMOUNT_IN_STOCK').text if item.find('AMOUNT_IN_STOCK') is not None else '0'
            ilosc = int(amount_text) if amount_text.isdigit() else 0
            dostepnosc = "TAK" if ilosc > 0 else "NIE"
            data.append({'ARTYKUL': kod, 'DOSTEPNOSC': dostepnosc})

        df = pd.DataFrame(data)

        # Krok 4: Zapis CSV
        print("Ardon - Zapis danych do pliku CSV...")
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('ARTYKUL|"DOSTEPNOSC"\n')
                for _, row in df.iterrows():
                    f.write(f'{row["ARTYKUL"]}|"{row["DOSTEPNOSC"]}"\n')
        except Exception as write_err:
            raise Exception(f"Błąd zapisu do pliku CSV: {write_err}")

        # Krok 5: Połączenie FTP i wysyłka
        print("Ardon - Nawiązywanie połączenia FTP...")
        try:
            ftp = FTP()
            ftp.connect(host=ftp_server, port=21, timeout=10)
            ftp.login(user=ftp_login, passwd=ftp_password)

            print("Ardon - Wysyłanie pliku CSV przez FTP...")
            with open(output_file, 'rb') as f:
                ftp.storbinary(f'STOR {os.path.basename(output_file)}', f)
        except all_errors as ftp_err:
            raise Exception(f"Błąd połączenia lub przesyłu FTP: {ftp_err}")
        finally:
            if ftp:
                try:
                    ftp.quit()
                    print("Ardon - Zakończono sesję FTP.")
                except Exception as quit_err:
                    print(f"Ardon - Błąd przy zamykaniu FTP: {quit_err}")

        print("Ardon - Przesyłanie zakończone sukcesem.")
        return {"status": "success", "message": "Przesyłanie zakończone sukcesem."}

    except Exception as e:
        print(f'Ardon - Błąd: {e}')
        return {"status": "error", "message": str(e)}

    finally:
        # Usuwanie plików tymczasowych
        for path in [xml_file, output_file]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    print(f"Ardon - Usunięto plik tymczasowy: {path}")
                except Exception as cleanup_err:
                    print(f"Ardon - Błąd przy usuwaniu pliku: {cleanup_err}")
