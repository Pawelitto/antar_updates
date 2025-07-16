import socket

def test_ftp_connection(host, port=21):
    try:
        sock = socket.create_connection((host, port), timeout=10)
        sock.close()
        return {"status": "Połączenie powiodło się"}
    except Exception as e:
        return {"status": "Błąd połączenia: {e}"}

