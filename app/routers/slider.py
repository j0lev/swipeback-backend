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
from app.models import Metric, Module, Hero
from app.models.slider import SliderCreate, SliderPublic, Slider

from app.models.session import Session, SessionDep

router = APIRouter(prefix="/modules", tags=["Sliders"])

@router.post("/{module_id}/sliders", response_model=SliderPublic)
def create_slider(
    module_id: int,
    data: SliderCreate,
    session: SessionDep,
    user: CurrentActiveUserDI
):
    db_session = session.get(Module, module_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Module not found")

    slider = Slider(
        module_id=module_id,
        text=data.text
    )

    session.add(slider)
    session.commit()
    session.refresh(slider)

    return slider

@router.get("/sliders/by_module_id/{module_id}", response_model=list[SliderPublic])
def get_sliders(
    module_id: int,
    session: SessionDep
):
    sliders = session.exec(
        select(Slider).where(Slider.module_id == module_id)
    ).all()

    return sliders

@router.get("/sliders/by_join_code/{join_code}", response_model=list[SliderPublic])
def get_sliders(
    join_code: str,
    session: SessionDep
):
    db_session: Session = session.exec(select(Session).where(Session.join_code == join_code)).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    module_id = db_session.module_id

    db_module = session.exec(select(Module).where(Module.id == module_id)).first()
    if not db_module:
        raise HTTPException(status_code=404, detail="Module not found")
    module_id = db_module.id

    sliders = session.exec(
        select(Slider).where(Slider.module_id == module_id)
    ).all()
    sliders_public = []
    for slider in sliders:
        slider_public = SliderPublic(id=slider.id, text=slider.text)
        sliders_public.append(slider_public)
    return sliders_public

