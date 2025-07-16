import os
import csv
import tempfile
import requests
import pandas as pd
from ftplib import FTP
from dotenv import load_dotenv

load_dotenv()

def run_portwest():
    print("Portwest - Rozpoczęto pracę nad Portwest...")

    # Dane z .env
    url = os.getenv('PORTWEST_CSV_URL')
    ftp_server = os.getenv('FTP_HOST')
    ftp_user = os.getenv('PORTWEST_FTP_USER')
    ftp_pass = os.getenv('PORTWEST_FTP_PASS')

    # Ścieżki tymczasowe
    tmp_dir = tempfile.gettempdir()
    csv_file = os.path.join(tmp_dir, 'portwest_temporary.csv')
    output_file = os.path.join(tmp_dir, 'portwest.csv')

    try:
        # Pobranie pliku CSV
        response = requests.get(url)
        response.raise_for_status()

        with open(csv_file, 'wb') as file:
            file.write(response.content)

        print("Portwest - CSV został pobrany pomyślnie.")

        # Wczytanie i przetwarzanie pliku
        df = pd.read_csv(csv_file)

        # Zmiana nazw kolumn i konwersja danych
        df.rename(columns={'Item': 'ARTYKUL', 'SoH': 'DOSTEPNOSC'}, inplace=True)
        df['DOSTEPNOSC'] = df['DOSTEPNOSC'].apply(lambda x: "TAK" if x > 0 else "NIE")

        with open(output_file, 'w', encoding='utf-8') as f:
            # Zapis nagłówka
            f.write(f'ARTYKUL|"DOSTEPNOSC"\n')
            
            # Zapis wierszy
            for _, row in df.iterrows():
                f.write(f'{row["ARTYKUL"]}|"{row["DOSTEPNOSC"]}"\n')

        # Wysyłka przez FTP
        ftp = FTP()
        ftp.connect(host=ftp_server, port=21)
        ftp.login(ftp_user, ftp_pass)

        with open(output_file, 'rb') as file:
            ftp.storbinary(f'STOR {os.path.basename(output_file)}', file)

        ftp.quit()
        print(f"Portwest - Plik '{output_file}' został wysłany na FTP.")
        return {"status": "success", "message": "Przesyłanie zakończone sukcesem."}

    except Exception as e:
        msg = f"Portwest - Błąd: {e}"
        print(msg)
        return {"status": "error", "message": msg}

    finally:
        # Usuwanie tymczasowych plików
        for path in [csv_file, output_file]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    print(f"Portwest - Usunięto tymczasowy plik: {path}")
                except Exception as cleanup_err:
                    print(f"Portwest - Błąd przy usuwaniu '{path}': {cleanup_err}")
