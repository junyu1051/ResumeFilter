from app.repository.user_repository import UserRepository
from app.model.entities import User
from app.model.dto import UserRegisterDTO, UserLoginDTO
from app.utils.security import hash_password, verify_password, create_access_token
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

class UserService:
    def __init__(self):
        self.repo = UserRepository()

    def register_user(self, db: Session, dto: UserRegisterDTO):
        existing_user = self.repo.get_by_email(db, dto.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        new_user = User(
            username=dto.username,
            email=dto.email,
            password=hash_password(dto.password)
        )
        return self.repo.create_user(db, new_user)

    def login_user(self, db: Session, dto: UserLoginDTO):
        user = self.repo.get_by_email(db, dto.email)
        if not user or not verify_password(dto.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        token = create_access_token({"sub": user.email})
        return {"access_token": token, "token_type": "bearer"}
