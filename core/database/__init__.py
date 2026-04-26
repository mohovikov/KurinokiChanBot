from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from core.config import DATABASE_URL, DEBUG

engine = create_async_engine(url=DATABASE_URL, echo=DEBUG)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
