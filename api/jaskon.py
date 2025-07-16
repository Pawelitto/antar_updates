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

    # Ścieżki tymczasowe
    tmp_dir = tempfile.gettempdir()
    csv_path = os.path.join(tmp_dir, 'jaskon_input.csv')
    output_path = os.path.join(tmp_dir, 'jaskon.csv')

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
        df_selected.columns = ['ARTYKUL', 'DOSTEPNOSC']
        df_selected['DOSTEPNOSC'] = df_selected['DOSTEPNOSC'].apply(lambda x: "TAK" if x != 0 else "NIE")

        # Zapis ręczny do CSV z wymaganym formatem
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('ARTYKUL|"DOSTEPNOSC"\n')
            for _, row in df_selected.iterrows():
                f.write(f'{row["ARTYKUL"]}|"{row["DOSTEPNOSC"]}"\n')

        # Wysyłka przez FTP
        ftp = FTP()
        ftp.connect(host=ftp_server, port=21)
        ftp.login(ftp_user, ftp_pass)

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
