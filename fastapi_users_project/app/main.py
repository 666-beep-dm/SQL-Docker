from fastapi import FastAPI

from app.database import engine, Base
from app.routes import users
from app.models import user


app = FastAPI()


Base.metadata.create_all(bind=engine)


app.include_router(users.router)