from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config.database import SessionLocal
from app.service.user_service import UserService
from app.model.dto import UserRegisterDTO, UserLoginDTO
from app.model.vo import UserVO

router = APIRouter(prefix="/user", tags=["User"])
service = UserService()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=UserVO)
def register_user(dto: UserRegisterDTO, db: Session = Depends(get_db)):
    user = service.register_user(db, dto)
    return user

@router.post("/login")
def login_user(dto: UserLoginDTO, db: Session = Depends(get_db)):
    return service.login_user(db, dto)
