import os
import pandas as pd
import requests
from ftplib import FTP
from dotenv import load_dotenv

load_dotenv()

file_path = 'common_kody.xlsx'
output_file = 'hermon.xlsx'

# Wczytywanie danych z Excela
try:
    excel_data = pd.read_excel(file_path)
    print("Hermon - Plik został wczytany pomyślnie.")
except FileNotFoundError:
    print(f"Hermon - Plik {file_path} nie został znaleziony.")
    exit()
except Exception as e:
    print(f"Hermon - Wystąpił błąd podczas wczytywania pliku: {e}")
    exit()

# Sprawdzenie kolumny
if 'Kod towaru' not in excel_data.columns:
    print("Hermon - Brak kolumny 'Kod towaru' w pliku.")
    exit()

# Lista kodów
kody_towaru = excel_data['Kod towaru'].tolist()

# Dane z .env
api_base = os.getenv('HERMON_API_URL')
login = os.getenv('HERMON_LOGIN')
password = os.getenv('HERMON_PASSWORD')

ftp_server = os.getenv('FTP_HOST')
ftp_user = os.getenv('HERMON_FTP_USER')
ftp_pass = os.getenv('HERMON_FTP_PASS')
ftp_folder = os.getenv('HERMON_FTP_FOLDER', 'data')

# Autoryzacja
try:
    auth_response = requests.post(f"{api_base}/authenticate", json={"Login": login, "Password": password})
    auth_response.raise_for_status()

    token = auth_response.json().get('token')
    if not token:
        print("Hermon - Nie udało się uzyskać tokenu.")
        exit()
    print("Hermon - Token autoryzacyjny uzyskany.")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Pobieranie danych
    articles_url = f"{api_base}/articles"
    response = requests.post(articles_url, json=kody_towaru, headers=headers)
    response.raise_for_status()

    data = response.json()
    print("Hermon - Dane pobrane pomyślnie.")

    # Przetwarzanie danych
    results = []
    for item in data:
        kod = item.get('id')
        if not kod:
            continue

        branches = item.get('branchesAvailability', [])
        quantity = branches[0].get('quantity', '0') if branches else '0'
        soh = quantity != '0'
        results.append({'Kod': kod, 'SoH': soh})

    df = pd.DataFrame(results)
    df.to_excel(output_file, index=False)

    # Wysyłka FTP
    try:
        ftp = FTP(ftp_server)
        ftp.login(ftp_user, ftp_pass)
        ftp.cwd(ftp_folder)

        with open(output_file, 'rb') as f:
            ftp.storbinary(f'STOR {output_file}', f)

        print(f"Hermon - Plik '{output_file}' wysłany na FTP do folderu '{ftp_folder}'.")
        ftp.quit()

    except Exception as ftp_err:
        print(f"Hermon - Błąd FTP: {ftp_err}")

except requests.exceptions.RequestException as req_err:
    print(f"Hermon - Błąd HTTP: {req_err}")
except Exception as e:
    print(f"Hermon - Inny błąd: {e}")

finally:
    # Usunięcie tylko pliku wynikowego
    if os.path.exists(output_file):
        try:
            os.remove(output_file)
            print(f"Hermon - Tymczasowy plik '{output_file}' został usunięty.")
        except Exception as cleanup_err:
            print(f"Hermon - Błąd przy usuwaniu pliku tymczasowego: {cleanup_err}")
