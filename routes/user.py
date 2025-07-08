from fastapi import APIRouter,Header,Request,HTTPException
from ..models.userSchema import SignUpScheme,logInSchema
from ..auth.authHandler import sign_jwt,decode_jwt
from typing import Annotated
import json 

router = APIRouter() 


@router.post("/signUp")
async def signUp(user:SignUpScheme,request:Request):

    userDict = user.model_dump()

    result = await request.app.mongodb["users"].insert_one(userDict)

    # token = sign_jwt(user_id=str(result.inserted_id))

    return {"body":"user Signed up."}


@router.post("/logIn")
async def logIn(response:logInSchema,request:Request,token:Annotated[str|None,Header()]=None):

    inserted_user = await request.app.mongodb["users"].find_one({"email":response.email,"password":response.password})

    if not inserted_user:
        raise HTTPException(status_code=404, detail="User does not exist")

    data = sign_jwt(user_id=str(inserted_user["_id"]))

    return data