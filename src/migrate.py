import asyncio

from src.models import db


async def main():
    await db.set_bind("postgresql://localhost/postgres")
    await db.gino.create_all()
    await db.pop_bind().close()


asyncio.run(main())
