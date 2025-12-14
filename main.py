from typing import Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic_settings import BaseSettings, SettingsConfigDict

import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

db_uri = os.environ.get("MONGODB_URI")

client = MongoClient(db_uri, server_api=ServerApi('1'))

db_success = ""

try:
    client.admin.command('ping')
    db_success = "Pinged your deployment. You successfully connected to MongoDB!"
except Exception as e:
    db_success = e

origins = [
    "https://swipeback.pages.dev",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World", "db_success": db_success}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

