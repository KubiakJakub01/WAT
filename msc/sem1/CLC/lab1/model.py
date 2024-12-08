'''Database model and CRUD operations'''
from datetime import datetime

from database import Base
from pydantic import BaseModel, ValidationError
from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.orm import Session

from .publisher import TOPICS


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)
    value = Column(Float)
    added_at = Column(DateTime)

    def __post_init__(self):
        self.added_at = datetime.now()
        if self.topic not in TOPICS:
            raise ValidationError(f'Invalid topic: {self.topic}')


class ItemCreate(BaseModel):
    topic: str
    value: float


def get_item(db: Session, item_id: int):
    return db.query(Item).filter(Item.id == item_id).first()


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Item).offset(skip).limit(limit).all()


def create_item(db: Session, item: ItemCreate):
    db_item = Item(topic=item.topic, value=item.value)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_item(db: Session, item_id: int, item: ItemCreate):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    db_item.topic = item.topic
    db_item.value = item.value
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_item(db: Session, item_id: int):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    db.delete(db_item)
    db.commit()
    return db_item