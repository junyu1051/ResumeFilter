from fastapi import HTTPException  # Ensure the import is here
import os
from uuid import uuid4
from app.utils.pdf_utils import scan_pdf
from app.repository.resume_repository import ResumeRepository
from app.repository.user_repository import UserRepository
import logging

class ResumeService:
    def __init__(self, resume_repository, user_repository):
        self.resume_repository = resume_repository
        self.user_repository = user_repository

    

#-----------------------------------------------------------------------------------------------
#---------------upload_resume-------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------


    async def upload_resume(self, file, operator, db_session):

        logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.DEBUG)

        try:
            # Define the upload directory
            upload_dir = "resumes"
            os.makedirs(upload_dir, exist_ok=True)

            # Generate a unique filename
            file_extension = file.filename.split('.')[-1]
            unique_filename = f"{uuid4()}.{file_extension}"
            file_path = os.path.join(upload_dir, unique_filename)


            try:
            # Save the file
                with open(file_path, "wb") as buffer:
                    buffer.write(await file.read())
                    logger.info(f"File {file.filename} saved successfully to {file_path}.")
            except Exception as e:
                logger.error(f"Error saving file: {e}")
                raise HTTPException(status_code=500, detail="Error saving the file.")
            
            try:
            # Scan the PDF file to extract details
                resume_data = scan_pdf(file_path)
                logger.info("PDF scanned successfully.")

            except Exception as e:
                logger.error(f"Error scanning PDF: {e}")
                raise HTTPException(status_code=500, detail="Error scanning the PDF.")

            # Get user_id from operator (username)
            # user = self.user_repository.get_by_username(db_session, operator)
            # if not user:
            #     user = None 
            #     logger.error(f"User {operator} not found.")
            #     # Handle case where user is not found, maybe raise an exception
                

            # Save the extracted data to the database
            resume_detail = self.resume_repository.save_resume_detail(
                name=resume_data['name'],
                phone_number=resume_data['phone_number'],
                birthday=resume_data['birthday'],
                working_exp=resume_data['working_exp'],
                education=resume_data['education'],
                area=resume_data['area'],
                resume_url=file_path,
                operator=operator,
                user_id= "null"  
            )
            logger.info(f"Resume details for {resume_data['name']} saved to the database.")

            try:
                # Save position and skill information
                self.resume_repository.save_position(
                    resume_id=resume_detail.resume_id,
                    name=resume_data['name'],
                    birthday=resume_data['birthday']
                )
                logger.info("Position saved successfully.")
            except Exception as e:
                logger.error(f"Error saving position: {e}")


            # Save skill information
            if 'skills' in resume_data and resume_data['skills']:
                for skill_name in resume_data['skills']:
                    try:
                        self.resume_repository.save_skill(
                            resume_id=resume_detail.resume_id,
                            skill_name=skill_name,
                            name=resume_data['name'],
                            birthday=resume_data['birthday']
                        )
                        logger.info(f"Skill {skill_name} saved successfully.")
                    except Exception as e:
                        logger.error(f"Error saving skill {skill_name}: {e}")
            else:
                self.resume_repository.save_skill(
                    resume_id=resume_detail.resume_id,
                    skill_name=None,
                    name=resume_data['name'],
                    birthday=resume_data['birthday']
                )

        except Exception as e:
            logger.error(f"Error in upload_resume: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        

        return resume_detail
    

#-----------------------------------------------------------------------------------------------
#---------------remove resume--------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------


    async def remove_resume(self, resume_id, db_session):
        resume = self.resume_repository.get_resume_by_id(resume_id)
        if resume:
            # Remove the file from the filesystem
            if os.path.exists(resume.resume_url):
                os.remove(resume.resume_url)
            
            db_session.delete(resume)
            db_session.commit()
            return True
        return False


#-----------------------------------------------------------------------------------------------
#---------------update_resume-------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------

    async def update_resume(self, resume_id, resume_data, db_session):
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

#-----------------------------------------------------------------------------------------------
#---------------scan_resume---------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------

    async def scan_resume(self, resume):
        # This will be used to scan the PDF and extract data
        # Assuming resume object has a 'resume_url' attribute with the file path
        return scan_pdf(resume.resume_url)
