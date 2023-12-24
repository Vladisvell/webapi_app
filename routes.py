from typing import List

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from crud import (
    create_category, get_categories, get_category, update_category, delete_category,
    create_item, get_items, get_item, update_item, delete_item
)

import schemas
from database import get_db
from sqlalchemy.orm import Session


router_websocket = APIRouter()
router_categories = APIRouter(prefix='/categories', tags=['category'])
router_items = APIRouter(prefix='/items', tags=['item'])


# WebSocket
class ClientManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_private_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ClientManager()


async def notify_clients(message: str):
    for connection in manager.active_connections:
        await connection.send_text(message)


@router_websocket.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    await manager.broadcast(f"Кот #{client_id} присоединился к чату")
    try:
        while True:
            data = await websocket.receive_text()
            #await manager.send_private_message(f"Вы сказали: {data}", websocket)
            await manager.broadcast(f"Кот #{client_id} говорит: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Кот #{client_id} покинул чат")

# Категории
@router_categories.post("/", response_model=schemas.Category)
async def create_category_route(category_data: schemas.CategoryCreate, db: Session = Depends(get_db)):
    category = create_category(db, category_data)
    await notify_clients(f"Добавлена категория: {category.name}")
    return category


@router_categories.get("/", response_model=List[schemas.Category])
async def read_categories(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    categories = get_categories(db, skip=skip, limit=limit)
    return categories


@router_categories.get("/{category_id}", response_model=schemas.Category)
async def read_category(category_id: int, db: Session = Depends(get_db)):
    category = get_category(db, category_id)
    return category


@router_categories.patch("/{category_id}", response_model=schemas.Category)
async def update_category_route(category_id: int, category_data: schemas.CategoryUpdate, db: Session = Depends(get_db)):
    updated_category = update_category(db, category_id, category_data)
    if updated_category:
        await notify_clients(f"Категория обновлена: {updated_category.name}")
        return updated_category
    return {"message": "Category not found"}


@router_categories.delete("/{category_id}")
async def delete_category_route(category_id: int, db: Session = Depends(get_db)):
    deleted = delete_category(db, category_id)
    if deleted:
        await notify_clients(f"Категория удалена: ID {category_id}")
        return {"message": "Category deleted"}
    return {"message": "Category not found"}


# Товары
@router_items.post("/", response_model=schemas.Item)
async def create_item_route(schema: schemas.ItemCreate, db: Session = Depends(get_db)):
    item = create_item(db, schema)
    await notify_clients(f"Добавлен предмет: {item.name}")
    return item


@router_items.get("/", response_model=List[schemas.Item])
async def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    items = get_items(db, skip=skip, limit=limit)
    return items


@router_items.get("/{item_id}", response_model=schemas.Item)
async def read_item(item_id: int, db: Session = Depends(get_db)):
    item = get_item(db, item_id)
    return item


@router_items.patch("/{item_id}")
async def update_item_route(item_id: int, schema: schemas.ItemUpdate, db: Session = Depends(get_db)):
    updated_item = update_item(db, item_id, schema)
    if updated_item:
        await notify_clients(f"Предмет обновлен: {updated_item.name}")
        return updated_item
    return {"message": "Item not found"}


@router_items.delete("/{item_id}")
async def delete_item_route(item_id: int, db: Session = Depends(get_db)):
    deleted = delete_item(db, item_id)
    if deleted:
        await notify_clients(f"Предмет удален: ID {item_id}")
        return {"message": "Item deleted"}
    return {"message": "Item not found"}
