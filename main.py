from typing import Annotated
from fastapi import FastAPI, Depends, Query, Path
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from contextlib import asynccontextmanager
import sqlalchemy
from database import init_db, get_session
from models.models import PaginatedResponse, Task, UserCreate, TaskBase, User
from sqlmodel import Session, func, select
from jose import jwt


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan, title="To-Do-List-API")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
SessionDep = Annotated[Session, Depends(get_session)]


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


@app.get("/users/profile")
async def profile(token: Token):
    return token


@app.post("/login")
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


# tiene que retornar el token
@app.post("/register", response_model=User)
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


@app.get("/users", response_model=list[User])
async def get_users(
    session: SessionDep,
    token: Token,
):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    response = session.exec(select(User)).all()

    return response


@app.post("/todos", response_model=Task)
async def create_task(
    session: SessionDep,
    token: Token,
    task: TaskBase,
):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    data = Task(
        title=task.title,
        description=task.description,
    )

    session.add(data)
    session.commit()
    session.refresh(data)

    return data


@app.put("/todos/{task_id}", response_model=Task)
async def update_task(session: SessionDep, token: Token, task: Task):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        data = session.exec(select(Task).where(Task.id == task.id)).one()
    except sqlalchemy.exc.NoResultFound:
        raise HTTPException(status_code=404, detail="Task not found")

    data.title = task.title
    data.description = task.description

    session.add(data)
    session.commit()
    session.refresh(data)

    return data


@app.delete("/todos/{task_id}")
async def delete_task(
    session: SessionDep,
    token: Token,
    task_id: int = Path(ge=1, le=100),
):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        data = session.exec(select(Task).where(Task.id == task_id)).one()
    except sqlalchemy.exc.NoResultFound:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(data)
    session.commit()

    return HTTPException(status_code=204, detail="Task deleted successfully")


@app.get("/todos", response_model=PaginatedResponse)
async def get_tasks(
    session: SessionDep,
    token: Token,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    offset = (page - 1) * limit

    tasks = session.exec(select(Task).offset(offset).limit(limit)).all()
    total_tasks = session.exec(select(func.count(Task.id))).one()

    return PaginatedResponse(
        tasks=tasks,
        total_tasks=total_tasks,
        page=page,
        limit=limit,
    )
