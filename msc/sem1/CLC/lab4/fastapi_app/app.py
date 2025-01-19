from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/hello")
async def hello():
    return {"message": "Hello from FastAPI (Etap I)"}

@app.post("/items")
async def create_item(request: Request):
    data = await request.json()
    return {"received_data": data}


@app.get("/status")
async def status():
    return {"status": "OK", "message": "Nowy GET endpoint (Etap II)"}


@app.post("/process")
async def process_data(request: Request):
    data = await request.json()
    return {"status": "processed", "input_data": data}
