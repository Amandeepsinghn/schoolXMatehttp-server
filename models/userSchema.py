from pydantic import BaseModel, Field, EmailStr


class SignUpScheme(BaseModel):
    name:str = Field(...,min_length=1,max_length=40)
    password:str = Field(...,min_length=1,max_length=40)
    email:EmailStr = Field(...)
    
class logInSchema(BaseModel):
    email:EmailStr = Field(...)
    password:str = Field(...,min_length=1,max_length=40)