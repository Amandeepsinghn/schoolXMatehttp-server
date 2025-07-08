from pydantic import BaseModel, Field, EmailStr


class SignUpScheme(BaseModel):
    name:str = Field(...)
    password:str = Field(...)
    email:EmailStr = Field(...)
    
class logInSchema(BaseModel):
    email:EmailStr = Field(...)
    password:str = Field(...)