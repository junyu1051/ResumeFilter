from fastapi import HTTPException  # Ensure the import is here
import os
from uuid import uuid4
from app.utils.pdf_utils import scan_pdf
from app.repository.resume_repository import ResumeRepository
from app.repository.user_repository import UserRepository
from fastapi.responses import JSONResponse
import logging
import base64

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
#---------------get_resume_with_positions_and_skills-------------------------------------------
#-----------------------------------------------------------------------------------------------

    async def get_resume_with_positions_and_skills(self, resume_id: str, include_pdf: bool = False):
        data = self.resume_repository.get_resume_detail_with_position_and_skill(resume_id)
        if not data:
            raise HTTPException(status_code=404, detail="Resume not found")

        if include_pdf:
            # Read local PDF and add base64 to JSON payload
            pdf_path = self.resume_repository.get_resume_file_path(resume_id)
            if not pdf_path or not os.path.exists(pdf_path):
                raise HTTPException(status_code=404, detail="PDF file not found on disk")
            with open(pdf_path, "rb") as f:
                raw = f.read()
            data["pdf_base64"] = "data:application/pdf;base64," + base64.b64encode(raw).decode("utf-8")
        return data

    async def get_resume_pdf_path(self, resume_id: str) -> str:
        pdf_path = self.resume_repository.get_resume_file_path(resume_id)
        if not pdf_path:
            raise HTTPException(status_code=404, detail="Resume not found")
        return pdf_path


    # async def get_resume_with_positions_and_skills(self, resume_id, db_session):
    #     resume_data = self.resume_repository.get_resume_detail_with_position_and_skill(resume_id)
    #     if not resume_data:
    #         raise HTTPException(status_code=404, detail="Resume not found")
        
    #     # Convert the result to JSON and return it
    #     return JSONResponse(content=resume_data, status_code=200)

#-----------------------------------------------------------------------------------------------
#---------------get_all_resumes_paginated------------------------------------------------------
#-----------------------------------------------------------------------------------------------
 
    async def get_all_resumes_paginated(self, page: int, page_size: int):
        """Paginate resumes"""
        if page < 1 or page_size < 1:
            raise HTTPException(status_code=400, detail="Invalid page or page_size")

        offset = (page - 1) * page_size
        resumes = self.resume_repository.get_paginated_resumes(offset, page_size)

        if not resumes:
            raise HTTPException(status_code=404, detail="No resumes found")

        # Convert results to list of dicts (JSON serializable)
        result = [
            {
                "name": r.name,
                "operator": r.operator,
                "gmt_create": str(r.gmt_create),
                "gmt_modify": str(r.gmt_modify),
                "position_name": r.position_name
            }
            for r in resumes
        ]
        return result
#-----------------------------------------------------------------------------------------------
#---------------remove resume--------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------

    async def remove_resume(self, resume_id, db_session):
        # Use repository delete that returns the removed ResumeDetail or None
        resume = self.resume_repository.delete_resume_tree(resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")

        # Best-effort file removal (ignore if missing)
        try:
            if resume.resume_url and os.path.exists(resume.resume_url):
                os.remove(resume.resume_url)
        except Exception:
            # Do not fail deletion if filesystem cleanup fails
            pass

        return True


#-----------------------------------------------------------------------------------------------
#---------------update_resume_full---------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------

    async def update_resume_full(self, resume_id: str, payload: dict, db_session):
        
        detail_updates = {
            k: v for k, v in payload.items()
            if k in {"name", "phone_number", "birthday", "working_exp", "education", "area", "resume_url", "operator"}
        }
        positions = payload.get("positions", None)
        skills = payload.get("skills", None)

        updated = self.resume_repository.update_resume_full(
            resume_id_str=resume_id,
            detail_updates=detail_updates if detail_updates else None,
            positions=positions if isinstance(positions, list) else None,
            skills=skills if isinstance(skills, list) else None,
        )

        if not updated:
            raise HTTPException(status_code=404, detail="Resume not found")

        return updated




