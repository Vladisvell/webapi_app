from sqlalchemy.orm import Session

import schemas
from models import Category, Item


# Category
def create_category(db: Session, schema: schemas.CategoryCreate):
    db_category = Category(**schema.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def get_categories(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Category).offset(skip).limit(limit).all()


def get_category(db: Session, category_id: int):
    return db.query(Category).filter_by(id=category_id).first()


def update_category(db: Session, category_id: int, category_data: schemas.CategoryUpdate | dict):
    db_category = db.query(Category).filter_by(id=category_id).first()

    category_data = category_data if isinstance(category_data, dict) else category_data.model_dump()

    if db_category:
        for key, value in category_data.items():
            if hasattr(db_category, key):
                setattr(db_category, key, value)

        db.commit()
        db.refresh(db_category)

    return db_category


def delete_category(db: Session, category_id: int):
    db_category = db.query(Category).filter_by(id=category_id).first()
    if db_category:
        db.delete(db_category)
        db.commit()
        return True
    return False


# Item
def create_item(db: Session, schema: schemas.ItemCreate):
    db_item = Item(**schema.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_items(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Item).offset(skip).limit(limit).all()


def get_item(db: Session, item_id: int):
    return db.query(Item).filter_by(id=item_id).first()


def update_item(db: Session, item_id: int, item_data: schemas.ItemUpdate | dict):
    db_item = db.query(Item).filter_by(id=item_id).first()

    item_data = item_data if isinstance(item_data, dict) else item_data.model_dump()

    if db_item:
        for key, value in item_data.items():
            if hasattr(db_item, key):
                setattr(db_item, key, value)

        db.commit()
        db.refresh(db_item)
        return db_item
    return None


def delete_item(db: Session, item_id: int):
    db_item = db.query(Item).filter_by(id=item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
        return True
    return False
