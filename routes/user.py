from fastapi import APIRouter,Header,Request,HTTPException,Depends
from ..models.userSchema import SignUpScheme,logInSchema
from ..auth.authHandler import sign_jwt,decode_jwt,dbResponseParser
from ..auth.authBearer import JWTBearer
from fastapi.security import HTTPAuthorizationCredentials
from typing import Annotated
import json 
from bson.objectid import ObjectId

router = APIRouter() 


@router.post("/signUp")
async def signUp(user:SignUpScheme,request:Request):

    userDict = user.model_dump()
    
    result = await request.app.mongodb["users"].insert_one(userDict)

    return {"body":"user Signed up."}


@router.post("/logIn")
async def logIn(loginData:logInSchema,request:Request,token:Annotated[str|None,Header()]=None):

    inserted_user = await request.app.mongodb["users"].find_one({"email":loginData.email,"password":loginData.password})

    if not inserted_user:
        raise HTTPException(status_code=404, detail="User does not exist")

    data = sign_jwt(user_id=str(inserted_user["_id"]))

    return data

@router.get("/getProfile")
async def getProfile(request:Request,token:HTTPAuthorizationCredentials=Depends(JWTBearer())):

    userId = token["user_id"]

    response = dbResponseParser(await request.app.mongodb["users"].find_one({"_id":ObjectId(userId)}))

    return {"body": response} 

