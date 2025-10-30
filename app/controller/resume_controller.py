from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
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

@router.get("/scan/{resume_id}")
async def scan_resume(resume_id: str, db_session: Session = Depends(get_db)):
    resume_repository = ResumeRepository(db_session)
    user_repository = UserRepository()
    resume_service = ResumeService(resume_repository, user_repository)

    resume = resume_repository.get_resume_by_id(resume_id)  # Fetch resume by ID
    if resume:
        scanned_text = await resume_service.scan_resume(resume)
        return JSONResponse(content={"scanned_text": scanned_text}, status_code=200)
    else:
        raise HTTPException(status_code=404, detail="Resume not found!")
