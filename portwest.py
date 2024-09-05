import os
import requests
import pandas as pd
from ftplib import FTP

print("Portwest - Rozpoczęto pracę nad Portwest...")

# URL do pliku CSV
url = "http://d11ak7fd9ypfb7.cloudfront.net/marketing_files/simple_soh/simpleSOH20.csv"

# Pobranie pliku CSV
response = requests.get(url)
if response.status_code == 200:
    with open("portwest.csv", 'wb') as file:
        file.write(response.content)
else:
    print("Portwest - Nie udało się pobrać pliku CSV.")
    exit()

# Wczytanie pliku CSV do DataFrame
df = pd.read_csv("portwest.csv")

# Zmiana nazw kolumn: 'Item' na 'Symbol', 'SoH' na 'Stany'
df.rename(columns={'Item': 'Symbol', 'SoH': 'Stany'}, inplace=True)

# Modyfikacja kolumny 'Stany': zamiana liczby na 'dostępny' lub 'niedostępny'
df['Stany'] = df['Stany'].apply(lambda x: True if x > 0 else False)

# Utworzenie podkatalogu 'data' jeżeli nie istnieje
if not os.path.exists('data'):
    os.makedirs('data')

# Zapisanie wynikowego pliku w formacie Excel w podkatalogu 'data'
output_file = 'portwest.xlsx'
df.to_excel(output_file, index=False, engine='openpyxl')

# Połączenie z serwerem FTP
ftp_server = 'ftp.antar.pl'
ftp_login = 'portwest'
ftp_password = 'zSPnQ4n!'

try:
        # Nawiązanie połączenia z serwerem FTP
        ftp = FTP(ftp_server)
        ftp.login(ftp_login, ftp_password)
        
        # Przejście do folderu 'data' na serwerze FTP
        ftp.cwd('data')

        # Otwieranie pliku i przesyłanie go na serwer FTP
        with open(output_file, 'rb') as file:
            ftp.storbinary(f'STOR portwest.xlsx', file)
        
        print(f"Portwest - Plik '{output_file}' został pomyślnie zapisany na serwerze FTP w folderze 'data'.")

        # Zamknięcie połączenia FTP
        ftp.quit()
        
        # Usunięcie lokalnego pliku po przesłaniu
        os.remove(output_file)
        os.remove('portwest.csv')

except Exception as e:
        print(f'Portwest - Wystąpił błąd podczas połączenia z FTP lub przesyłania pliku: {e}')

print(f"Portwest - Proces dla Portwest zakończony pomyślnie. Plik zapisano jako {output_file}.")