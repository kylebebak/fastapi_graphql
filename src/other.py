from typing import Optional, List
import asyncio

from fastapi import FastAPI
from pydantic import BaseModel
from starlette.websockets import WebSocket

from src.bus import Bus
from src.redis_app import get_subscriber, redis_send


CHANNEL = "main"
app = FastAPI()
websockets: List[WebSocket] = []
bus = Bus()


class Item(BaseModel):
    name: str
    price: float
    is_offer: Optional[bool] = None


# in-memory
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
    await bus.send(item.json(), CHANNEL)
    return {"item": item}


@app.websocket("/ws_bus")
async def ws_bus(websocket: WebSocket):
    await websocket.accept()
    bus.add(websocket, CHANNEL)
    while True:
        data = await websocket.receive_text()
        await bus.send(data, CHANNEL)


# redis bus
@app.post("/ws/write_redis_bus")
async def post_ws_redis_bus(item: Item):
    await redis_send(CHANNEL, item.json())
    return {"item": item}


@app.websocket("/ws_redis_bus")
async def ws_redis_bus(websocket: WebSocket):
    await websocket.accept()

    async def pub():
        while True:
            data = await websocket.receive_text()
            await redis_send(CHANNEL, data)

    await asyncio.gather(asyncio.create_task(pub()), asyncio.create_task(sub(CHANNEL, websocket)))


async def sub(ch: str, websocket: WebSocket):
    _, subscriber = await get_subscriber(ch)

    while True:
        text = await subscriber.get(encoding="utf-8")
        await websocket.send_text(text)
