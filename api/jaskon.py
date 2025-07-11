import os
import tempfile
import requests
import pandas as pd
from ftplib import FTP
from dotenv import load_dotenv

load_dotenv()

def run_jaskon():
    print("Jaskon - Rozpoczęto pracę nad Jaskon...")

    # Zmienne środowiskowe
    url = os.getenv('JASKON_CSV_URL')
    ftp_server = os.getenv('FTP_HOST')
    ftp_user = os.getenv('JASKON_FTP_USER')
    ftp_pass = os.getenv('JASKON_FTP_PASS')
    ftp_folder = os.getenv('JASKON_FTP_FOLDER', 'data')

    # Ścieżki tymczasowe
    tmp_dir = tempfile.gettempdir()
    csv_path = os.path.join(tmp_dir, 'jaskon.csv')
    output_path = os.path.join(tmp_dir, 'jaskon.xlsx')

    try:
        # Pobranie pliku CSV
        response = requests.get(url, verify=False)
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
        ftp = FTP()
        ftp.connect(host=ftp_server, port=21)
        ftp.login(ftp_user, ftp_pass)
        ftp.cwd(ftp_folder)

        with open(output_path, 'rb') as file:
            ftp.storbinary(f'STOR {os.path.basename(output_path)}', file)

        ftp.quit()
        print(f"Jaskon - Plik '{output_path}' został zapisany na FTP.")
        return {"status": "success", "message": "Przesyłanie zakończone sukcesem."}

    except Exception as e:
        msg = f"Jaskon - Błąd: {e}"
        print(msg)
        return {"status": "error", "message": msg}

    finally:
        # Usuwanie plików tymczasowych
        for path in [csv_path, output_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    print(f"Jaskon - Usunięto plik tymczasowy: {path}")
                except Exception as cleanup_err:
                    print(f"Jaskon - Błąd przy usuwaniu '{path}': {cleanup_err}")
