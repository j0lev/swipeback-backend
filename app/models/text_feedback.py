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
from app.models import Session, Metric, Module, Hero


class TextFeedback(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    session_id: int = Field(foreign_key="session.id", index=True)

    content: str

    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TextFeedbackCreate(SQLModel):
    content: str

class TextFeedbackPublic(SQLModel):
    content: str
    timestamp: datetime

router = APIRouter(prefix="/feedback", tags=["Text Feedback"])

@router.post("/text/{join_code}")
def submit_text_feedback(
    join_code: str,
    data: TextFeedbackCreate,
    session: SessionDep
):
    db_session = session.exec(
        select(Session).where(
            Session.join_code == join_code,
            Session.is_active == True
        )
    ).first()

    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found or inactive")

    feedback = TextFeedback(
        session_id=db_session.id,
        content=data.content
    )

    session.add(feedback)
    session.commit()

    return {"status": "received"}

@router.get(
    "/sessions/{session_id}/text-feedback",
    response_model=List[TextFeedbackPublic]
)
def get_text_feedback(
    session_id: int,
    session: SessionDep,
    user: CurrentActiveUserDI
):
    feedback = session.exec(
        select(TextFeedback).where(TextFeedback.session_id == session_id)
    ).all()

    return feedback
