from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine('sqlite+aiosqlite:///buzcoin.db', echo=True)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

