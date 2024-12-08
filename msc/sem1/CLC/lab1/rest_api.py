'''Rest api using FastApi

Run with:
    uvicorn rest_api:app --reload
'''
import csv

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

TSV_FILE = 'data.tsv'

class Item(BaseModel):
    '''Item model'''
    id: int
    name: str
    value: float

    class Config:
        json_schema_extra = {
            'example': {
                'id': 1,
                'name': 'Sample Item',
                'value': 10.99
            }
        }


def read_data():
    '''Function to read data from TSV file'''
    with open(TSV_FILE, mode='r', newline='') as file:
        reader = csv.DictReader(file, delimiter='\t')
        return [Item(**row) for row in reader]


def write_data(items):
    '''Function to write data to TSV file'''
    with open(TSV_FILE, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'name', 'value'], delimiter='\t')
        writer.writeheader()
        for item in items:
            writer.writerow(item.dict())


@app.get('/')
async def root():
    '''GET method to retrieve root'''
    return {'message': 'Hello World!'}


@app.get('/items', response_model=list[Item])
async def get_items():
    '''GET method to retrieve all entries'''
    return read_data()


@app.get('/items/{item_id}', response_model=Item)
async def get_item(item_id: int):
    '''GET method to retrieve a specific entry'''
    items = read_data()
    item = next((item for item in items if item.id == item_id), None)
    if item:
        return item
    raise HTTPException(status_code=404, detail='Item not found')


@app.post('/items', response_model=Item)
async def add_item(item: Item):
    '''POST method to add a new entry'''
    items = read_data()
    if any(existing_item.id == item.id for existing_item in items):
        raise HTTPException(status_code=400, detail='Item with this ID already exists')
    items.append(item)
    write_data(items)
    return item


@app.put('/items/{item_id}', response_model=Item)
async def update_item(item_id: int, updated_item: Item):
    '''PUT method to update an existing entry'''
    items = read_data()
    for idx, item in enumerate(items):
        if item.id == item_id:
            items[idx] = updated_item
            write_data(items)
            return updated_item
    raise HTTPException(status_code=404, detail='Item not found')


@app.delete('/items/{item_id}')
async def delete_item(item_id: int):
    '''DELETE method to delete an existing entry'''
    items = read_data()
    for idx, item in enumerate(items):
        if item.id == item_id:
            del items[idx]
            write_data(items)
            return {'message': 'Item deleted'}
    raise HTTPException(status_code=404, detail='Item not found')
