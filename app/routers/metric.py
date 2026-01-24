from fastapi import Depends, FastAPI, HTTPException, status, Query, APIRouter
from sqlmodel import SQLModel, Field, select

from app.db import SessionDep
from app.auth import CurrentActiveUserDI
from app.models.metric import Metric, MetricCreate, MetricPublic, MetricUpdate
from datetime import datetime, timedelta, timezone
from typing import Union, Annotated

from contextlib import asynccontextmanager

import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy import delete

from pydantic import BaseModel
from app.models import Session, Module, Hero

from app.routers.metric_value import delete_metric_values

router = APIRouter(tags=["metrics"])

@router.post(
    "/sessions/{session_id}/metrics",
    response_model=MetricPublic,
    status_code=201
)
def create_metric(
    session_id: int,
    metric: MetricCreate,
    session: SessionDep,
    user: CurrentActiveUserDI
):
    db_session = session.get(Session, session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Optional: Ownership prüfen (Session gehört User)
    db_metric = Metric(
        session_id=session_id,
        title=metric.title
    )
    session.add(db_metric)
    session.commit()
    session.refresh(db_metric)
    return db_metric


@router.get("/sessions/{session_id}/metrics", response_model=list[MetricPublic])
def read_metrics(
    session_id: int,
    session: SessionDep,
    user: CurrentActiveUserDI
):
    statement = select(Metric).where(Metric.session_id == session_id)
    return session.exec(statement).all()


@router.patch("/metrics/{metric_id}", response_model=MetricPublic)
def update_metric(
    metric_id: int,
    metric_update: MetricUpdate, #TODO update integration? i don't know
    session: SessionDep,
    user: CurrentActiveUserDI
):
    metric = session.get(Metric, metric_id)
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")

    update_data = metric_update.model_dump(exclude_unset=True)
    metric.sqlmodel_update(update_data)

    session.add(metric)
    session.commit()
    session.refresh(metric)
    return metric


@router.delete("/metrics/{metric_id}", status_code=204)
def delete_metric(
    metric_id: int,
    session: SessionDep,
    user: CurrentActiveUserDI
):
    metric = session.get(Metric, metric_id)
    if not metric:
        raise HTTPException(status_code=404, detail="Metric not found")

    session.delete(metric)
    session.commit()

@router.delete("/metrics/all/{session_id}", status_code=204)
def delete_metric(
    session_id: int,
    session: SessionDep,
    user: CurrentActiveUserDI
):
    delete_metric_values()
    session.exec(
        delete(Metric).where(Metric.session_id == session_id)
    )
    session.commit()
