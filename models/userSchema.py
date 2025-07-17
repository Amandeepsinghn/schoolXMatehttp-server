from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class SignUpScheme(BaseModel):
    name:str = Field(...,min_length=1,max_length=40)
    password:str = Field(...,min_length=1,max_length=40)
    email:EmailStr = Field(...)
    
class logInSchema(BaseModel):
    email:EmailStr = Field(...)
    password:str = Field(...,min_length=1,max_length=40)

class UpdateSchema(BaseModel):
    email:Optional[EmailStr] = Field(None)
    password:Optional[str] = Field(None,min_length=1)
    name:Optional[str] = Field(None,min_length=1)
    