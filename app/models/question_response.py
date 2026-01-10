from fastapi import Depends, FastAPI, HTTPException, status, Query, APIRouter
from sqlmodel import SQLModel, Field, select

from app.db import SessionDep
from app.auth import CurrentActiveUserDI
from datetime import datetime, timedelta, timezone
from typing import Union, Annotated

from contextlib import asynccontextmanager

import jwt
from jwt.exceptions import InvalidTokenError

from pydantic import BaseModel

class QuestionResponse(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    question_id: int = Field(foreign_key="question.id", index=True)

    answer: bool

    timestamp: datetime = Field(default_factory=datetime.utcnow)

class QuestionResponseCreate(SQLModel):
    question_id: int
    answer: bool

class QuestionResult(SQLModel):
    question_id: int
    text: str
    yes_count: int
    no_count: int

