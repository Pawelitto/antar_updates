import os
import pandas as pd
import requests
from ftplib import FTP

file_path = 'common_kody.xlsx'
output_file = 'hermon.xlsx'

# Wczytanie pliku Excel
try:
    excel_data = pd.read_excel(file_path)
    print("Hermon - Plik został wczytany pomyślnie.")
except FileNotFoundError:
    print(f"Hermon - Plik {file_path} nie został znaleziony.")
    exit()
except Exception as e:
    print(f"Hermon - Wystąpił błąd podczas wczytywania pliku: {e}")
    exit()

if 'Kod towaru' not in excel_data.columns:
    print("Hermon - Brak kolumny 'Kod towaru' w pliku.")
    exit()

kody_towaru = excel_data['Kod towaru'].tolist()

# Autoryzacja
auth_url = "http://78.31.93.254:81/client-service/authenticate"
auth_data = {
    "Login": "018249",
    "Password": "Antar-12345"
}
ftp_server = 'ftp.antar.pl'
ftp_login = 'hermon'
ftp_password = '#frJv8PmL'

try:
    auth_response = requests.post(auth_url, json=auth_data)
    auth_response.raise_for_status()
    token = auth_response.json().get('token')

    if not token:
        print("Hermon - Nie udało się uzyskać tokenu autoryzacyjnego.")
        exit()

    print("Hermon - Token autoryzacyjny uzyskany pomyślnie.")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    url = "http://78.31.93.254:81/client-service/articles"
    response = requests.post(url, json=kody_towaru, headers=headers)
    response.raise_for_status()

    print("Hermon - Zapytanie wysłane pomyślnie.")

    data = response.json()

    # Przetwarzanie danych
    ids = []
    availability = []

    for item in data:
        item_id = item.get('id')
        if not item_id:
            continue

        branches = item.get('branchesAvailability', [])
        is_available = False
        if branches:
            quantity = branches[0].get('quantity', '0')
            is_available = quantity != '0'

        ids.append(item_id)
        availability.append(is_available)

    df = pd.DataFrame({
        'Kod': ids,
        'SoH': availability
    })

    df.to_excel(output_file, index=False)

    # FTP Upload
    try:
        ftp = FTP(ftp_server)
        ftp.login(ftp_login, ftp_password)
        ftp.cwd('data')

        with open(output_file, 'rb') as file:
            ftp.storbinary(f'STOR {output_file}', file)

        print(f"Hermon - Plik '{output_file}' został pomyślnie zapisany na serwerze FTP w folderze 'data'.")
        ftp.quit()

    except Exception as ftp_err:
        print(f"Hermon - Błąd FTP: {ftp_err}")

except requests.exceptions.RequestException as req_err:
    print(f"Hermon - Błąd HTTP: {req_err}")

except Exception as e:
    print(f"Hermon - Inny błąd: {e}")

finally:
    # Usuń tylko plik wynikowy, nie dotykaj common_kody.xlsx
    if os.path.exists(output_file):
        try:
            os.remove(output_file)
            print(f"Hermon - Tymczasowy plik '{output_file}' został usunięty.")
        except Exception as cleanup_err:
            print(f"Hermon - Błąd przy usuwaniu pliku tymczasowego: {cleanup_err}")
