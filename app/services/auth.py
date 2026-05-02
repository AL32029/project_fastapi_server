import datetime
import hashlib
from typing import Optional, Annotated, Dict

import bcrypt
from asyncpg import UniqueViolationError
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import select
from starlette import status

from core.config import app_settings
from db.db import db_dependency
from models import Users
from schemas.users import UserRegisterSchema, UserLoginSchema

JWT_SECRET = app_settings.jwt_secret
ALGORITHM = app_settings.encrypt_algorithm
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/auth/token')

def hash_password(password: str) -> str:
    password_bytes = hashlib.sha256(password.encode()).digest()
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=14)).decode()

def verify_password(password: str, hashed_password: str) -> bool:
    try:
        password_bytes = hashlib.sha256(password.encode()).digest()
        return bcrypt.checkpw(password_bytes, hashed_password.encode())
    except (ValueError, TypeError):
        return False


def create_access_token(data: dict, expires_delta: datetime.timedelta = datetime.timedelta(minutes=15)) -> str:
    to_encode = data.copy()
    expire = int((datetime.datetime.now(datetime.UTC) + expires_delta).timestamp())
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)


async def reg_user(user_data: UserRegisterSchema, db: db_dependency):
    try:
        create_user_statement = Users(
            **user_data.model_dump(exclude={'password'}),
            hashed_password=hash_password(user_data.password)
        )
        db.add(create_user_statement)
        await db.commit()
        return {"response": "User created successfully"}
    except UniqueViolationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User with such credentials already exists'
        )
    except Exception as ex:
        raise ex


async def auth_user(login_data: UserLoginSchema, db: db_dependency):
    user: Optional[Users] = await db.scalar(select(Users).where(Users.email == login_data.email))

    if not user:
        return False

    if not verify_password(login_data.password, user.hashed_password):
        return False

    return user

async def get_current_user(token: str = Depends(oauth2_bearer)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        print(payload)
        user_data = {"sub": payload.get("sub")}
        if user_data is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user_data

user_dependency = Annotated[Dict, Depends(get_current_user)]
