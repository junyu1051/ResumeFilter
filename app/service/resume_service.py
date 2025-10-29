from utils.pdf_utils import scan_pdf
from repository.resume_repository import ResumeRepository

class ResumeService:
    def __init__(self, resume_repository):
        self.resume_repository = resume_repository

    def upload_resume(self, file, operator, db_session):
        # Scan the PDF file to extract details
        resume_data = scan_pdf(file)
        
        # Save the extracted data to the database
        resume_detail = self.resume_repository.save_resume_detail(
            name=resume_data['name'],
            phone_number=resume_data['phone_number'],
            birthday=resume_data['birthday'],
            working_exp=resume_data['working_exp'],
            education=resume_data['education'],
            area=resume_data['area'],
            resume_url=resume_data['resume_url'],
            operator=operator  # Pass operator (username)
        )
        return resume_detail


    def remove_resume(self, resume_id, db_session):
        resume = self.resume_repository.get_resume_by_id(resume_id)
        if resume:
            db_session.delete(resume)
            db_session.commit()
            return True
        return False

    def update_resume(self, resume_id, resume_data, db_session):
        return self.resume_repository.update_resume(
            resume_id,
            resume_data.get('name'),
            resume_data.get('phone_number'),
            resume_data.get('birthday'),
            resume_data.get('working_exp'),
            resume_data.get('education'),
            resume_data.get('area'),
            resume_data.get('resume_url')
        )
    
    def scan_resume(self, file):
        # This will be used to scan the PDF and extract data
        return scan_pdf(file)
