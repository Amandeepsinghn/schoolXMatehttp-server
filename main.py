from fastapi import FastAPI
from routes import userRouter,testRouter,chatPdfRouter
from database.database import lifespan
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=userRouter.router, prefix="/api")

app.include_router(router=testRouter.router,prefix="/api/test")

app.include_router(router=chatPdfRouter.router,prefix="/api/chatPdf")

