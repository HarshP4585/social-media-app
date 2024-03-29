from fastapi import Depends, status
from fastapi.security.oauth2 import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import time
from .dto import TokenData
from .database import get_db
from .models import User as UserSQLAlchemy, RevokedToken
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRATION_TIME = settings.access_token_expire_min

def get_token(payload: dict):
    payload_copy = payload.copy()
    expire = time.time() + ACCESS_TOKEN_EXPIRATION_TIME * 60
    # use "exp" to use library's expiry time validation
    payload_copy["expire"] = expire
    
    return jwt.encode(payload_copy, SECRET_KEY, ALGORITHM)

def verify_access_token(token: str):
    # how expire will work?
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        
        # verify the expiry of the token
        if payload.get("expire", -1) < time.time():
            raise JWTError("token expired")
        
    except JWTError:
        # return -1
        return TokenData(id = -1)

    user_id = payload.get("user_id")
    
    if not user_id:
        # return -1
        return TokenData(id = -1)
    
    # return user_id
    return TokenData(id = user_id)

# embeded as dependency in controllers to verify token and get user id
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # if token is revoked, return None which will raise error and not let user to access the resources
    db_token = db.query(RevokedToken).filter(RevokedToken.token == token).first()
    if db_token:
        return None
    
    token = verify_access_token(token)
    
    # fetch and return user from the database using user id
    user = db.query(UserSQLAlchemy).filter(UserSQLAlchemy.id == token.id).first()
    return user
