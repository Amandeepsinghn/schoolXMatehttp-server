from fastapi import FastAPI
from .routes import userRouter,testRouter,chatPdfRouter
from .database.database import lifespan

app = FastAPI(lifespan=lifespan)

app.include_router(router=userRouter.router, prefix="/api")

app.include_router(router=testRouter.router,prefix="/api/test")

app.include_router(router=chatPdfRouter.router,prefix="/api/chatPdf")

