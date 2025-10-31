from fastapi import HTTPException  # Ensure the import is here
from datetime import datetime
from app.model.resume import ResumeDetail, Position, Skill
from sqlalchemy.orm import sessionmaker
import json
import uuid

# Helper function to parse birthday strings
def _parse_birthday(birthday_str):
    try:
        # Attempt to parse the birthday string into a valid date format.
        # Handle date ranges by extracting the start date.
        if birthday_str and ' - ' in birthday_str:
            birthday_str = birthday_str.split(' - ')[0].strip()
        
        # Attempt to parse common date formats
        for fmt in ('%Y', '%b %Y', '%B %Y', '%Y-%m-%d', '%d %b %Y', '%d %B %Y'):
            try:
                return datetime.strptime(birthday_str, fmt).date()
            except ValueError:
                continue
        return None # Return None if no format matches
    except (ValueError, TypeError):
        # If it doesn't match the expected format, handle the error
        return None

class ResumeRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    
#-----------------------------------------------------------------------------------------------
#---------------save_resume_detail--------------------------------------------------------------
#-----------------------------------------------------------------------------------------------

    def save_resume_detail(self, name, phone_number, birthday, working_exp, education, area, resume_url, operator, user_id):
        try:
        # Convert birthday string to date
            birthday_date = _parse_birthday(birthday)

            # Serialize the education list to a JSON string
            education_json = json.dumps(education)

            # Create a new ResumeDetail object
            new_resume = ResumeDetail(
                name=name,
                phone_number=phone_number,
                birthday=str(birthday_date) if birthday_date else None,
                working_exp=working_exp,
                education=education_json,
                area=area,
                resume_url=resume_url,
                operator=operator,
                user_id=user_id
            )
            
            self.db_session.add(new_resume)
            self.db_session.commit()
            self.db_session.refresh(new_resume)
            return new_resume

        except Exception as e:
            self.db_session.rollback()  # Rollback if any error occurs
            raise HTTPException(status_code=500, detail=f"Error saving resume: {e}")
        

#-----------------------------------------------------------------------------------------------
#---------------save_position--------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------
       
    def save_position(self, resume_id, name, birthday, position_name=None):
        birthday_date = _parse_birthday(birthday)
        new_position = Position(
            resume_id=resume_id,
            name=name,
            birthday=str(birthday_date) if birthday_date else None,
            position_name=position_name
        )
        self.db_session.add(new_position)
        self.db_session.commit()
        return new_position
    
#-----------------------------------------------------------------------------------------------
#---------------save_skill--------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------
       
    def save_skill(self, resume_id, skill_name, name, birthday):
        birthday_date = _parse_birthday(birthday)
        new_skill = Skill(
            resume_id=resume_id,
            skill_name=skill_name,
            name=name,
            birthday=str(birthday_date) if birthday_date else None
        )
        self.db_session.add(new_skill)
        self.db_session.commit()
        return new_skill
    
   
#-----------------------------------------------------------------------------------------------
#---------------get_resume_detail_with_position_and_skill--------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------
       
    
    def get_resume_detail_with_position_and_skill(self, resume_id_str):
        # Log the input to verify the resume_id
        print(f"Received resume_id: {resume_id_str}")  # Debugging print statement
        
        # Convert the string to UUID
        try:
            resume_id = uuid.UUID(resume_id_str)
            print(f"Converted resume_id: {resume_id}")  # Log the converted UUID
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid resume_id format")
        
        # Fetch resume details
        resume_detail = self.db_session.query(ResumeDetail).filter_by(resume_id=resume_id).first()
        if not resume_detail:
            return None
        
        # Fetch position details
        positions = self.db_session.query(Position).filter_by(resume_id=resume_id).all()
        
        # Fetch skill details
        skills = self.db_session.query(Skill).filter_by(resume_id=resume_id).all()
        
        # Return as a combined dictionary, convert UUID to string
        return {
            "resume_detail": {
                "resume_id": str(resume_detail.resume_id),  # Convert UUID to string for JSON response
                "name": resume_detail.name,
                "phone_number": resume_detail.phone_number,
                "birthday": resume_detail.birthday,
                "working_exp": resume_detail.working_exp,
                "education": resume_detail.education,
                "area": resume_detail.area,
                "resume_url": resume_detail.resume_url,
                "operator": resume_detail.operator,
                "user_id": resume_detail.user_id,
            },
            "positions": [{"position_id": str(position.position_id), "position_name": position.position_name} for position in positions],
            "skills": [{"skill_id": str(skill.skill_id), "skill_name": skill.skill_name} for skill in skills]
        }


      
#-----------------------------------------------------------------------------------------------
#---------------get_paginated_resumes-----------------------------------------------------------
#-----------------------------------------------------------------------------------------------
    def get_paginated_resumes(self, offset: int, limit: int):
        """Fetch paginated resumes with position info"""
        query = (
            self.db_session.query(
                ResumeDetail.name,
                ResumeDetail.operator,
                ResumeDetail.gmt_create,
                ResumeDetail.gmt_modify,
                Position.position_name
            )
            .join(Position, Position.resume_id == ResumeDetail.resume_id)
            .order_by(ResumeDetail.gmt_create.desc())
            .offset(offset)
            .limit(limit)
        )
        return query.all()
    



    def get_resumes_by_operator(self, operator):
        # Fetch all resumes uploaded by a specific operator (username)
        return self.db_session.query(ResumeDetail).filter_by(operator=operator).all()

    def get_resumes_by_user(self, user_id):
        # Fetch all resumes uploaded by a specific user
        return self.db_session.query(ResumeDetail).filter_by(user_id=user_id).all()

    def get_resume_by_id(self, resume_id):
        # Fetch a resume by its ID
        return self.db_session.query(ResumeDetail).filter_by(resume_id=resume_id).first()

    def update_resume(self, resume_id, name=None, phone_number=None, birthday=None, working_exp=None, education=None, area=None, resume_url=None):
        resume = self.db_session.query(ResumeDetail).filter_by(resume_id=resume_id).first()
        if resume:
            # Update resume fields
            if name:
                resume.name = name
            if phone_number:
                resume.phone_number = phone_number
            if birthday:
                resume.birthday = birthday
            if working_exp:
                resume.working_exp = working_exp
            if education:
                resume.education = education
            if area:
                resume.area = area
            if resume_url:
                resume.resume_url = resume_url
            resume.gmt_modify = datetime.utcnow()  # This is correct since it calls the function to get the current time
            self.db_session.commit()
            return resume
        return None
