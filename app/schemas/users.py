from pydantic import BaseModel, EmailStr


class UserRegisterSchema(BaseModel):
    email: EmailStr
    password: str
    name: str


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str
