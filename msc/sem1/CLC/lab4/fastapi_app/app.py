from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
from models import Item

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/hello")
async def hello():
    return {"message": "Hello from FastAPI Etap III"}


@app.post("/items")
async def create_item(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    payload = data.get("mqtt_message", "")

    item = Item(payload=payload)
    db.add(item)
    db.commit()
    db.refresh(item)

    return {"status": "ok", "inserted_id": item.id, "payload": item.payload}


@app.get("/items")
def get_items(db: Session = Depends(get_db)):
    items = db.query(Item).all()
    results = [{"id": it.id, "payload": it.payload} for it in items]
    return {"items": results}


@app.get("/status")
async def status():
    return {"status": "OK", "message": "Nowy GET endpoint (Etap III + SQLAlchemy)"}


@app.post("/process")
async def process_data(request: Request):
    data = await request.json()
    processed = f"Data processed: {data}"
    return {"status": "processed", "data": processed}
