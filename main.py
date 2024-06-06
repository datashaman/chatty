import os

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from dotenv import load_dotenv

from fastapi import FastAPI, File, Body, Request, HTTPException, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from openai import OpenAI

from pydantic import model_validator

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Session, SQLModel, create_engine


load_dotenv()


class Chat(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: UUID = Field(
        sa_column_kwargs={"unique": True},
        nullable=False,
        index=True,
        default_factory=uuid4,
    )
    title: str = Field(nullable=False, index=True)
    new_message: Optional[str] = None

    created_at: datetime = Field(sa_column=Column(DateTime, server_default=func.now()))
    updated_at: datetime = Field(sa_column=Column(DateTime, onupdate=func.now()))


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: UUID = Field(
        sa_column_kwargs={"unique": True},
        nullable=False,
        index=True,
        default_factory=uuid4,
    )
    role: str = 'user'
    content: str

    created_at: datetime = Field(sa_column=Column(DateTime, server_default=func.now()))

    chat_id: int = Field(foreign_key="chat.id", index=True)

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


openai = OpenAI()

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
async def on_startup() -> None:
    SQLModel.metadata.create_all(engine)


@app.get("/chats")
async def list_chats() -> List[Chat]:
    with Session(engine) as session:
        return session.query(Chat).order_by(Chat.created_at.desc()).all()


@app.get("/chats/{uuid}")
async def get_chat(uuid: str) -> Chat:
    with Session(engine) as session:
        chat = session.query(Chat).filter(Chat.uuid == uuid).first()
        if chat is None:
            raise HTTPException(status_code=404, detail="Chat not found")
        return chat


@app.post("/chats")
async def create_chat(chat: Chat) -> Chat:
    with Session(engine) as session:
        session.add(chat)
        session.commit()
        session.refresh(chat)
        return chat


@app.patch("/chats/{uuid}")
async def update_chat(uuid: str, chat: Chat) -> Chat:
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
async def send_message(uuid: str, message: Message = Body(...), files: List[UploadFile] = File(...)) -> Message:
    print(files)
    chat = await get_chat(uuid)
    with Session(engine) as session:
        message.chat_id = chat.id
        session.add(message)
        session.commit()
        session.refresh(message)

        messages = (
            session.query(Message)
            .with_entities(Message.role, Message.content)
            .filter(Message.chat_id == chat.id)
            .order_by(Message.created_at)
            .all()
        )

        response_message = complete_chat([message._asdict() for message in messages])
        response_message.chat_id = chat.id

        session.add(response_message)
        session.commit()
        session.refresh(response_message)
        return response_message


def complete_chat(messages: List[dict]) -> Message:
    completion = openai.chat.completions.create(
        messages=messages,
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=os.getenv("OPENAI_TEMPERATURE", 0.2),
    )

    return Message(
        content=completion.choices[0].message.content,
        role="assistant",
    )


@app.get("/chats/{uuid}/messages")
async def list_messages(uuid: str, after: str = None) -> List[Message]:
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
