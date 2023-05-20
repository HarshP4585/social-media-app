import json
from fastapi import APIRouter, Depends, status, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..dto import Login, Token
from ..models import User as UserSQLAlchemy
from ..database import get_db
from ..utils import verify
from ..oauth2 import get_token

router = APIRouter(
    tags=["authentication"]
)

@router.post("/login")
# use OAuth2PasswordRequestForm for Form data
def login(payload: Login, db: Session = Depends(get_db)):
    user = db.query(UserSQLAlchemy).filter(UserSQLAlchemy.email == payload.email).first()
    if not user:
        return Response(
            status_code=status.HTTP_404_NOT_FOUND,
            content=json.dumps({"data": f"user with email: {payload.email} not found"}),
            media_type="application/json"
        )
    elif not verify(payload.password, user.password): # hash(payload.password) != user.password
        return Response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=json.dumps({"data": "password does not match"}),
            media_type="application/json"
        )

    # provide the payload like user_id, role, scopes (but no private info like passwords)
    access_token = get_token({"user_id": user.id})
    # create and return token
    # use pydantic Token model to return response model
    return Response(
        content=json.dumps({"data": {"access_token": access_token, "token_type": "Bearer"}}),
        media_type="application/json"
    )