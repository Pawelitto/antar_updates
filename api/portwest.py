import os
import requests
import pandas as pd
from ftplib import FTP
from dotenv import load_dotenv

print("Portwest - Rozpoczęto pracę nad Portwest...")

# Załaduj zmienne środowiskowe
load_dotenv()

# Ścieżki plików lokalnych
csv_file = 'portwest.csv'
output_file = 'portwest.xlsx'

# Dane z .env
url = os.getenv('PORTWEST_CSV_URL')
ftp_server = os.getenv('FTP_HOST')
ftp_user = os.getenv('PORTWEST_FTP_USER')
ftp_pass = os.getenv('PORTWEST_FTP_PASS')
ftp_folder = os.getenv('PORTWEST_FTP_FOLDER', 'data')

try:
    # Pobranie pliku CSV
    response = requests.get(url)
    response.raise_for_status()

    with open(csv_file, 'wb') as file:
        file.write(response.content)

    print("Portwest - CSV został pobrany pomyślnie.")

    # Wczytanie i przetwarzanie pliku
    df = pd.read_csv(csv_file)

    df.rename(columns={'Item': 'Kod', 'SoH': 'SoH'}, inplace=True)
    df['SoH'] = df['SoH'].apply(lambda x: x > 0)

    df.to_excel(output_file, index=False, engine='openpyxl')

    # Połączenie z FTP i przesłanie pliku
    try:
        ftp = FTP(ftp_server)
        ftp.login(ftp_user, ftp_pass)
        ftp.cwd(ftp_folder)

        with open(output_file, 'rb') as file:
            ftp.storbinary(f'STOR {output_file}', file)

        print(f"Portwest - Plik '{output_file}' został wysłany na FTP do folderu '{ftp_folder}'.")
        ftp.quit()

    except Exception as ftp_err:
        print(f"Portwest - Błąd FTP: {ftp_err}")

except Exception as e:
    print(f"Portwest - Błąd ogólny: {e}")

finally:
    # Usuwanie tymczasowych plików
    for path in [csv_file, output_file]:
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"Portwest - Usunięto tymczasowy plik: {path}")
            except Exception as cleanup_err:
                print(f"Portwest - Błąd przy usuwaniu '{path}': {cleanup_err}")
