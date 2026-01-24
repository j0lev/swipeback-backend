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



class ModuleBase(SQLModel):
    title: str
    description: str | None = None

class Module(ModuleBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="userindb.username") # TODO to connect with hero
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ModuleCreate(ModuleBase):
    pass

class ModulePublic(ModuleBase):
    id: int
    created_at: datetime

class ModuleUpdate(SQLModel):
    title: str | None = None
