from pydantic import BaseModel, EmailStr

class UserRegisterDTO(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLoginDTO(BaseModel):
    email: EmailStr
    password: str
