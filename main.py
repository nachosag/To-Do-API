from typing import Annotated
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from database import init_db, get_session
from models.models import User
from sqlmodel import Session, select


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
SessionDep = Annotated[Session, Depends(get_session)]

@app.get("/")
async def root():
    return {"Message": "Welcome to my To-do-list API."}

@app.get("/users")
async def get_users(session: SessionDep) -> list[User]:
    users = session.exec(select(User)).all()
    return users


@app.post("/users")
async def create_user(user: User, session: SessionDep) -> User:
    user = User(
        id=user.id,
        email=user.email,
        password=user.password,
        name=user.name,
        tasks=user.tasks,
    )

    session.add(user)
    session.commit()
    session.refresh(user)
    return user
