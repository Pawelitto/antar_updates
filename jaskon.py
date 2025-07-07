import os
import requests
import pandas as pd
from ftplib import FTP

print("Jaskon - Rozpoczęto pracę nad Jaskon...")

# Stałe plików
csv_path = 'jaskon.csv'
output_path = 'jaskon.xlsx'

# URL do pliku CSV
url = "https://pliki.jaskon.pl/37aaYdqdQmtL5jRmieTqqMrakZg3vmyhMtpwWFXXW7HjyX7eKKJHuZLRFH3nZv7C/jaskon.csv"

try:
    # Pobranie pliku CSV
    response = requests.get(url, verify=False)
    response.raise_for_status()

    with open(csv_path, 'wb') as file:
        file.write(response.content)

    print("Jaskon - Plik CSV został pobrany pomyślnie.")

    # Wczytanie pliku CSV
    df = pd.read_csv(csv_path, sep=';', encoding='ISO-8859-1', skiprows=1)

    # Zmiana nazw kolumn i logiki dostępności
    df_selected = df[['Symbol', 'Stany']].copy()
    df_selected.columns = ['Kod', 'SoH']
    df_selected['SoH'] = df_selected['SoH'].apply(lambda x: True if x != 0 else False)

    # Zapis do pliku Excel
    df_selected.to_excel(output_path, index=False, engine='openpyxl')

    # Dane dostępowe do FTP
    ftp_server = 'ftp.antar.pl'
    ftp_login = 'jaskon'
    ftp_password = 'Kp!7EcqGafVR2'

    # Wysyłka pliku przez FTP
    try:
        ftp = FTP(ftp_server)
        ftp.login(ftp_login, ftp_password)
        ftp.cwd('data')

        with open(output_path, 'rb') as file:
            ftp.storbinary(f'STOR {output_path}', file)

        print(f"Jaskon - Plik '{output_path}' został pomyślnie zapisany na serwerze FTP w folderze 'data'.")
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
                print(f"Jaskon - Plik tymczasowy '{path}' został usunięty.")
            except Exception as cleanup_err:
                print(f"Jaskon - Błąd przy usuwaniu '{path}': {cleanup_err}")
