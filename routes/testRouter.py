from fastapi import APIRouter,Header,Request,HTTPException,Depends
from ..auth.authHandler import dbResponseParser
from ..auth.authBearer import JWTBearer
from fastapi.security import HTTPAuthorizationCredentials
from typing import Annotated
import uuid
from ..models.testSchema import testIntialize,testRespond,GenerateTest
from ..utils import llmChain,testGeneration
import json 
import ast

router = APIRouter() 

"""store the sessionData in reddis for making scalable application"""
sessionData = {}

@router.post("/intialize")
async def intialize(request:testIntialize):
    startDict = request.model_dump()

    if startDict["start"] ==True:
        sessionID = str(uuid.uuid4())
        sessionData[sessionID] = {"topic":None,"subTopic":None,"difficultLevel":None} 

    return {
        "body":{"sessionId":sessionID}
    }


@router.post("/respond")
async def respond(request:testRespond):

    request = request.model_dump(exclude_unset=True) 

    if request["sessionId"] not in sessionData:
        raise HTTPException(status_code=404,detail="Session id does not exsist")

    keyData = [key for key,data in request.items()][0]

    sessionData[request["sessionId"]][keyData] = request[keyData]
    
    response = json.loads(llmChain(sessionData[request["sessionId"]]))
        
    if response["isComplete"] == True:
        del(sessionData[request["sessionId"]])
        return {"body":response}

    response["sessionId"] = request["sessionId"]

    return {"body":response}


@router.post("/generateTest")
async def generateTest(user:GenerateTest):
    data= user.model_dump()

    data = testGeneration(data)

    return {
        "body":data
    }




