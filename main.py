import os

def run_ardon():
    print("Uruchamianie skryptu ardon.py...")
    os.system('python3 /app/ardon.py')
    print("Skrypt ardon.py został zakończony.\n")

def run_jaskon():
    print("Uruchamianie skryptu jaskon.py...")
    os.system('python3 /app/jaskon.py')
    print("Skrypt jaskon.py został zakończony.\n")

def run_portwest():
    print("Uruchamianie skryptu portwest.py...")
    os.system('python3 /app/portwest.py')
    print("Skrypt portwest.py został zakończony.\n")

def run_hermon():
    print("Uruchamianie skryptu hermon.py...")
    os.system('python3 /app/hermon.py')
    print("Skrypt hermon.py został zakończony.\n")

def run_cerva():
    print("Uruchamianie skryptu cerva.py...")
    os.system('python3 /app/cerva.py')
    print("Skrypt cerva.py został zakończony.\n")

def run_all_scripts():
    print("=== Rozpoczęcie uruchamiania wszystkich skryptów ===")
    run_ardon()
    run_jaskon()
    run_portwest()
    run_hermon()
    run_cerva()
    print("=== Wszystkie skrypty zostały uruchomione ===\n")

run_all_scripts()