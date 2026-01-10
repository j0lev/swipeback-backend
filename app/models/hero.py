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
