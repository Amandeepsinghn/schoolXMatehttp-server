from pydantic import BaseModel, Field
from typing import Optional

class testIntialize(BaseModel):
    start:bool= Field(None)

class testRespond(BaseModel):
    topic:Optional[str] = Field(None,min_length=2,max_length=50)
    subTopic:Optional[str]= Field(None,min_length=2,max_length=50)
    difficultLevel:Optional[str] = Field(None,min_length=2,max_length=50)
    sessionId:str =Field(...)

    class Config:
        extra = "forbid"  # optional, prevents extra fields

class GenerateTest(BaseModel):
    topic:str = Field(...)
    subTopic:str = Field(...)
    difficultLevel:str = Field(...)


class qaSchema(BaseModel):
    question:str = Field(...)

class pdfSchema(BaseModel):
    id:str = Field(...)