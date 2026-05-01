from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from auth.auth import reg_user, auth_user, create_access_token, user_dependency
from db.db import db_dependency
from schemas.users import UserRegisterSchema, UserLoginSchema

auth_router = APIRouter(prefix='/auth', tags=['auth'])

@auth_router.post('/register')
async def register_user(user_data: UserRegisterSchema, db: db_dependency):
    try:
        return await reg_user(user_data=user_data, db=db)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'An error has occurred: {ex}'
        )

@auth_router.post('/login')
async def login_for_access_token(login_data: UserLoginSchema, db: db_dependency):
    user = await auth_user(login_data=login_data, db=db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password'
        )

    access_token = create_access_token(
        data={'sub': {'email': user.email}}
    )

    return {'access_token': access_token, 'token_type': 'bearer'}

@auth_router.post("/token")
async def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: db_dependency):
    user = await auth_user(
        UserLoginSchema(email=form_data.username, password=form_data.password),
        db=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate user.")
    access_token = create_access_token(
        data={"sub": user.email}
    )
    return {'access_token': access_token, 'token_type': 'bearer'}

@auth_router.get("/current_user")
async def get_current_user(user: user_dependency):
    return {"user": user}