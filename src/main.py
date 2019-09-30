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
from src.models import db, User, Address, AddressDetails
from src import gql


CHANNEL = "main"
app = FastAPI()
app.add_route(
    "/graphql",
    GraphQLApp(schema=graphene.Schema(query=gql.Query), executor_class=AsyncioExecutor),
)


class UserModel(BaseModel):
    id: int
    name: str
    age: int


class UserInModel(BaseModel):
    name: str
    age: int


class AddressInModel(BaseModel):
    user_id: int
    email_address: str


class AddressDetailsInModel(BaseModel):
    address_id: int
    details: str


def httpx_to_starlette_response(res: httpx.AsyncResponse) -> Response:
    headers = dict(res.headers)
    headers.pop("content-length", None)
    headers.pop("content-encoding", None)
    return Response(res.content, status_code=res.status_code, headers=headers)


@app.on_event("startup")
async def startup():
    await db.set_bind("postgresql://localhost/postgres")


@app.on_event("shutdown")
async def shutdown():
    await db.pop_bind().close()


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
async def post_ws_redis(user: UserModel):
    redis = await get_redis()
    await redis.publish(CHANNEL, user.json())
    return {"user": user}


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


@app.get("/users", response_model=List[UserModel])
async def read_users():
    objs = await User.query.gino.all()
    return [obj.__values__ for obj in objs]


@app.post("/users", response_model=UserModel)
async def create_user(user: UserInModel):
    obj = await User.create(name=user.name, age=user.age)
    return {**obj.__values__}


@app.post("/addresses")
async def create_address(address: AddressInModel):
    obj = await Address.create(user_id=address.user_id, email_address=address.email_address)
    return {**obj.__values__}


@app.post("/address_details")
async def create_address_details(details: AddressDetailsInModel):
    obj = await AddressDetails.create(address_id=details.address_id, details=details.details)
    return {**obj.__values__}
