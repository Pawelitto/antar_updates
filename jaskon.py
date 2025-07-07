import os
import requests
import pandas as pd
from ftplib import FTP
from dotenv import load_dotenv

print("Jaskon - Rozpoczęto pracę nad Jaskon...")

# Załaduj dane z .env
load_dotenv()

# Ścieżki plików
csv_path = 'jaskon.csv'
output_path = 'jaskon.xlsx'

# Zmienne środowiskowe
url = os.getenv('JASKON_CSV_URL')
ftp_server = os.getenv('FTP_HOST')
ftp_user = os.getenv('JASKON_FTP_USER')
ftp_pass = os.getenv('JASKON_FTP_PASS')
ftp_folder = os.getenv('JASKON_FTP_FOLDER', 'data')

try:
    # Pobranie pliku CSV
    response = requests.get(url)
    response.raise_for_status()

    with open(csv_path, 'wb') as file:
        file.write(response.content)

    print("Jaskon - Plik CSV został pobrany pomyślnie.")

    # Wczytanie i przetwarzanie pliku
    df = pd.read_csv(csv_path, sep=';', encoding='ISO-8859-1', skiprows=1)
    df_selected = df[['Symbol', 'Stany']].copy()
    df_selected.columns = ['Kod', 'SoH']
    df_selected['SoH'] = df_selected['SoH'].apply(lambda x: x != 0)

    # Zapis do Excel
    df_selected.to_excel(output_path, index=False, engine='openpyxl')

    # Wysyłka przez FTP
    try:
        ftp = FTP(ftp_server)
        ftp.login(ftp_user, ftp_pass)
        ftp.cwd(ftp_folder)

        with open(output_path, 'rb') as file:
            ftp.storbinary(f'STOR {output_path}', file)

        print(f"Jaskon - Plik '{output_path}' został zapisany na FTP w folderze '{ftp_folder}'.")
        ftp.quit()

    except Exception as ftp_err:
        print(f"Jaskon - Błąd FTP: {ftp_err}")

except Exception as e:
    print(f"Jaskon - Błąd ogólny: {e}")

finally:
    # Usuwanie plików tymczasowych
    for path in [csv_path, output_path]:
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"Jaskon - Usunięto plik tymczasowy: {path}")
            except Exception as cleanup_err:
                print(f"Jaskon - Błąd przy usuwaniu '{path}': {cleanup_err}")
