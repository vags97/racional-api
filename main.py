from fastapi import FastAPI
from src.router import router
from src.database import Base, engine
from src.config import APP_ENV
from src.migration_examples import create_examples

if APP_ENV == 'DEV':
    Base.metadata.create_all(bind=engine)
    create_examples()

app = FastAPI()

app.include_router(router)