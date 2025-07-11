from fastapi import APIRouter,Header,Request,HTTPException,Depends,UploadFile
from ..auth.authHandler import dbResponseParser
from ..auth.authBearer import JWTBearer
from fastapi.security import HTTPAuthorizationCredentials
from langchain.text_splitter import RecursiveCharacterTextSplitter
import uuid
from bson.objectid import ObjectId
import os 
from dotenv import load_dotenv 
from pinecone import Pinecone
from werkzeug.utils import secure_filename
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
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
async def uploadPdf(file:UploadFile,token:HTTPAuthorizationCredentials=Depends(JWTBearer())):
    try:
        filename = secure_filename(file.filename)
        upload_dir = "uploadedFile"
        os.makedirs(upload_dir,exist_ok=True)

        unique_uuid = str(uuid.uuid4())

        tempPath = os.path.join(upload_dir,f"{unique_uuid}_{filename}")

        with open(tempPath,"wb") as fileObj:
            fileObj.write(await file.read())
        
        loader = PyPDFLoader(tempPath)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=50)
        finalDocument = splitter.split_documents(docs)
        
        texts = [doc.page_content for doc in finalDocument]

        embedding = embeddings.embed_documents(texts)
            
        vectorToUpload = [] 
        for i in range(len(texts)):
            vectorToUpload.append((unique_uuid,embedding[i],{"user_id":token["user_id"]}))

        index.upsert(vectorToUpload)

        return {
            "body":{
                "sessionId":unique_uuid
            }
        }
    finally:
        os.remove(tempPath)
    








