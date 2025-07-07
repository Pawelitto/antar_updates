import os
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from ftplib import FTP
from dotenv import load_dotenv

# Załaduj zmienne z .env
load_dotenv()

print("Ardon - Rozpoczęto pracę nad Ardon...")

# Pobierz dane z env
xml_url = os.getenv('ARDON_XML_URL')
ftp_server = os.getenv('FTP_HOST')
ftp_login = os.getenv('ARDON_FTP_USER')
ftp_password = os.getenv('ARDON_FTP_PASS')
ftp_folder = os.getenv('ARDON_FTP_FOLDER', 'data')

# Nazwy plików
xml_file = 'ardon.xml'
excel_file = 'ardon.xlsx'

try:
    # Pobranie pliku XML
    response = requests.get(xml_url)
    response.raise_for_status()

    with open(xml_file, 'wb') as file:
        file.write(response.content)

    # Parsowanie pliku XML
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Wyciąganie danych
    item_codes = []
    amounts_in_stock = []

    for item in root.findall('.//SHOPITEM'):
        item_code = item.find('ITEM_CODE').text
        amount_in_stock = item.find('AMOUNT_IN_STOCK').text
        item_codes.append(item_code)
        amounts_in_stock.append(amount_in_stock)

    # Tworzenie DataFrame
    df = pd.DataFrame({
        'Kod': item_codes,
        'SoH': amounts_in_stock
    })
    df['SoH'] = df['SoH'].apply(lambda x: int(x) > 0)

    # Zapisz plik Excel
    df.to_excel(excel_file, index=False, engine='openpyxl')

    # Połączenie FTP i wysyłka
    try:
        ftp = FTP(ftp_server)
        ftp.login(ftp_login, ftp_password)
        ftp.cwd(ftp_folder)

        with open(excel_file, 'rb') as file:
            ftp.storbinary(f'STOR {excel_file}', file)

        print(f"Ardon - Plik '{excel_file}' został pomyślnie zapisany na serwerze FTP w folderze '{ftp_folder}'.")
        ftp.quit()

    except Exception as ftp_err:
        print(f'Ardon - Błąd FTP: {ftp_err}')

except Exception as e:
    print(f'Ardon - Błąd ogólny: {e}')

finally:
    # Usuwanie lokalnych plików tymczasowych
    for path in [xml_file, excel_file]:
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"Ardon - Usunięto plik tymczasowy: {path}")
            except Exception as cleanup_err:
                print(f"Ardon - Błąd przy usuwaniu '{path}': {cleanup_err}")
