import os
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from ftplib import FTP

print("Ardon - Rozpoczęto pracę nad Ardon...")

# URL do pliku XML
url = "https://www.ardon.pl/data-feed/ff2042f7-5fe8-4fbf-988d-335b1e8bb0e8"

# Pobranie pliku XML
response = requests.get(url, verify=False)
if response.status_code == 200:
    with open("ardon.xml", 'wb') as file:
        file.write(response.content)
else:
    print("Ardon - Nie udało się pobrać pliku XML.")
    exit()

# Parsowanie pliku XML
tree = ET.parse('ardon.xml')
root = tree.getroot()

# Inicjalizacja list na dane
item_codes = []
amounts_in_stock = []

# Iteracja po elementach SHOPITEM i wyciąganie potrzebnych danych
for item in root.findall('.//SHOPITEM'):
    item_code = item.find('ITEM_CODE').text
    amount_in_stock = item.find('AMOUNT_IN_STOCK').text
    
    item_codes.append(item_code)
    amounts_in_stock.append(amount_in_stock)

# Tworzenie DataFrame z wyciągniętych danych
df = pd.DataFrame({
    'Kod': item_codes,
    'SoH': amounts_in_stock
})

# Modyfikacja kolumny 'SoH'
df['SoH'] = df['SoH'].apply(lambda x: True if int(x) > 0 else False)

# Zapisanie wynikowego pliku w formacie Excel do bufora w pamięci
output_path = 'ardon.xlsx'
df.to_excel(output_path, index=False, engine='openpyxl')

# Dane dostępowe do serwera FTP
ftp_server = 'ftp.antar.pl'
ftp_login = 'ardon'
ftp_password = '4_SHAXsqdAsp'

try:
    ftp = FTP(ftp_server)
    ftp.login(ftp_login, ftp_password)
    ftp.cwd('data')
    
    with open(output_path, 'rb') as file:
        ftp.storbinary(f'STOR {output_path}', file)

    print(f"Ardon - Plik '{output_path}' został pomyślnie zapisany na serwerze FTP.")
    ftp.quit()

except Exception as e:
    print(f'Wystąpił błąd podczas połączenia z FTP lub przesyłania pliku: {e}')

finally:
    for file_path in ['ardon.xml', output_path]:
        if os.path.exists(file_path):
            os.remove(file_path)
