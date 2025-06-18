from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from starlette.responses import JSONResponse
from starlette.status import HTTP_201_CREATED

from Auth.authentication import AuthHandler
from Models.user_models import User, UserInput, UserLogin
from Utility.users import select_all_users, find_user
from db.db import get_session

user_router = APIRouter()
auth_handler = AuthHandler()

@user_router.post('/registration', status_code=201, tags=['users'],
                  description='Register new user')
def register(user: UserInput, session: Session = Depends(get_session)):
    users = select_all_users()

    if any(x.username == user.username for x in users):
        raise HTTPException(status_code=400, detail='Username is taken')

    hashed_pwd = auth_handler.get_password_hash(user.password)
    u = User(username=user.username, password=hashed_pwd, email=user.email, is_seller=user.is_seller)

    session.add(u)
    session.commit()

    return JSONResponse(
        content={"message": "User successfully registered"},
        status_code=HTTP_201_CREATED
    )

@user_router.post('/login', tags=['users'])
def login(user: UserLogin):
    user_found = find_user(user.username)
    if not user_found:
        raise HTTPException(status_code=401, detail='Invalid username and/or password')

    verified = auth_handler.verify_password(user.password, user_found.password)
    if not verified:
        raise HTTPException(status_code=401, detail='Invalid username and/or password')

    token = auth_handler.encode_token(user_found.username)
    return {'token': token}