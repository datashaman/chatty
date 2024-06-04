from uuid import UUID, uuid4

from datetime import datetime
from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse


class Chat(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: UUID = Field(sa_column_kwargs={"unique": True}, nullable=False, index=True, default_factory=uuid4)
    title: str = Field(nullable=False, index=True)
    new_message: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: UUID = Field(sa_column_kwargs={"unique": True}, nullable=False, index=True, default_factory=uuid4)
    role: str
    content: str

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    chat_id: int = Field(foreign_key="chat.id")


sqlite_url = "sqlite:///./test.db"
engine = create_engine(sqlite_url, echo=True, connect_args={"check_same_thread": False})

app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    SQLModel.metadata.create_all(engine)


@app.get("/chats")
async def list_chats():
    with Session(engine) as session:
        return session.query(Chat).order_by(Chat.created_at.desc()).all()


@app.get("/chats/{uuid}")
async def get_chat(uuid: str):
    with Session(engine) as session:
        chat = session.query(Chat).filter(Chat.uuid == uuid).first()
        if chat is None:
            raise HTTPException(status_code=404, detail="Chat not found")
        return chat


@app.post("/chats")
async def create_chat(chat: Chat):
    with Session(engine) as session:
        session.add(chat)
        session.commit()
        session.refresh(chat)
        return chat


@app.patch("/chats/{uuid}")
async def update_chat(uuid: str, chat: Chat):
    with Session(engine) as session:
        chat_db = session.query(Chat).filter(Chat.uuid == uuid).first()
        if chat_db is None:
            raise HTTPException(status_code=404, detail="Chat not found")
        chat_db.title = chat.title
        chat_db.new_message = chat.new_message
        chat_db.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(chat_db)
        return chat_db


@app.post("/chats/{uuid}/messages")
async def create_message(uuid: str, message: Message):
    chat = await get_chat(uuid)
    with Session(engine) as session:
        message.chat_id = chat.id
        session.add(message)
        session.commit()
        session.refresh(message)
        return message


@app.get("/chats/{uuid}/messages")
async def list_messages(uuid: str, after: str = None):
    chat = await get_chat(uuid)
    with Session(engine) as session:
        query = (
            session.query(Message)
            .filter(Message.chat_id == chat.id)
            .order_by(Message.created_at)
        )
        if after:
            message = (
                session.query(Message)
                .filter(Message.chat_id == chat.id)
                .filter(Message.uuid == after)
                .first()
            )
            return query.filter(Message.created_at > message.created_at).all()
        return query.all()
