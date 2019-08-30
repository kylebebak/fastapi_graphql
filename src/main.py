from typing import Optional, List
import asyncio

from fastapi import FastAPI
from pydantic import BaseModel
from starlette.websockets import WebSocket

from src.bus import Bus


app = FastAPI()
websockets: List[WebSocket] = []
bus = Bus()


class Item(BaseModel):
    name: str
    price: float
    is_offer: Optional[bool] = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}


# in-memory list
@app.post("/ws/write")
async def post_ws(item: Item):
    global websockets
    for ws in websockets:
        await ws.send_text(item.json())
    return {"item": item}


@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    global websockets
    websockets.append(websocket)
    while True:
        data = await websocket.receive_text()
        for ws in websockets:
            await ws.send_text(f"message text was: {data}")


# in-memory bus
@app.post("/ws/write_bus")
async def post_ws_bus(item: Item):
    await bus.send(item.json(), 'main')
    return {"item": item}


@app.websocket("/ws_bus")
async def ws_bus(websocket: WebSocket):
    await websocket.accept()
    bus.add(websocket, 'main')
    while True:
        data = await websocket.receive_text()
        bus.send(data, 'main')


# redis bus
@app.post("/ws/write_redis")
async def post_ws_redis(item: Item):
    global websockets
    for ws in websockets:
        await ws.send_text(item.json())
    return {"item": item}


@app.websocket("/ws_redis")
async def ws_redis(websocket: WebSocket):
    await websocket.accept()
    global websockets
    websockets.append(websocket)
    while True:
        data = await websocket.receive_text()
        for ws in websockets:
            await ws.send_text(f"message text was: {data}")
