import os
import tempfile
import pandas as pd
from ftplib import FTP
from dotenv import load_dotenv

load_dotenv()

def test_upload_ardon_csv():
    tmp_dir = tempfile.gettempdir()
    output_file = os.path.join(tmp_dir, 'TEST_FTP.csv')

    # Tworzenie testowych danych
    data = [
        {'ARTYKUL': 'TEST001', 'DOSTEPNOSC': 'TAK'},
        {'ARTYKUL': 'TEST002', 'DOSTEPNOSC': 'NIE'},
        {'ARTYKUL': 'TEST003', 'DOSTEPNOSC': 'TAK'},
    ]

    df = pd.DataFrame(data)

    # Zapis do CSV z formatowaniem
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('ARTYKUL|"DOSTEPNOSC"\n')
        for _, row in df.iterrows():
            f.write(f'{row["ARTYKUL"]}|"{row["DOSTEPNOSC"]}"\n')

    print(f"Testowy plik CSV utworzony: {output_file}")

    # Pobranie danych do FTP z .env
    ftp_server = os.getenv('FTP_HOST')
    ftp_user = os.getenv('ARDON_FTP_USER')
    ftp_pass = os.getenv('ARDON_FTP_PASS')

    # Wysyłka na FTP
    try:
        ftp = FTP()
        ftp.connect(ftp_server, 21)
        ftp.login(ftp_user, ftp_pass)
        ftp.set_pasv(True)

        with open(output_file, 'rb') as f:
            ftp.storbinary(f'STOR {os.path.basename(output_file)}', f)

        ftp.quit()
        return {"status": "success", "message": "Testowy plik został wysłany na FTP."}
    except Exception as e:
        return {"status": "error", "message": str(e)}