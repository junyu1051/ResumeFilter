import uuid
from sqlalchemy import Column, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.config.database import Base

class ResumeDetail(Base):
    __tablename__ = "resume_detail"

    resume_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100))
    phone_number = Column(String(20))
    birthday = Column(String(20))
    working_exp = Column(String(255))
    education = Column(String(255))
    area = Column(String(100))
    resume_url = Column(String(255))
    operator = Column(String(100))
    user_id = Column(String(36), ForeignKey("user.user_id"))

    gmt_create = Column(DateTime, server_default=func.now())
    gmt_modify = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __init__(self, name, phone_number, birthday, working_exp, education, area, resume_url, operator, user_id):
        self.name = name
        self.phone_number = phone_number
        self.birthday = birthday
        self.working_exp = working_exp
        self.education = education
        self.area = area
        self.resume_url = resume_url
        self.operator = operator
        self.user_id = user_id

class Position(Base):
    __tablename__ = "position"

    position_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resume_detail.resume_id"))
    position_name = Column(String(100), nullable=True)
    name = Column(String(100))
    birthday = Column(String(20))

    def __init__(self, resume_id, name, birthday, position_name=None):
        self.resume_id = resume_id
        self.name = name
        self.birthday = birthday
        self.position_name = position_name

class Skill(Base):
    __tablename__ = "skill"

    skill_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resume_detail.resume_id"))
    skill_name = Column(String(100))
    name = Column(String(100))
    birthday = Column(String(20))

    def __init__(self, resume_id, skill_name, name, birthday):
        self.resume_id = resume_id
        self.skill_name = skill_name
        self.name = name
        self.birthday = birthday
