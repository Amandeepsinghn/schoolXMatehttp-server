from fastapi import FastAPI
from .routes import user
from .database.database import lifespan

app = FastAPI(lifespan=lifespan)

app.include_router(router=user.router, prefix="/api")






    
