from sqlalchemy import Column, String, DateTime, func
from app.config.database import Base
import uuid

class User(Base):
    __tablename__ = "user"

    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True, unique=True)
    password = Column(String(255), nullable=False)
    gmt_create = Column(DateTime, server_default=func.now())
    gmt_modify = Column(DateTime, server_default=func.now(), onupdate=func.now())
