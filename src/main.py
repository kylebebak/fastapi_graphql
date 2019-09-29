from typing import Optional, List, AsyncIterator
import asyncio
import base64

from fastapi import FastAPI
from starlette.responses import StreamingResponse, Response
from starlette.requests import Request
from starlette.graphql import GraphQLApp
import httpx
import graphene  # type: ignore
from graphql.execution.executors.asyncio import AsyncioExecutor  # type: ignore
from pydantic import BaseModel
from starlette.websockets import WebSocket, WebSocketDisconnect

from src.redis_app import get_redis, get_subscriber
from src.models import db, Users, Addresses
from src import gql


CHANNEL = "main"
app = FastAPI()
app.add_route(
    "/graphql",
    GraphQLApp(schema=graphene.Schema(query=gql.Query), executor_class=AsyncioExecutor),
)


class Item(BaseModel):
    name: str
    price: float
    is_offer: Optional[bool] = None


class UserIn(BaseModel):
    name: str
    age: int


class User(BaseModel):
    id: int
    name: str
    age: int


def httpx_to_starlette_response(res: httpx.AsyncResponse) -> Response:
    headers = dict(res.headers)
    headers.pop("content-length", None)
    headers.pop("content-encoding", None)
    return Response(res.content, status_code=res.status_code, headers=headers)


@app.middleware("http")
async def proxy_to_httpbin(request: Request, call_next):
    client = httpx.AsyncClient()
    if "/proxy/" in request.url.path:
        res = await client.get(f"https://httpbin.org/get?proxy={request.url.path}")
        return httpx_to_starlette_response(res)
    else:
        return await call_next(request)


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
    except Exception as e:
        print(e)
        return


async def ws_frames() -> AsyncIterator[bytes]:
    i = 0
    while True:
        b = open(f"src/assets/{(i % 3) + 1}" + ".jpg", "rb").read()
        yield base64.b64encode(b)
        await asyncio.sleep(0.2)
        i += 1
        print(f"yielded frame {i}")


async def frames() -> AsyncIterator[bytes]:
    for i in range(30):
        b = open(f"src/assets/{(i % 3) + 1}" + ".jpg", "rb").read()
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + b + b"\r\n"
        )
        await asyncio.sleep(0.2)
        i += 1
        print(f"yielded frame {i}")


@app.websocket("/ws_video")
async def ws_video(ws: WebSocket):
    await ws.accept()

    async for frame in ws_frames():
        await ws.send_text(frame.decode("utf-8"))


@app.get("/video")
async def video():
    return StreamingResponse(
        frames(), headers={"Content-Type": "multipart/x-mixed-replace; boundary=frame"}
    )


@app.on_event("startup")
async def startup():
    await db.set_bind("postgresql://localhost/postgres")


@app.on_event("shutdown")
async def shutdown():
    await db.pop_bind().close()


@app.get("/users", response_model=List[User])
async def read_users():
    users = await Users.query.gino.all()
    return [user.__values__ for user in users]


@app.post("/users", response_model=User)
async def create_note(user: UserIn):
    user = await Users.create(name=user.name, age=user.age)
    return {**user.__values__}
