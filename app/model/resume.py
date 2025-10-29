import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.config.database import Base

class ResumeDetail(Base):
    __tablename__ = "resume_detail"

    resume_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # UUID for resume_id
    name = Column(String(100))
    phone_number = Column(String(20))
    birthday = Column(String(20))
    working_exp = Column(String(255))
    education = Column(String(255))
    area = Column(String(100))
    resume_url = Column(String(255))
    
    operator = Column(String(100))  

    gmt_create = Column(DateTime, server_default=datetime.utcnow)
    gmt_modify = Column(DateTime, server_default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, name, phone_number, birthday, working_exp, education, area, resume_url, operator):
        self.name = name
        self.phone_number = phone_number
        self.birthday = birthday
        self.working_exp = working_exp
        self.education = education
        self.area = area
        self.resume_url = resume_url
        self.operator = operator
