from typing import Optional, AsyncIterator
import asyncio
import random

from fastapi import FastAPI
from starlette.responses import StreamingResponse
from pydantic import BaseModel
from starlette.websockets import WebSocket, WebSocketDisconnect

from src.redis import get_redis, get_subscriber


CHANNEL = "main"
app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    is_offer: Optional[bool] = None


# redis
@app.post("/ws/write_redis")
async def post_ws_redis(item: Item):
    redis = await get_redis()
    await redis.publish(CHANNEL, item.json())
    return {"item": item}


@app.websocket("/ws_redis")
async def ws_redis(ws: WebSocket):
    """https://stackoverflow.com/questions/31623194/asyncio-two-loops-for-different-i-o-tasks
    """
    await ws.accept()
    _, subscriber = await get_subscriber(CHANNEL)
    redis = await get_redis()

    async def pub():
        while True:
            data = await ws.receive_text()
            await redis.publish(CHANNEL, data)

    async def sub():
        while True:
            text = await subscriber.get(encoding="utf-8")
            await ws.send_text(text)

    try:
        await asyncio.gather(asyncio.create_task(pub()), asyncio.create_task(sub()))
    except WebSocketDisconnect:
        print(f"{ws} disconnected")


async def frames() -> AsyncIterator[bytes]:
    i = 0
    while True:
        b = open(f'src/assets/{(i % 3) + 1}' + '.jpg', 'rb').read()
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + b + b"\r\n"
        )
        await asyncio.sleep(0.2)
        i += 1


@app.get("/video")
async def video():
    return StreamingResponse(
        frames(), headers={"Content-Type": "multipart/x-mixed-replace; boundary=frame"}
    )
