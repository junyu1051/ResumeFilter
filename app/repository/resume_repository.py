from datetime import datetime
from model.resume import ResumeDetail
from sqlalchemy.orm import sessionmaker


class ResumeRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    def save_resume_detail(self, name, phone_number, birthday, working_exp, education, area, resume_url, operator):
        # Create a new ResumeDetail object
        new_resume = ResumeDetail(
            name=name,
            phone_number=phone_number,
            birthday=birthday,
            working_exp=working_exp,
            education=education,
            area=area,
            resume_url=resume_url,
            operator=operator  # Save the operator's name directly
        )
        
        # Save it to the database
        self.db_session.add(new_resume)
        self.db_session.commit()
        return new_resume

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
            resume.gmt_modify = datetime.utcnow()  # Set modify time
            self.db_session.commit()
            return resume
        return None
