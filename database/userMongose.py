from typing import Optional, List # Supports for type hints
from pydantic import BaseModel,EmailStr # Most widely used data validation library for python
from enum import Enum # Supports for enumerations


class User(BaseModel):
    name: str
    password: str
    email: EmailStr

