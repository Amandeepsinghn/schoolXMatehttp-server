import time 
from typing import Dict
import os 
import jwt
from dotenv import load_dotenv 
load_dotenv()

JWT_SECRET= os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

def token_response(token:str) -> dict:
    return {"token":token}


def sign_jwt(user_id:str) -> Dict[str,str]:
    payload = {
        "user_id":user_id,
        "expires":time.time() + 1200
    }

    token = jwt.encode(payload,JWT_SECRET,algorithm=JWT_ALGORITHM)

    return token_response(token)


def decode_jwt(token:str) -> dict:
    try:
        decoded_token = jwt.decode(token,JWT_SECRET,algorithms=JWT_ALGORITHM)
        return decoded_token if decoded_token["expires"] >=time.time() else None 
    
    except:
        return {}
    

def dbResponseParser(request):
    request["_id"] = str(request["_id"])
    return request