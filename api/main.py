from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .ardon import run_ardon
from .cerva import run_cerva

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API działa!"}

@app.get("/ardon")
def ardon_route():
    result = run_ardon()
    return JSONResponse(result)

@app.get("/cerva")
def cerva_route():
    result = run_cerva()
    return JSONResponse(result)
