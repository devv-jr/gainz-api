from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from app.auth import create_access_token

router = APIRouter()

class TokenRequest(BaseModel):
    username: str
    password: str

@router.post('/token')
def get_token(req: TokenRequest):
    # Simple dev auth: verify against env variables
    ADMIN_USER = os.getenv('ADMIN_USER', 'admin')
    ADMIN_PASS = os.getenv('ADMIN_PASS', 'password')
    if req.username != ADMIN_USER or req.password != ADMIN_PASS:
        raise HTTPException(status_code=401, detail='Invalid credentials')
    token = create_access_token({'sub': req.username})
    return {'access_token': token, 'token_type': 'bearer'}
