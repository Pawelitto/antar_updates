import os
import requests
import pandas as pd
from ftplib import FTP
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

print("Cerva - Rozpoczęto pracę...")

# Załaduj dane z .env
load_dotenv()

# --- Dane logowania z .env ---
username = os.getenv('CERVA_USERNAME')
password = os.getenv('CERVA_PASSWORD')
partner = os.getenv('CERVA_PARTNER')
client_id = os.getenv('CERVA_CLIENT_ID')

ftp_server = os.getenv('FTP_HOST')
ftp_login = os.getenv('CERVA_FTP_USER')
ftp_password = os.getenv('CERVA_FTP_PASS')
ftp_folder = os.getenv('CERVA_FTP_FOLDER', 'data')

output_path = 'cerva.xlsx'

try:
    # Step 1: Request access token
    auth_url = "https://www.cerva.com/authorizationserver/oauth/token"
    auth_params = {
        "grant_type": "password",
        "client_id": client_id,
        "username": username,
        "password": password,
        "partner": partner
    }
    auth_response = requests.post(auth_url, params=auth_params)
    auth_response.raise_for_status()
    auth_data = auth_response.json()
    access_token = auth_data['access_token']
    print("Cerva - Token autoryzacyjny uzyskany.")

    # Step 2: Request feed with bearer token
    feed_url = "https://www.cerva.com/api/PL/feed"
    headers = {'Authorization': f'Bearer {access_token}'}
    feed_params = {"partner": partner, "lang": "PL"}

    feed_response = requests.get(feed_url, params=feed_params, headers=headers)
    feed_response.raise_for_status()
    feed_data = feed_response.json()

    # Get download URL for 'DISPO'
    dispo_feed = next(item for item in feed_data if item['feedType'] == 'DISPO')
    dispo_url = f"https://www.cerva.com{dispo_feed['downloadUrl']}"

    # Step 3: Request 'DISPO' data with bearer token
    dispo_response = requests.get(dispo_url, headers=headers)
    dispo_response.raise_for_status()
    dispo_xml = dispo_response.text

    # Parse XML response
    root = ET.fromstring(dispo_xml)

    # Prepare data
    data = []
    for product in root.findall('.//product'):
        code = product.get('code')
        torun_dispo = next(
            (int(detail.get('dispo')) for detail in product.findall('detail') if detail.get('site') == 'Toruń'),
            0
        )
        soh = torun_dispo > 0
        data.append({'Kod': code, 'SoH': soh})

    df = pd.DataFrame(data)
    df.to_excel(output_path, index=False)

    # FTP Upload
    try:
        ftp = FTP(ftp_server)
        ftp.login(ftp_login, ftp_password)
        ftp.cwd(ftp_folder)

        with open(output_path, 'rb') as file:
            ftp.storbinary(f'STOR {output_path}', file)

        print(f"Cerva - Plik '{output_path}' został zapisany na serwerze FTP w folderze '{ftp_folder}'.")
        ftp.quit()

    except Exception as ftp_err:
        print(f"Cerva - Błąd FTP: {ftp_err}")

except Exception as e:
    print(f"Cerva - Wystąpił błąd ogólny: {e}")

finally:
    if os.path.exists(output_path):
        try:
            os.remove(output_path)
            print("Cerva - Plik tymczasowy został usunięty.")
        except Exception as cleanup_err:
            print(f"Cerva - Błąd podczas usuwania pliku: {cleanup_err}")
