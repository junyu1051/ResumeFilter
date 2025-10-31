from fastapi import APIRouter, UploadFile, File, HTTPException, Depends,Query
from fastapi.responses import JSONResponse
from uuid import uuid4
from app.service.resume_service import ResumeService
from app.repository.resume_repository import ResumeRepository
from app.repository.user_repository import UserRepository
from app.config.database import SessionLocal
from sqlalchemy.orm import Session
from app.utils.security import get_current_user_username
import logging

router = APIRouter(prefix="/resume", tags=["Resume"])
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dependency to get the database session
def get_db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

   

@router.post("/upload")
async def upload_resume(resume: UploadFile = File(...), db_session: Session = Depends(get_db), operator: str = Depends(get_current_user_username)):

    try:
        logger.info(f"Received file: {resume.filename}")

    
        if resume.filename == '':
            raise HTTPException(status_code=400, detail="No selected file")

        if resume.filename.split('.')[-1].lower() not in ['pdf']:
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF allowed.")

        resume_repository = ResumeRepository(db_session)
        user_repository = UserRepository()
        resume_service = ResumeService(resume_repository, user_repository)

        resume_detail = await resume_service.upload_resume(resume, operator, db_session)

        return JSONResponse(content={"message": f"Resume {resume_detail.name} uploaded successfully!"}, status_code=200)
        
    except Exception as e:
            logger.error(f"Error while uploading resume: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
    
    
    
@router.get("/resume/{resume_id}")
async def get_resume_with_positions_and_skills(resume_id: str, db_session: Session = Depends(get_db)):
    resume_repository = ResumeRepository(db_session)
    user_repository = UserRepository()
    resume_service = ResumeService(resume_repository, user_repository)

    return await resume_service.get_resume_with_positions_and_skills(resume_id, db_session)




@router.get("/list")
async def list_resumes(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db_session: Session = Depends(get_db)
):
    """Paginated query for resumes"""
    resume_repository = ResumeRepository(db_session)
    user_repository = UserRepository()
    resume_service = ResumeService(resume_repository, user_repository)

    resumes = await resume_service.get_all_resumes_paginated(page, page_size)
    return JSONResponse(content={"data": resumes, "page": page, "page_size": page_size})




@router.delete("/remove/{resume_id}")
async def remove_resume(resume_id: str, db_session: Session = Depends(get_db)):
    resume_repository = ResumeRepository(db_session)
    user_repository = UserRepository()
    resume_service = ResumeService(resume_repository, user_repository)

    success = await resume_service.remove_resume(resume_id, db_session)
    if success:
        return JSONResponse(content={"message": "Resume removed successfully!"}, status_code=200)
    else:
        raise HTTPException(status_code=404, detail="Resume not found!")
