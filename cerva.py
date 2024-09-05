import os
import requests
import pandas as pd
from ftplib import FTP
import xml.etree.ElementTree as ET

# Step 1: Request access token
auth_url = "https://www.cerva.com/authorizationserver/oauth/token"
auth_params = {
    "grant_type": "password",
    "client_id": "crvweb",
    "username": "antarpm@gmail.com",
    "password": "Lealea12",
    "partner": "0000105363"
}
auth_response = requests.post(auth_url, params=auth_params)
auth_data = auth_response.json()
access_token = auth_data['access_token']

# Step 2: Request feed with bearer token
feed_url = "https://www.cerva.com/api/PL/feed"
headers = {'Authorization': f'Bearer {access_token}'}
feed_params = {
    "partner": "0000105363",
    "lang": "PL"
}
feed_response = requests.get(feed_url, params=feed_params, headers=headers)
feed_data = feed_response.json()

# Get download URL for 'DISPO'
dispo_feed = next(item for item in feed_data if item['feedType'] == 'DISPO')
dispo_url = f"https://www.cerva.com{dispo_feed['downloadUrl']}"

# Step 3: Request 'DISPO' data with bearer token
dispo_response = requests.get(dispo_url, headers=headers)
dispo_xml = dispo_response.text

# Parse XML response
root = ET.fromstring(dispo_xml)

# Prepare data for Excel
data = []
for product in root.findall('.//product'):
    code = product.get('code')
    torun_dispo = next((int(detail.get('dispo')) for detail in product.findall('detail') if detail.get('site') == 'Toruń'), 0)
    soh = True if torun_dispo > 0 else False
    data.append({'KODUDOST': code, 'SoH': soh})

# Create DataFrame
df = pd.DataFrame(data)

output_path = 'cerva.xlsx'

# Save to Excel
df.to_excel(output_path, index=False)

ftp_server = 'ftp.antar.pl'
ftp_login = 'cerva'
ftp_password = 'iqTFbP4_Nw9'

try:
  # Nawiązanie połączenia z serwerem FTP
  ftp = FTP(ftp_server)
  ftp.login(ftp_login, ftp_password)
  
  # Przejście do folderu 'data'
  ftp.cwd('data')
  
  # Otwieranie pliku i przesyłanie go na serwer FTP
  with open(output_path, 'rb') as file:
    ftp.storbinary(f'STOR {output_path}', file)
  
  print(f"Cerva - Plik '{output_path}' został pomyślnie zapisany na serwerze FTP w folderze 'data'.")

  # Zamknięcie połączenia FTP
  ftp.quit()
  
  # Usunięcie lokalnego pliku po przesłaniu
  os.remove(output_path)

except Exception as e:
  print(f'Cerva - Wystąpił błąd podczas połączenia z FTP lub przesyłania pliku: {e}')