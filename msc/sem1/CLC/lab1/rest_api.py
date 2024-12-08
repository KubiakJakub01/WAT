import uvicorn
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .model import Item, ItemCreate, create_item

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/')
async def root():
    '''GET method to retrieve root'''
    return {'message': 'Hello World!'}


@app.get('/items', response_model=list[Item])
async def get_items(db: Session = Depends(get_db)):
    '''GET method to retrieve all entries'''
    return db.query(Item).all()


@app.post('/items', response_model=Item)
async def create_new_item(item: ItemCreate, db: Session = Depends(get_db)):
    '''POST method to create a new item'''
    return create_item(db, item)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
