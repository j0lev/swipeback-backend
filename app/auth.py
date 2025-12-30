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

from app.db import SessionDep


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# TODO change this to an environmental variable of deployment platform
SECRET_KEY = "02b68540063b967e41f15dced7b908d3a4e69fc6a7ac8ff658b4f73e1d55582a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None


class User(SQLModel):
    username: str = Field(primary_key=True, index=True)
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = False

class UserInDB(User, table=True):
    hashed_password: str


class UserCreate(User):
    plain_password: str



password_hash = PasswordHash.recommended()

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)

@router.post("/users", response_model=User)
def create_user(user: UserCreate, session: SessionDep):
    db_user = UserInDB(
        **user.model_dump(),
        hashed_password=get_password_hash(user.plain_password)
    )
    potentially_existing_db_user = session.get(UserInDB, user.username)
    if potentially_existing_db_user:
        raise HTTPException(status_code=409, detail="Username already taken")
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return user

def get_user(username: str, session: SessionDep):
    user_db = session.get(UserInDB, username)
    if not user_db:
        raise HTTPException(status_code=404, detail="Hero not found")
    user = user_db.model_dump(exclude={"hashed_password"})
    return user

def authenticate_user(username: str, password: str, session: SessionDep):
    user_in_db = session.get(UserInDB, username)
    if not user_in_db:
        return False
    if not verify_password(password, user_in_db.hashed_password):
        return False
    return user_in_db

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

OAuth2SchemeDI = Annotated[str, Depends(oauth2_scheme)]

async def get_current_user(token: OAuth2SchemeDI, session: SessionDep):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username == None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username, session=session)
    if user is None:
        raise credentials_exception
    return user

CurrentUserDI = Annotated[User, Depends(get_current_user)]

async def get_current_active_user(current_user: CurrentUserDI):
    current_user = User.model_validate(current_user)
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

CurrentActiveUserDI = Annotated[User, Depends(get_current_active_user)]

OAuth2PasswordRequestFormDI = Annotated[OAuth2PasswordRequestForm, Depends()]

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestFormDI, session: SessionDep):
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer",}
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")