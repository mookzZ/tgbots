from sqlalchemy import select
from sqlalchemy import text
from database import engine, User, Base, async_session


async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def add_user(action: str, user_id: int, name: str):
    async with async_session() as session:
        async with session.begin():
            user = User(action=action, user_id=user_id, name=name)
            session.add(user)
        await session.commit()

async def get_user(limit: int | None = None):
    async with async_session() as session:
        result = await session.execute(text(f"SELECT * FROM user LIMIT {limit}"))
        a = ""
        for row in result:
            a += f"{row}\n"
        print(a)
        return a

async def get_filter_user(input_id: int):
    async with async_session() as session:
        stmt = select(User).where(User.user_id == input_id).order_by(User.created_at.desc())
        result = await session.execute(stmt)
        rows = result.scalars()
        output = ""
        for user in rows:
            output += f"ID: {user.user_id}\nИмя: {user.name}\nДата создания: {user.created_at}\n"
            output += "\n"
        return output

async def delete_user(user_id: int):
    async with async_session() as session:
        async with session.begin():
            stmt = select(User).where(User.user_id == user_id)
            result = await session.execute(stmt)
            user = result.scalars().first()
            if user is None:
                return
            await session.delete(user)
            await session.commit()
