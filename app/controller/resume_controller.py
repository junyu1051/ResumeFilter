from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from uuid import uuid4
from service.resume_service import ResumeService
from repository.resume_repository import ResumeRepository
from database import SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

# Dependency to get the database session
def get_db_session():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

@app.post("/upload")
async def upload_resume(resume: UploadFile = File(...), db_session: Session = Depends(get_db_session)):
    if resume.filename == '':
        raise HTTPException(status_code=400, detail="No selected file")

    if resume.filename.split('.')[-1].lower() not in ['pdf']:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF allowed.")

    operator = get_current_user_username()  # This should get the current logged-in user's username

    resume_repository = ResumeRepository(db_session)
    resume_service = ResumeService(resume_repository)

    resume_detail = await resume_service.upload_resume(resume, operator, db_session)

    return JSONResponse(content={"message": f"Resume {resume_detail.name} uploaded successfully!"}, status_code=200)

@app.delete("/remove/{resume_id}")
async def remove_resume(resume_id: str, db_session: Session = Depends(get_db_session)):
    resume_repository = ResumeRepository(db_session)
    resume_service = ResumeService(resume_repository)

    success = await resume_service.remove_resume(resume_id, db_session)
    if success:
        return JSONResponse(content={"message": "Resume removed successfully!"}, status_code=200)
    else:
        raise HTTPException(status_code=404, detail="Resume not found!")

@app.get("/scan/{resume_id}")
async def scan_resume(resume_id: str, db_session: Session = Depends(get_db_session)):
    resume_repository = ResumeRepository(db_session)
    resume_service = ResumeService(resume_repository)

    resume = await resume_repository.get_resumes_by_operator(resume_id)  # Fetch resume by ID
    if resume:
        scanned_text = await resume_service.scan_resume(resume)
        return JSONResponse(content={"scanned_text": scanned_text}, status_code=200)
    else:
        raise HTTPException(status_code=404, detail="Resume not found!")
