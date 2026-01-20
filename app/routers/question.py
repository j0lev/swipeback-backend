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
from app.models.question import Question, QuestionCreate, QuestionPublic

router = APIRouter(prefix="/sessions", tags=["Questions"])

@router.post("/{session_id}/questions", response_model=QuestionPublic)
def create_question(
    session_id: int,
    data: QuestionCreate,
    session: SessionDep,
    user: CurrentActiveUserDI
):
    db_session = session.get(Session, session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    question = Question(
        session_id=session_id,
        text=data.text
    )

    session.add(question)
    session.commit()
    session.refresh(question)

    return question

@router.get("/questions/by_session_id/{session_id}", response_model=list[QuestionPublic])
def get_questions(
    session_id: int,
    session: SessionDep
):
    questions = session.exec(
        select(Question).where(Question.session_id == session_id)
    ).all()

    return questions

@router.get("/questions/by_join_code/{join_code}", response_model=list[QuestionPublic])
def get_questions(
    join_code: str,
    session: SessionDep
):
    db_session = session.exec(select(Session).where(Session.join_code == join_code)).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    session_id = db_session.id
    questions = session.exec(
        select(Question).where(Question.session_id == session_id)
    ).all()

    return questions

