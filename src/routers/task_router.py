from fastapi import HTTPException, APIRouter, Path, Query
import sqlalchemy
from sqlmodel import func, select
from src.token import Token
from src.models.database import SessionDep
from src.models.models import PaginatedResponse, Task, TaskBase

task_router = APIRouter(tags=["Todos"])


@task_router.post("/", response_model=Task)
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


@task_router.put("/{task_id}", response_model=Task)
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


@task_router.delete("/{task_id}")
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


@task_router.get("/", response_model=PaginatedResponse)
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
