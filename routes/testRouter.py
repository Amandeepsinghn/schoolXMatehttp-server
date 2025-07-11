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
from bson.objectid import ObjectId

router = APIRouter() 

"""store the sessionData in reddis for making scalable application"""
sessionData = {}

@router.post("/intialize")
async def intialize(request:testIntialize,token:HTTPAuthorizationCredentials=Depends(JWTBearer())):
    startDict = request.model_dump()

    if startDict["start"] ==True:
        sessionID = str(uuid.uuid4())
        sessionData[sessionID] = {"topic":None,"subTopic":None,"difficultLevel":None} 

    return {
        "body":{"sessionId":sessionID}
    }


@router.post("/respond")
async def respond(request:testRespond,token:HTTPAuthorizationCredentials=Depends(JWTBearer())):

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
async def generateTest(user:GenerateTest,request:Request,token:HTTPAuthorizationCredentials=Depends(JWTBearer())):
    data= user.model_dump()

    testList = ast.literal_eval(testGeneration(data))
    data["test"] = testList
    data["user_id"] = ObjectId(token["user_id"])

    del(data["topic"])
    del(data["subTopic"])
    del(data["difficultLevel"])

    await request.app.mongodb["tests"].insert_one(data)

    return {"body":"test has been sucessfully created"}



@router.get("/getAllTest")
async def getTest(request:Request,token:HTTPAuthorizationCredentials=Depends(JWTBearer())):

    data = request.app.mongodb["tests"].find({"user_id":ObjectId(token["user_id"])},{"topic":1,"subTopic":1})

    dataToShow = []

    async for doc in data:
        doc["_id"] = str(doc["_id"])
        dataToShow.append(doc)

    return {"body":dataToShow}

@router.get("/getTest/{test_id}")
async def getSingleTest(test_id:str,request:Request,token:HTTPAuthorizationCredentials=Depends(JWTBearer())):
    
    data = dbResponseParser(await request.app.mongodb["tests"].find_one({"_id":ObjectId(test_id)},{"test":1,"_id":0}))

    return {"body":data}



