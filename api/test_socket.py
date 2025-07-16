import socket
import traceback

def test_ftp_connection(host, port=21):
    try:
        sock = socket.create_connection((host, port), timeout=10)
        sock.close()
        return {"status": "Połączenie powiodło się"}
    except Exception as e:
        print(traceback.format_exc())
        return {"status": f"Błąd połączenia: {e}"}


