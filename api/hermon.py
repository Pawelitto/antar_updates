import os
import tempfile
import pandas as pd
import requests
from ftplib import FTP
from dotenv import load_dotenv

load_dotenv()

def run_hermon():
    print("Hermon - Rozpoczęto pracę nad Hermon...")

    # Ustal ścieżkę absolutną do pliku 'common_kody.xlsx' znajdującego się w tym samym folderze co skrypt
    file_path = '/home/ubuntu/antar_updates/api/common_kody.xlsx'

    print(f"Hermon - Próbuję wczytać plik z: {file_path}")
    print(f"Hermon - Czy plik istnieje? {os.path.exists(file_path)}")


    tmp_dir = tempfile.gettempdir()
    output_file = os.path.join(tmp_dir, 'hermon.csv')

    print(f"Hermon - Bieżący katalog roboczy: {os.getcwd()}")
    print(f"Hermon - Szukam pliku pod ścieżką: {file_path}")

    # Wczytywanie danych z Excela
    try:
        excel_data = pd.read_excel(file_path)
        print("Hermon - Plik został wczytany pomyślnie.")
    except FileNotFoundError:
        msg = f"Hermon - Plik {file_path} nie został znaleziony."
        print(msg)
        return {"status": "error", "message": msg}
    except Exception as e:
        msg = f"Hermon - Wystąpił błąd podczas wczytywania pliku: {e}"
        print(msg)
        return {"status": "error", "message": msg}

    if 'Kod towaru' not in excel_data.columns:
        msg = "Hermon - Brak kolumny 'Kod towaru' w pliku."
        print(msg)
        return {"status": "error", "message": msg}

    kody_towaru = excel_data['Kod towaru'].tolist()

    api_base = os.getenv('HERMON_API_URL')
    login = os.getenv('HERMON_LOGIN')
    password = os.getenv('HERMON_PASSWORD')

    ftp_server = os.getenv('FTP_HOST')
    ftp_user = os.getenv('HERMON_FTP_USER')
    ftp_pass = os.getenv('HERMON_FTP_PASS')

    try:
        auth_response = requests.post(f"{api_base}/authenticate", json={"Login": login, "Password": password})
        auth_response.raise_for_status()

        token = auth_response.json().get('token')
        if not token:
            msg = "Hermon - Nie udało się uzyskać tokenu."
            print(msg)
            return {"status": "error", "message": msg}
        print("Hermon - Token autoryzacyjny uzyskany.")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        response = requests.post(f"{api_base}/articles", json=kody_towaru, headers=headers)
        response.raise_for_status()
        data = response.json()
        print("Hermon - Dane pobrane pomyślnie.")

        results = []
        for item in data:
            kod = item.get('id')
            if not kod:
                continue
            branches = item.get('branchesAvailability', [])
            quantity = branches[0].get('quantity', '0') if branches else '0'
            dostepnosc = "TAK" if quantity != '0' else "NIE"
            results.append({'ARTYKUL': kod, 'DOSTEPNOSC': dostepnosc})

        df = pd.DataFrame(results)

        # Zapis do CSV z odpowiednim formatowaniem
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('ARTYKUL|"DOSTEPNOSC"\n')
            for _, row in df.iterrows():
                f.write(f'{row["ARTYKUL"]}|"{row["DOSTEPNOSC"]}"\n')

        # Wysyłka FTP
        ftp = FTP()
        ftp.connect(host=ftp_server, port=21)
        ftp.login(ftp_user, ftp_pass)

        with open(output_file, 'rb') as f:
            ftp.storbinary(f'STOR {os.path.basename(output_file)}', f)

        ftp.quit()
        print("Hermon - Przesyłanie zakończone sukcesem.")
        return {"status": "success", "message": "Przesyłanie zakończone sukcesem."}

    except requests.exceptions.RequestException as req_err:
        msg = f"Hermon - Błąd HTTP: {req_err}"
        print(msg)
        return {"status": "error", "message": msg}
    except Exception as e:
        msg = f"Hermon - Błąd: {e}"
        print(msg)
        return {"status": "error", "message": msg}
    finally:
        if os.path.exists(output_file):
            try:
                os.remove(output_file)
                print(f"Hermon - Usunięto plik tymczasowy: {output_file}")
            except Exception as cleanup_err:
                print(f"Hermon - Błąd przy usuwaniu pliku: {cleanup_err}")
