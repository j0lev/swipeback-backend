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

router = APIRouter(tags=["metrics"])

class MetricValue(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    metric_id: int = Field(foreign_key="metric.id")
    value: int = Field(ge=0, le=10)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MetricValueCreate(SQLModel):
    metric_id: int
    value: int

class MetricValuePublic(SQLModel):
    value: int
    timestamp: datetime

class MetricResult(SQLModel):
    metric_id: int
    title: str
    average: float | None
    values: list[MetricValuePublic]

router = APIRouter(prefix="/feedback", tags=["Metric Values"])

@router.post("/metric/{join_code}")
def submit_metric_value(join_code: str, data: MetricValueCreate, session: SessionDep):
    # aktive Session über Join-Code finden
    db_session = session.exec(
        select(Session).where(
            Session.join_code == join_code,
            Session.is_active == True
        )
    ).first()

    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found or inactive")

    # Metric prüfen
    metric = session.get(Metric, data.metric_id)
    if not metric or metric.session_id != db_session.id:
        raise HTTPException(status_code=404, detail="Metric not found")

    # MetricValue speichern
    metric_value = MetricValue(
        metric_id=data.metric_id,
        value=data.value
    )

    session.add(metric_value)
    session.commit()

    return {"status": "ok"}

@router.get(
    "/sessions/{session_id}/metrics/results",
    response_model=list[MetricResult]
)
def get_metric_results(
    session_id: int,
    session: SessionDep,
    user: CurrentActiveUserDI
):
    # Session prüfen
    db_session = session.get(Session, session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Alle Metrics der Session
    metrics = session.exec(
        select(Metric).where(Metric.session_id == session_id)
    ).all()

    results: list[MetricResult] = []

    for metric in metrics:
        values = session.exec(
            select(MetricValue).where(MetricValue.metric_id == metric.id)
        ).all()

        public_values = [
            MetricValuePublic(
                value=v.value,
                timestamp=v.timestamp
            )
            for v in values
        ]

        average = (
            sum(v.value for v in values) / len(values)
            if values else None
        )

        results.append(
            MetricResult(
                metric_id=metric.id,
                title=metric.title,
                average=average,
                values=public_values
            )
        )
    return results

