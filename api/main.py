from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .ardon import run_ardon

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API działa!"}

@app.get("/ardon")
def ardon_route():
    result = run_ardon()
    return JSONResponse(result)
