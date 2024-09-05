import os
import pandas as pd
import requests
import json
from ftplib import FTP

# Wczytanie pliku Excel
file_path = 'common_kody.xlsx'  # Podaj ścieżkę do pliku

try:
    # Wczytywanie danych z pliku Excel
    excel_data = pd.read_excel(file_path)
    print("Hermon - Plik został wczytany pomyślnie.")
except FileNotFoundError:
    print(f"Hermon - Plik {file_path} nie został znaleziony.")
    exit()
except Exception as e:
    print(f"Hermon - Wystąpił błąd podczas wczytywania pliku: {e}")
    exit()

# Sprawdzenie, czy kolumna "Kod towaru" istnieje
if 'Kod towaru' not in excel_data.columns:
    print("Hermon - Brak kolumny 'Kod towaru' w pliku.")
    exit()

# Pobranie kodów z kolumny "Kod towaru"
kody_towaru = excel_data['Kod towaru'].tolist()

# Dane do autoryzacji
auth_url = "http://78.31.93.254:81/client-service/authenticate"
auth_data = {
    "Login": "018249",
    "Password": "Antar-12345"
}

ftp_server = 'ftp.antar.pl'
ftp_login = 'hermon'
ftp_password = '#frJv8PmL'

# Wysyłanie żądania POST do uzyskania tokena
try:
    auth_response = requests.post(auth_url, json=auth_data)
    if auth_response.status_code == 200:
        auth_json = auth_response.json()
        token = auth_json.get('token', None)
        if not token:
            print("Hermon - Nie udało się uzyskać tokenu autoryzacyjnego.")
            exit()
        print("Hermon - Token autoryzacyjny uzyskany pomyślnie.")
    else:
        print("Hermon - Błąd przy uzyskiwaniu tokenu autoryzacyjnego:", auth_response.status_code)
        print("Hermon - Szczegóły błędu:", auth_response.text)
        exit()
except requests.exceptions.RequestException as e:
    print(f"Hermon - Wystąpił błąd przy uzyskiwaniu tokenu autoryzacyjnego: {e}")
    exit()

# Nagłówki zapytania z uzyskanym tokenem
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# URL endpointu do wysłania zapytania o artykuły
url = "http://78.31.93.254:81/client-service/articles"

# Wysyłanie żądania POST z tokenem
try:
    response = requests.post(url, json=kody_towaru, headers=headers)
    
    # Sprawdzanie odpowiedzi serwera
    if response.status_code == 200:
        print("Hermon - Zapytanie wysłane pomyślnie.")
        
        # Przetwarzanie odpowiedzi serwera bez zapisywania do pliku JSON
        data = response.json()

        # Przygotowanie list do przechowywania wyników
        ids = []
        availability = []

        # Przetwarzanie danych z pominięciem brakujących id
        for item in data:
            # Wyciągnięcie wartości id
            item_id = item.get('id', None)
            if item_id is None:
                continue  # Pomijanie elementów bez kodu

            # Wyciągnięcie wartości quantity z branchesAvailability
            branches_availability = item.get('branchesAvailability', [])
            # Domyślnie ustawienie availability jako False
            is_available = False
            if branches_availability:
                quantity = branches_availability[0].get('quantity', '0')
                # Sprawdzenie, czy quantity jest różne od "0"
                is_available = quantity != '0'
            
            # Dodanie wyników do list
            ids.append(item_id)
            availability.append(is_available)

        # Stworzenie DataFrame
        df = pd.DataFrame({'Kod': ids, 'SoH': availability})

        # Zapisanie wyników do pliku Excel
        output_file = 'hermon.xlsx'
        df.to_excel(output_file, index=False)

        try:
            # Nawiązanie połączenia z serwerem FTP
            ftp = FTP(ftp_server)
            ftp.login(ftp_login, ftp_password)
            
            # Przejście do folderu 'data' na serwerze FTP
            ftp.cwd('data')

            # Otwieranie pliku i przesyłanie go na serwer FTP
            with open(output_file, 'rb') as file:
                ftp.storbinary(f'STOR hermon.xlsx', file)
            
            print(f"Hermon - Plik '{output_file}' został pomyślnie zapisany na serwerze FTP w folderze 'data'.")

            # Zamknięcie połączenia FTP
            ftp.quit()
            
            # Usunięcie lokalnego pliku po przesłaniu
            os.remove(output_file)

        except Exception as e:
            print(f'Wystąpił błąd podczas połączenia z FTP lub przesyłania pliku: {e}')
        
        # Wyświetlenie wyników
        print(f"Hermon - Wynikowa analiza dostępności zapisana w: {output_file}")
    else:
        print("Hermon - Błąd przy wysyłaniu zapytania:", response.status_code)
        print("Hermon - Szczegóły błędu:", response.text)
except requests.exceptions.RequestException as e:
    print(f"Hermon - Wystąpił błąd przy wysyłaniu zapytania: {e}")