from sqlmodel import SQLModel, Relationship, Field


class Task(SQLModel, table=True):
    id: int = Field(primary_key=True)
    title: str
    description: str
    owner_id: int | None = Field(foreign_key="user.id")
    owner: "User" = Relationship(back_populates="tasks")


class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    email: str
    password: str
    name: str
    tasks: list[Task] | None = Relationship(back_populates="owner")