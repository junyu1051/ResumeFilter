from pydantic import BaseModel

class UserVO(BaseModel):
    user_id: str
    username: str
    email: str

    class Config:
        orm_mode = True
