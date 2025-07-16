from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .ardon import run_ardon
from .cerva import run_cerva
from .hermon import run_hermon
from .jaskon import run_jaskon
from .portwest import run_portwest
from .ftptest import test_upload_ardon_csv
from .test_socket import test_ftp_connection

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API działa!"}

@app.get("/sockettest")
def sockettest_route():
    result = test_ftp_connection('ftp.antar.pl')
    return JSONResponse(result)

@app.get("/ftptest")
def ftptest_route():
    result = test_upload_ardon_csv()
    return JSONResponse(result)

@app.get("/ardon")
def ardon_route():
    result = run_ardon()
    return JSONResponse(result)

@app.get("/cerva")
def cerva_route():
    result = run_cerva()
    return JSONResponse(result)

@app.get("/hermon")
def hermon_route():
    result = run_hermon()
    return JSONResponse(result)

@app.get("/jaskon")
def jaskon_route():
    result = run_jaskon()
    return JSONResponse(result)

@app.get("/portwest")
def portwest_route():
    result = run_portwest()
    return JSONResponse(result)