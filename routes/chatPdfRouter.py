from fastapi import APIRouter,Header,Request,HTTPException,Depends,UploadFile
from auth.authHandler import dbResponseParser
from auth.authBearer import JWTBearer
from models.testSchema import qaSchema,pdfSchema
from fastapi.security import HTTPAuthorizationCredentials
from langchain.text_splitter import RecursiveCharacterTextSplitter
import uuid
from bson.objectid import ObjectId
import os 
from langchain.chains.combine_documents import create_stuff_documents_chain
from dotenv import load_dotenv 
from pinecone import Pinecone
from werkzeug.utils import secure_filename
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableMap
from langchain_core.documents import Document
load_dotenv()

embeddings=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
llm=ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"),model_name="Llama3-8b-8192")

prompt=ChatPromptTemplate.from_template(
    """
    Answer the questions based on the provided context only.
    Please provide the most accurate respone based on the question
    <context>
    {context}
    <context>
    Question:{input}

    """

)


pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("school")

router = APIRouter() 

@router.post("/uploadFile")
async def uploadPdf(file:UploadFile,request:Request,token:HTTPAuthorizationCredentials=Depends(JWTBearer())):
    try:
        filename = secure_filename(file.filename)
        upload_dir = "uploadedFile"
        os.makedirs(upload_dir,exist_ok=True)

        unique_uuid = str(uuid.uuid4())

        tempPath = os.path.join(upload_dir,f"{unique_uuid}_{filename}")

        with open(tempPath,"wb") as fileObj:
            fileObj.write(await file.read())
        
        result = await request.app.mongodb["chatPdf"].insert_one({"user_id":ObjectId(token["user_id"]),"name":filename,"chatHistory":[]})

        unique_id = str(result.inserted_id)

        loader = PyPDFLoader(tempPath)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=50)
        finalDocument = splitter.split_documents(docs)
        
        texts = [doc.page_content for doc in finalDocument]

        embedding = embeddings.embed_documents(texts)
            
        vectorToUpload = [] 
        for i in range(len(texts)):
            vectorToUpload.append((str(uuid.uuid4()),embedding[i],{"user_id":token["user_id"],"unique_id":unique_id,"text":texts[i]}))

        index.upsert(vectorToUpload)

        return {"body":{"sessionId":unique_id}}
    finally:
        os.remove(tempPath)
    
@router.post("/qaChat/{sessionId}")
async def qaChat(question:qaSchema,sessionId:str,request:Request,token:HTTPAuthorizationCredentials=Depends(JWTBearer())):
    question = question.model_dump()
    unique_id = sessionId

    queryEmbeddding = embeddings.embed_query(question["question"])

    
    response = index.query(        
        vector = queryEmbeddding,
        top_k=5,
        filter={"user_id":str(token["user_id"]),"unique_id":unique_id},
        include_metadata=True
    )

    docs = [Document(page_content=match["metadata"]["text"],metadata=match["metadata"]) for match in response['matches']]


    documentChain = create_stuff_documents_chain(llm=llm,prompt=prompt)

    retreival_chain = RunnableMap({"context":lambda _:docs,"input":lambda x:x["input"]}) | documentChain

    answer =retreival_chain.invoke({"input":question["question"]})

    response = await request.app.mongodb["chatPdf"].update_one({"user_id": ObjectId(token["user_id"]),"_id":ObjectId(sessionId)},
    {"$push": {"chatHistory":{"question":question["question"],"answer":answer}}})

    return {"body":answer}

@router.get("/getAllpdf")
async def getAllpdf(request:Request,token:HTTPAuthorizationCredentials=Depends(JWTBearer())):

    response = request.app.mongodb["chatPdf"].find({"user_id":ObjectId(token["user_id"])},{"name":1,"_id":1,"chatHistory":1})

    dataToShow = []
    async for doc in response:
        doc["_id"] = str(doc["_id"])
        dataToShow.append(doc)

    return {"body":dataToShow}


@router.post("/getSinglePdf")
async def singlePdf(data:pdfSchema,request:Request,token:HTTPAuthorizationCredentials=Depends(JWTBearer())):

    data = data.model_dump()

    id = data["id"]

    response = dbResponseParser(await request.app.mongodb["chatPdf"].find_one({"_id":ObjectId(id)},{"_id":0,"chatHistory":1}))

    return {"body":response["chatHistory"]}










