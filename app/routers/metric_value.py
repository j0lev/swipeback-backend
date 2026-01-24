from fastapi import Depends, FastAPI, HTTPException, status, Query, APIRouter
from sqlmodel import SQLModel, Field, select

from app.db import SessionDep
from app.auth import CurrentActiveUserDI
from app.models.metric_value import MetricValue, MetricValueCreate, MetricValuePublic, MetricResult
from datetime import datetime, timedelta, timezone
from typing import Union, Annotated

from contextlib import asynccontextmanager

import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy import delete
from pydantic import BaseModel
from app.models import Session, Metric, Module, Hero


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

@router.delete("/all/{metric_id}", status_code=204)
def delete_metric_values(
    metric_id: int,
    session: SessionDep,
    user: CurrentActiveUserDI
):
    session.exec(
        delete(MetricValue).where(MetricValue.metric_id == metric_id)
    )
    session.commit()