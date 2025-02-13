from sqlmodel import SQLModel, Session, create_engine

url = "sqlite:///todo-list.db"
engine = create_engine(url, connect_args={"check_same_thread": False})


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session