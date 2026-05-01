from datetime import timedelta, datetime
from typing import Optional, Annotated, Dict

import bcrypt
from asyncpg import UniqueViolationError
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import select
from starlette import status

from core.config import app_settings
from db.db import db_dependency
from models import Users
from schemas.users import UserRegisterSchema, UserLoginSchema

JWT_SECRET = app_settings.jwt_secret
ALGORITHM = app_settings.encrypt_algoritm
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/auth/token')


def generate_salt() -> str:
    return bcrypt.gensalt().decode("utf-8")

def hash_password(password: str, salt: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        salt.encode("utf-8")
    ).decode("utf-8")

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)) -> str:
    to_encode = data.copy()
    expire = int((datetime.utcnow() + expires_delta).timestamp())
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)


async def reg_user(user_data: UserRegisterSchema, db: db_dependency):
    user_salt: str = generate_salt()
    try:
        create_user_statement = Users(
            **user_data.model_dump(exclude={'password'}),
            salt=user_salt,
            hashed_password=hash_password(user_data.password, user_salt)
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
    result = await db.execute(select(Users).where(Users.email == login_data.email))
    user: Optional[Users] = result.scalars().first()

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
        user_data = {"sub": payload.get("sub")}
        if user_data is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user_data

user_dependency = Annotated[Dict, Depends(get_current_user)]
