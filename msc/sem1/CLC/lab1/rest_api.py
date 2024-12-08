import uvicorn
from database import get_db
from fastapi import Depends, FastAPI, HTTPException
from model import (Item, ItemCreate, ItemResponse, create_item, delete_item,
                   get_item, update_item)
from sqlalchemy.orm import Session

app = FastAPI()


@app.get('/')
async def root():
    '''GET method to retrieve root'''
    return {'message': 'Hello World!'}


@app.get('/items', response_model=list[ItemResponse])
async def get_items(db: Session = Depends(get_db)):
    '''GET method to retrieve all entries'''
    item = db.query(Item).all()
    if not item:
        raise HTTPException(status_code=404, detail='No items found')
    return item


@app.post('/items', response_model=ItemResponse)
async def create_new_item(item: ItemCreate, db: Session = Depends(get_db)):
    '''POST method to create a new item'''
    return create_item(db, item)


@app.get('/items/{item_id}', response_model=ItemResponse)
async def get_item_by_id(item_id: int, db: Session = Depends(get_db)):
    '''GET method to retrieve an entry by ID'''
    item = get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail='Item not found')
    return item


@app.put('/items/{item_id}', response_model=ItemResponse)
async def update_item_by_id(item_id: int, item: ItemCreate, db: Session = Depends(get_db)):
    '''PUT method to update an entry by ID'''
    return update_item(db, item_id, item)


@app.delete('/items/{item_id}', response_model=ItemResponse)
async def delete_item_by_id(item_id: int, db: Session = Depends(get_db)):
    '''DELETE method to delete an entry by ID'''
    return delete_item(db, item_id)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
