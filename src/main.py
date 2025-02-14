from fastapi import FastAPI
from src.routers.task_router import task_router
from src.routers.user_router import user_router
from src.models.database import lifespan

app = FastAPI(lifespan=lifespan, title="To-Do-List-API")
app.include_router(router=task_router, prefix="/todos")
app.include_router(router=user_router, prefix="/users")
