from fastapi import FastAPI
from app.controller import user_controller

app = FastAPI(title="Resume Management System")

app.include_router(user_controller.router)

@app.get("/")
def root():
    return {"message": "Resume Management System API is running"}
