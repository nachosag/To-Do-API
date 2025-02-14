from typing import Annotated
from fastapi import Depends
from jose import jwt
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select
from src.models.database import SessionDep
from src.models.models import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


def encode_token(payload: dict) -> str:
    token = jwt.encode(payload, "my-secret", algorithm="HS256")
    return token


def decode_token(
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> dict:
    data = jwt.decode(token, "my-secret", algorithms=["HS256"])
    user = session.exec(select(User).where(User.email == data["email"])).one()
    return user


Token = Annotated[dict, Depends(decode_token)]
