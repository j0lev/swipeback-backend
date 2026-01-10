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

