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

# what you need to do:
# - define models
#     - define them how you expect the model to be created from the user, how it is updated by the user, how it is returned to the user and how it is saved in db
#     - models must inherit SQLModel
#     - models must have a primary_key attribute when stored in db
# - create a router, import this router in main.py and add the router in app.include_routers
# - define API methods
#   - use SessionDep dependency injection to access the database
#   - use CurrentActiveUserDI dependency injection to only allow the request when the user is authenticated
#   - response_model is the data type that is returned to the user (e.g. for a user, you don't want to return the hashed password)

class HeroBase(SQLModel):
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)


class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    secret_name: str

class HeroPublic(HeroBase): # what is returned to the client
    id: int

# validates data from clients, also how I would handle passwords?
class HeroCreate(HeroBase): # what is to be inserted into the db (it adds a secret name)
    secret_name: str

# because types change, we need to re-declare all the fields
class HeroUpdate(HeroBase):
    name: str | None = None
    age: int | None = None
    secret_name: str | None = None

router = APIRouter()


@router.post("/heroes/", response_model=HeroPublic)
def create_hero(hero: HeroCreate, session: SessionDep, user: CurrentActiveUserDI):
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


# here again we use HeroPublic so data then is validated and serialized
@router.get("/heroes", response_model=list[HeroPublic])
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100
):
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes

@router.get("/heroes/{hero_id}", response_model=HeroPublic)
def read_hero(hero_id: int, session: SessionDep) -> Hero:
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero

@router.patch("/heroes/{hero_id}", response_model=HeroPublic)
def update_hero(hero_id: int, hero: HeroUpdate, session: SessionDep):
    hero_db = session.get(Hero, hero_id)
    if not hero_id:
        raise HTTPException(status_code=404, detail="Hero not found")
    hero_data = hero.model_dump(exclude_unset=True) # exclude_unset => remove default values
    hero_db.sqlmodel_update(hero_data) # update hero_db with data from hero_data
    session.add(hero_db)
    session.commit()
    session.refresh(hero_db)
    return hero_db

@router.delete("/heroes/{hero_id}")
def delete_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return {"ok": True}