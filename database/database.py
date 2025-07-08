from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os 
from fastapi import FastAPI

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):

    await startup_db_client(app)
    yield

    await shutdown_db_client(app)


async def startup_db_client(app):
    app.mongodb_client = AsyncIOMotorClient(
        os.getenv("MONGO_DB_CONNECTION_STRING"))
    app.mongodb = app.mongodb_client.get_database("college")



async def shutdown_db_client(app):
    app.mongodb_client.close()
