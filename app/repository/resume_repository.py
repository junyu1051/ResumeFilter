from fastapi import HTTPException  # Ensure the import is here
from datetime import datetime,date
from app.model.resume import ResumeDetail, Position, Skill
from sqlalchemy.orm import sessionmaker
import json
import uuid
from sqlalchemy.exc import SQLAlchemyError

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
    


def _to_iso(dt):
    if isinstance(dt, datetime):
        return dt.isoformat()
    if isinstance(dt, date):
        return dt.isoformat()
    return dt

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
    
    
    # def get_resume_file_path(self, resume_id_str: str) -> str | None:
    #     try:
    #         resume_uuid = uuid.UUID(resume_id_str)
    #     except ValueError:
    #         raise HTTPException(status_code=400, detail="Invalid resume_id format")
    #     resume = (
    #         self.db_session.query(ResumeDetail)
    #         .filter_by(resume_id=resume_uuid)
    #         .first()
    #     )
    #     return resume.resume_url if resume else None
    
    # def get_resume_detail_with_position_and_skill(self, resume_id_str):
    #     # Log the input to verify the resume_id
    #     print(f"Received resume_id: {resume_id_str}")  # Debugging print statement
        
    #     # Convert the string to UUID
    #     try:
    #         resume_id = uuid.UUID(resume_id_str)
    #         print(f"Converted resume_id: {resume_id}")  # Log the converted UUID
    #     except ValueError:
    #         raise HTTPException(status_code=400, detail="Invalid resume_id format")
        
    #     # Fetch resume details
    #     resume_detail = self.db_session.query(ResumeDetail).filter_by(resume_id=resume_id).first()
    #     if not resume_detail:
    #         return None
        
    #     # Fetch position details
    #     positions = self.db_session.query(Position).filter_by(resume_id=resume_id).all()
        
    #     # Fetch skill details
    #     skills = self.db_session.query(Skill).filter_by(resume_id=resume_id).all()
        
    #     # Return as a combined dictionary, convert UUID to string
    #     return {
    #         "resume_detail": {
    #             "resume_id": str(resume_detail.resume_id),  # Convert UUID to string for JSON response
    #             "name": resume_detail.name,
    #             "phone_number": resume_detail.phone_number,
    #             "birthday": resume_detail.birthday,
    #             "working_exp": resume_detail.working_exp,
    #             "education": resume_detail.education,
    #             "area": resume_detail.area,
    #             "resume_url": resume_detail.resume_url,
    #             "operator": resume_detail.operator,
    #             "user_id": resume_detail.user_id,
    #         },
    #         "positions": [{"position_id": str(position.position_id), "position_name": position.position_name} for position in positions],
    #         "skills": [{"skill_id": str(skill.skill_id), "skill_name": skill.skill_name} for skill in skills]
    #     }
    
    


      
    def get_resume_detail_with_position_and_skill(self, resume_id_str: str) -> dict | None:
        try:
            resume_id = uuid.UUID(resume_id_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid resume_id format")

        resume_detail = (
            self.db_session.query(ResumeDetail)
            .filter_by(resume_id=resume_id)
            .first()
        )
        if not resume_detail:
            return None

        positions = self.db_session.query(Position).filter_by(resume_id=resume_id).all()
        skills = self.db_session.query(Skill).filter_by(resume_id=resume_id).all()

        return {
            "resume_detail": {
                "resume_id": str(resume_detail.resume_id),
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
            "positions": [
                {"position_id": str(p.position_id), "position_name": p.position_name}
                for p in positions
            ],
            "skills": [
                {"skill_id": str(s.skill_id), "skill_name": s.skill_name}
                for s in skills
            ],
        }

    def get_resume_file_path(self, resume_id_str: str) -> str | None:
        try:
            resume_uuid = uuid.UUID(resume_id_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid resume_id format")

        resume = (
            self.db_session.query(ResumeDetail)
            .filter_by(resume_id=resume_uuid)
            .first()
        )
        return resume.resume_url if resume else None
    

#-----------------------------------------------------------------------------------------------
#---------------get_paginated_resumes-----------------------------------------------------------
#-----------------------------------------------------------------------------------------------
    def get_paginated_resumes(self, offset: int, limit: int):
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
    

      
#-----------------------------------------------------------------------------------------------
#---------------delete_resume_tree-------------------------------------------------------------
#-----------------------------------------------------------------------------------------------

    def delete_resume_tree(self, resume_id_str: str):
        try:
            resume_uuid = uuid.UUID(resume_id_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid resume_id format")

        try:
            # Fetch resume to (a) verify existence and (b) get resume_url for file removal by service
            resume = (
                self.db_session.query(ResumeDetail)
                .filter_by(resume_id=resume_uuid)
                .first()
            )
            if not resume:
                return None  # service will 404

            # Delete children first (no ON DELETE CASCADE defined in models)
            self.db_session.query(Skill).filter_by(resume_id=resume_uuid).delete(synchronize_session=False)
            self.db_session.query(Position).filter_by(resume_id=resume_uuid).delete(synchronize_session=False)

            # Delete parent
            self.db_session.delete(resume)
            self.db_session.commit()
            return resume  # return the object so service can remove the file
        except Exception as e:
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail=f"Error deleting resume: {e}")
        

    
#-----------------------------------------------------------------------------------------------
#---------------update_resume_full-------------------------------------------------------------
#-----------------------------------------------------------------------------------------------
        
  
  
    def update_resume_full(
        self,
        resume_id_str: str,
        detail_updates: dict | None,
        positions: list[str] | None,
        skills: list[str] | None,
    ):
       
        # Validate UUID
        try:
            resume_uuid = uuid.UUID(resume_id_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid resume_id format")

        try:
            resume: ResumeDetail | None = (
                self.db_session.query(ResumeDetail)
                .filter_by(resume_id=resume_uuid)
                .first()
            )
            if not resume:
                raise HTTPException(status_code=404, detail="Resume not found")

            # ------- Update resume_detail (partial) -------
            if detail_updates:
                name = detail_updates.get("name")
                phone_number = detail_updates.get("phone_number")
                birthday = detail_updates.get("birthday")
                working_exp = detail_updates.get("working_exp")
                education = detail_updates.get("education")
                area = detail_updates.get("area")
                resume_url = detail_updates.get("resume_url")
                operator = detail_updates.get("operator")

                if name is not None:
                    resume.name = name
                if phone_number is not None:
                    resume.phone_number = phone_number
                if birthday is not None:
                    # normalize using your helper
                    from app.repository.resume_repository import _parse_birthday  # local import to avoid circulars
                    parsed = _parse_birthday(birthday)
                    resume.birthday = str(parsed) if parsed else (birthday or None)
                if working_exp is not None:
                    resume.working_exp = working_exp
                if education is not None:
                    # accept list or string; store JSON string (your model stores varchar) :contentReference[oaicite:3]{index=3}
                    if isinstance(education, (list, tuple)):
                        resume.education = json.dumps(list(education), ensure_ascii=False)
                    else:
                        # assume already-serialized string
                        resume.education = str(education)
                if area is not None:
                    resume.area = area
                if resume_url is not None:
                    resume.resume_url = resume_url
                if operator is not None:
                    resume.operator = operator

                resume.gmt_modify = datetime.utcnow()  # explicit touch

            # ------- Replace positions if provided -------
            if positions is not None:
                # wipe and recreate (since no ON DELETE CASCADE & no unique constraints) :contentReference[oaicite:4]{index=4}
                self.db_session.query(Position).filter_by(resume_id=resume_uuid).delete(synchronize_session=False)
                # use latest name/birthday from resume_detail for child rows
                for p in positions:
                    pos = Position(
                        resume_id=resume_uuid,
                        position_name=p,
                        name=resume.name or "",
                        birthday=resume.birthday or None
                    )
                    self.db_session.add(pos)

            # ------- Replace skills if provided -------
            if skills is not None:
                self.db_session.query(Skill).filter_by(resume_id=resume_uuid).delete(synchronize_session=False)
                for s in skills:
                    sk = Skill(
                        resume_id=resume_uuid,
                        skill_name=s,
                        name=resume.name or "",
                        birthday=resume.birthday or None
                    )
                    self.db_session.add(sk)

            self.db_session.commit()
            self.db_session.refresh(resume)

            # Prepare payload (convert UUIDs for JSON)
            updated_positions = (
                self.db_session.query(Position)
                .filter_by(resume_id=resume_uuid)
                .all()
            )
            updated_skills = (
                self.db_session.query(Skill)
                .filter_by(resume_id=resume_uuid)
                .all()
            )

            return {
                "resume_detail": {
                    "resume_id": str(resume.resume_id),
                    "name": resume.name,
                    "phone_number": resume.phone_number,
                    # ✅ normalize birthdays that might be date/datetime
                    "birthday": _to_iso(resume.birthday),
                    "working_exp": resume.working_exp,
                    "education": resume.education,
                    "area": resume.area,
                    "resume_url": resume.resume_url,
                    "operator": resume.operator,
                    "user_id": resume.user_id,
                    "gmt_create": _to_iso(resume.gmt_create),
                    "gmt_modify": _to_iso(resume.gmt_modify),
                },
                "positions": [
                    {
                        "position_id": str(p.position_id),
                        "position_name": p.position_name,
                        "name": p.name,
                        "birthday": _to_iso(p.birthday),
                    }
                    for p in updated_positions
                ],
                "skills": [
                    {
                        "skill_id": str(sk.skill_id),
                        "skill_name": sk.skill_name,
                        "name": sk.name,
                        "birthday": _to_iso(sk.birthday),
                    }
                    for sk in updated_skills
                ],
            }

        except HTTPException:
            # pass through known HTTP errors
            raise
        except SQLAlchemyError as e:
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {e}")
        except Exception as e:
            self.db_session.rollback()
            raise HTTPException(status_code=500, detail=f"Error updating resume: {e}")










#-----------------------------------------------------------------------------------------------


    def get_resumes_by_operator(self, operator):
        # Fetch all resumes uploaded by a specific operator (username)
        return self.db_session.query(ResumeDetail).filter_by(operator=operator).all()

    def get_resumes_by_user(self, user_id):
        # Fetch all resumes uploaded by a specific user
        return self.db_session.query(ResumeDetail).filter_by(user_id=user_id).all()

    def get_resume_by_id(self, resume_id):
        # Fetch a resume by its ID
        return self.db_session.query(ResumeDetail).filter_by(resume_id=resume_id).first()

