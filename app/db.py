from datetime import datetime, timedelta, timezone
from typing import Union, Annotated

from contextlib import asynccontextmanager

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, FastAPI, HTTPException, status, Query, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from pwdlib import PasswordHash

from pydantic_settings import BaseSettings, SettingsConfigDict

import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from pydantic import BaseModel

from sqlmodel import Field, Session, SQLModel, create_engine, select



POSTGRESQL_URL = "postgresql://jonathan@localhost:5432/mydb"

engine = create_engine(POSTGRESQL_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]