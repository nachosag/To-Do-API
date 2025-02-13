from typing import Annotated, List
from fastapi import FastAPI, Depends, HTTPException, Query, Path
from contextlib import asynccontextmanager
import sqlalchemy
from database import init_db, get_session
from models.models import PaginatedResponse, UserBase, Task, UserCreate, TaskBase
from sqlmodel import Session, func, select


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan, title="To-Do-List-API")
SessionDep = Annotated[Session, Depends(get_session)]


@app.post("/register", response_model=str)
async def register_user(session: SessionDep, user: UserCreate):
    pass


@app.post("/login", response_model=str)
async def login_user(session: SessionDep, user: UserBase):
    pass


@app.post("/todos", response_model=Task)
async def create_task(session: SessionDep, task: TaskBase):
    data = Task(
        title=task.title,
        description=task.description,
    )

    session.add(data)
    session.commit()
    session.refresh(data)

    return data


@app.put("/todos/{task_id}", response_model=Task)
async def update_task(session: SessionDep, task: Task):
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
async def delete_task(session: SessionDep, task_id: int = Path(ge=1, le=100)):
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
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
):
    offset = (page - 1) * limit

    tasks = session.exec(select(Task).offset(offset).limit(limit)).all()
    total_tasks = session.exec(select(func.count(Task.id))).one()

    return PaginatedResponse(
        tasks=tasks,
        total_tasks=total_tasks,
        page=page,
        limit=limit,
    )
