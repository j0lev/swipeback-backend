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



class ModuleBase(SQLModel):
    title: str
    description: str | None = None

class Module(ModuleBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="userindb.username")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ModuleCreate(ModuleBase):
    pass

class ModulePublic(ModuleBase):
    id: int
    created_at: datetime

router = APIRouter(prefix="/modules", tags=["modules"])

@router.post("/", response_model=ModulePublic)
def create_module(
    module: ModuleCreate,
    session: SessionDep,
    user: CurrentActiveUserDI
):
    db_module = Module(
        **module.model_dump(),
        user_id=user.username
    )
    session.add(db_module)
    session.commit()
    session.refresh(db_module)
    return db_module


@router.get("/", response_model=list[ModulePublic]) 
def read_modules( # to show all modules of this professor
    session: SessionDep,
    user: CurrentActiveUserDI
):
    statement = select(Module).where(Module.user_id == user.username)
    return session.exec(statement).all()

@router.get("/{module_id}", response_model=ModulePublic)
def read_module( # to show the exact module
    module_id: int,
    session: SessionDep,
    user: CurrentActiveUserDI
):
    module = session.get(Module, module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    if module.user_id != user.username:
        raise HTTPException(status_code=403, detail="Not allowed")
    return module

@router.patch("/{module_id}", response_model=ModulePublic)
def update_module(
    module_id: int,
    module_update: ModuleUpdate,
    session: SessionDep,
    user: CurrentActiveUserDI
):
    module = session.get(Module, module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    if module.user_id != user.username:
        raise HTTPException(status_code=403, detail="Not allowed")

    update_data = module_update.model_dump(exclude_unset=True)
    module.sqlmodel_update(update_data)

    session.add(module)
    session.commit()
    session.refresh(module)
    return module


@router.delete("/{module_id}", status_code=204)
def delete_module(
    module_id: int,
    session: SessionDep,
    user: CurrentActiveUserDI
):
    module = session.get(Module, module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    if module.user_id != user.username:
        raise HTTPException(status_code=403, detail="Not allowed")

    session.delete(module)
    session.commit()
