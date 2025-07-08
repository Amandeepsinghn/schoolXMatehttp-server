from fastapi import APIRouter,Header,Request
from ..models.userSchema import SignUpScheme,logInSchema
from ..auth.authHandler import sign_jwt,decode_jwt
from typing import Annotated
from ..database.userMongose import User

router = APIRouter() 


@router.post("/signUp",response_model=User)
async def signUp(response:SignUpScheme,request:Request):

    userDict = response.model_dump()

    result = await request.app.mongodb["users"].insert_one(userDict)

    inserted_user = await request.app.mongodb["users"].find_one({"_id": result.inserted_id})

    return inserted_user


@router.post("/logIn")
async def logIn(response:logInSchema,token:Annotated[str|None,Header()]=None):

    response = decode_jwt(token=token)

    if response!=None:
        return {
            "message":response
        }
    
    else:
        return {
            "message":"not working"
        }


