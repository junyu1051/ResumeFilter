from app.model.entities import User
from sqlalchemy.orm import Session

class UserRepository:
    def get_by_email(self, db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, username: str):
        return db.query(User).filter(User.username == username).first()

    def create_user(self, db: Session, user: User):
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
