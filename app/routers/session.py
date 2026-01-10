from datetime import datetime, timedelta, timezone
from typing import Union, Annotated

from contextlib import asynccontextmanager

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, FastAPI, HTTPException, status, Query, APIRouter



from pydantic import BaseModel

from app.db import SessionDep
from app.auth import CurrentActiveUserDI

from sqlmodel import Field, SQLModel, select
from app.models import Module, Hero, Session
from uuid import uuid4


router = APIRouter()

@router.post("/modules/{module_id}/sessions/start")
def start_session(
    module_id: int,
    session: SessionDep,
    user: CurrentActiveUserDI
):
    module = session.get(Module, module_id)
    if not module or module.user_id != user.username:
        raise HTTPException(status_code=403)

    active = session.exec(
        select(Session).where(
            Session.module_id == module_id,
            Session.is_active == True
        )
    ).first()
    if active:
        raise HTTPException(400, "Active session already exists")

    db_session = Session(
        module_id=module_id,
        start_time=datetime.utcnow(),
        join_code=uuid4().hex[:6].upper(), #Generates a random UUID (uses random numbers)
        is_active=True
    )
    session.add(db_session)
    session.commit()
    session.refresh(db_session)
    return db_session

@router.post("/sessions/{session_id}/end")
def end_session(
    session_id: int,
    session: SessionDep,
    user: CurrentActiveUserDI
):
    db_session = session.get(Session, session_id)
    if not db_session:
        raise HTTPException(404)

    db_session.is_active = False
    db_session.end_time = datetime.utcnow()

    session.add(db_session)
    session.commit()
    return {"status": "ended"}
