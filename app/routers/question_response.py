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
from app.models import Session, Metric, Module, Hero, Question
from app.models.question_response import QuestionResponse, QuestionResponseCreate, QuestionResult

router = APIRouter(prefix="/feedback", tags=["Question Responses"])


@router.post("/question/{join_code}")
def submit_question_response(
    join_code: str,
    data: QuestionResponseCreate,
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

    question = session.get(Question, data.question_id)
    if not question or question.session_id != db_session.id:
        raise HTTPException(status_code=404, detail="Question not found")

    response = QuestionResponse(
        question_id=data.question_id,
        answer=data.answer
    )

    session.add(response)
    session.commit()

    return {"status": "ok"}


@router.get(
    "/sessions/{session_id}/questions/results",
    response_model=list[QuestionResult]
)
def get_question_results(
    session_id: int,
    session: SessionDep,
    user: CurrentActiveUserDI
):
    questions = session.exec(
        select(Question).where(Question.session_id == session_id)
    ).all()

    results: list[QuestionResult] = []

    for question in questions:
        responses = session.exec(
            select(QuestionResponse).where(
                QuestionResponse.question_id == question.id
            )
        ).all()

        yes_count = sum(1 for r in responses if r.answer)
        no_count = sum(1 for r in responses if not r.answer)

        results.append(
            QuestionResult(
                question_id=question.id,
                text=question.text,
                yes_count=yes_count,
                no_count=no_count
            )
        )

    return results
