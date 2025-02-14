from typing import List
from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    email: str
    password: str


class UserCreate(UserBase):
    name: str


class TaskBase(SQLModel):
    title: str
    description: str


# Database models
class Task(TaskBase, table=True):
    id: int = Field(default=None, primary_key=True)


class User(UserCreate, table=True):
    id: int = Field(default=None, primary_key=True)


# Response models
class PaginatedResponse(BaseModel):
    tasks: List[Task]
    total_tasks: int
    page: int
    limit: int
