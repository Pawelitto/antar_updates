import os
import requests
import pandas as pd
from ftplib import FTP

print("Jaskon - Rozpoczęto pracę nad Jaskon...")

# URL do pliku CSV
url = "https://pliki.jaskon.pl/37aaYdqdQmtL5jRmieTqqMrakZg3vmyhMtpwWFXXW7HjyX7eKKJHuZLRFH3nZv7C/jaskon.csv"

# Pobranie pliku CSV
response = requests.get(url, verify=False)
if response.status_code == 200:
    with open("jaskon.csv", 'wb') as file:
        file.write(response.content)
else:
    print("Jaskon - Nie udało się pobrać pliku CSV.")
    exit()

# Wczytanie pliku CSV do DataFrame
df = pd.read_csv("jaskon.csv", sep=';', encoding='ISO-8859-1', skiprows=1)

# Zmiana nazw kolumn: 'Symbol' oraz 'Stany'
df_selected = df[['Symbol', 'Stany']]
df_selected['Stany'] = df_selected['Stany'].apply(lambda x: True if x != 0 else False)

# Zapisanie wynikowego pliku w formacie Excel
output_path = 'jaskon.xlsx'
df_selected.to_excel(output_path, index=False, engine='openpyxl')

# Połączenie z serwerem FTP
ftp_server = 'ftp.antar.pl'
ftp_login = 'jaskon'
ftp_password = 'Kp!7EcqGafVR2'

try:
    # Nawiązanie połączenia z serwerem FTP
    ftp = FTP(ftp_server)
    ftp.login(ftp_login, ftp_password)
    
    # Przejście do folderu 'data'
    ftp.cwd('data')
    
    # Otwieranie pliku i przesyłanie go na serwer FTP
    with open(output_path, 'rb') as file:
        ftp.storbinary(f'STOR {output_path}', file)
    
    print(f"Jaskon - Plik '{output_path}' został pomyślnie zapisany na serwerze FTP w folderze 'data'.")

    # Zamknięcie połączenia FTP
    ftp.quit()
    
    # Usunięcie lokalnego pliku po przesłaniu
    os.remove(output_path)
    os.remove('jaskon.csv')

except Exception as e:
    print(f'Jaskon - Wystąpił błąd podczas połączenia z FTP lub przesyłania pliku: {e}')