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

class Slider(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    module_id: int = Field(foreign_key="module.id", index=True)

    text: str

class SliderCreate(SQLModel):
    text: str

class SliderPublic(SQLModel):
    id: int
    text: str
