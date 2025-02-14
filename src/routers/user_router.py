from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from src.models.database import SessionDep
from src.models.models import User, UserCreate
from src.token import Token, encode_token

user_router = APIRouter(tags=["Users"])


@user_router.get("/profile")
async def profile(token: Token):
    return token


@user_router.post("/login")
async def login(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    try:
        user = session.exec(
            select(User).where(
                (User.email == form_data.username)
                & (User.password == form_data.password)
            )
        ).one()
    except Exception:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    token = encode_token({"username": user.name, "email": user.email})

    return {
        "access_token": token,
    }


@user_router.post("/register", response_model=User)
async def register_user(
    session: SessionDep,
    user: UserCreate,
):
    data = User(
        email=user.email,
        password=user.password,
        name=user.name,
    )

    session.add(data)
    session.commit()
    session.refresh(data)

    return data


@user_router.get("/", response_model=list[User])
async def get_users(
    session: SessionDep,
    token: Token,
):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    response = session.exec(select(User)).all()

    return response
