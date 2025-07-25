from fastapi import APIRouter,Header,Request,HTTPException,Depends
from models.userSchema import SignUpScheme,logInSchema,UpdateSchema
from auth.authHandler import sign_jwt,decode_jwt,dbResponseParser
from auth.authBearer import JWTBearer
from fastapi.security import HTTPAuthorizationCredentials
from typing import Annotated
import json 
from bson.objectid import ObjectId

router = APIRouter() 


@router.post("/signUp")
async def signUp(user:SignUpScheme,request:Request):

    userDict = user.model_dump()

    user = await request.app.mongodb["users"].find_one({"email":user.email})
    if user:
        raise HTTPException(status_code=404,detail="email already taken.")
    
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

@router.post("/updateProfile")
async def updateProfile(user:UpdateSchema,request:Request,token:HTTPAuthorizationCredentials=Depends(JWTBearer())):

    userData = user.model_dump() 

    user = await request.app.mongodb["users"].find_one({"_id":ObjectId(token["user_id"])})

    if not user:
        raise(HTTPException(status_code=411,detail="user does not exsist"))

    filter = {"_id":ObjectId(token["user_id"])}

    try:
        if userData["email"]!=None:
            query = {'$set':{'email':userData["email"]}}
            emailResponse = await request.app.mongodb["users"].update_one(filter,query)

        if userData["password"]!=None:
            query = {'$set':{'password':userData["password"]}}
            passwordResponse = await request.app.mongodb["users"].update_one(filter,query)

        if userData["name"]!=None:
            query = {'$set':{'name':userData["name"]}}
            nameResponse = await request.app.mongodb["users"].update_one(filter,query)

    except Exception as e:
        raise HTTPException(status_code = 404,detail = str(e))

    return {
        "body":"profile has been updated"
    }