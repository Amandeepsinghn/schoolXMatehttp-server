from fastapi import FastAPI

from pydantic import BaseModel
from .auth.authHandler import sign_jwt

app = FastAPI()

class SignUp(BaseModel):
    user_id:str


@app.post("/signUp")
async def signUp(response:SignUp):

    print(response)
    response = sign_jwt(user_id=response.user_id)
    return response

    
