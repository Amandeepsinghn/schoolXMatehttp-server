from fastapi import FastAPI
from .routes import userRouter,testRouter
from .database.database import lifespan

app = FastAPI(lifespan=lifespan)

app.include_router(router=userRouter.router, prefix="/api")

app.include_router(router=testRouter.router,prefix="/api/test")



