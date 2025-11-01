from fastapi import FastAPI
from app.controller import user_controller
from app.controller import resume_controller
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Resume Management System")



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_controller.router)
app.include_router(resume_controller.router)

@app.get("/")
def root():
    return {"message": "Resume Management System API is running"}
