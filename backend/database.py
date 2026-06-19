from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.settings import settings
import asyncio
from functools import partial

engine = create_engine(settings.BASE_DIR.joinpath('security.db').as_uri().replace('file://', 'sqlite:///'))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


async def init_db():
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, partial(Base.metadata.create_all, bind=engine))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
