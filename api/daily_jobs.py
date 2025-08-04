from ardon import run_ardon
from cerva import run_cerva
from hermon import run_hermon
from jaskon import run_jaskon
from portwest import run_portwest

def main():
    print("Start jobów")
    try:
        print("Run Ardon:", run_ardon())
        print("Run Cerva:", run_cerva())
        print("Run Hermon:", run_hermon())
        print("Run Jaskon:", run_jaskon())
        print("Run Portwest:", run_portwest())
        print("Wszystkie zadania zakończone")
    except Exception as e:
        print("Błąd podczas wykonywania zadań:", e)

if __name__ == "__main__":
    main()
