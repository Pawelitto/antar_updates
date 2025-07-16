import os
import requests
import pandas as pd
from ftplib import FTP
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
import tempfile

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

# 📂 Plik tymczasowy
tmp_dir = tempfile.gettempdir()
output_path = os.path.join(tmp_dir, 'cerva.csv')

def run_cerva():
    print("Cerva - Rozpoczęto pracę...")
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

        # Step 3: Request 'DISPO' data
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
            dostepnosc = "TAK" if torun_dispo > 0 else "NIE"
            data.append({'ARTYKUL': code, 'DOSTEPNOSC': dostepnosc})

        df = pd.DataFrame(data)

        # Zapis do CSV z odpowiednim formatem
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('ARTYKUL|"DOSTEPNOSC"\n')
            for _, row in df.iterrows():
                f.write(f'{row["ARTYKUL"]}|"{row["DOSTEPNOSC"]}"\n')

        # FTP Upload
        try:
            ftp = FTP(ftp_server)
            ftp.login(ftp_login, ftp_password)

            with open(output_path, 'rb') as file:
                ftp.storbinary(f'STOR {os.path.basename(output_path)}', file)

            print(f"Cerva - Plik '{output_path}' został zapisany na serwerze FTP.")
            ftp.quit()

            return {"status": "success", "message": "Przesyłanie zakończone sukcesem."}

        except Exception as ftp_err:
            print(f"Cerva - Błąd FTP: {ftp_err}")
            return {"status": "error", "message": f"Błąd FTP: {ftp_err}"}

    except Exception as e:
        print(f"Cerva - Wystąpił błąd ogólny: {e}")
        return {"status": "error", "message": str(e)}

    finally:
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
                print("Cerva - Plik tymczasowy został usunięty.")
            except Exception as cleanup_err:
                print(f"Cerva - Błąd podczas usuwania pliku: {cleanup_err}")
