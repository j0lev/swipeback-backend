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
from uuid import uuid4


class Session(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    module_id: int = Field(foreign_key="module.id")
    start_time: datetime
    end_time: datetime | None = None
    join_code: str = Field(index=True, unique=True)
    is_active: bool = True
