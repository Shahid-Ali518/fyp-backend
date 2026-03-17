
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.database import create_tables
from api.category_controller import router as category_router
from api.question_controller import router as question_router
from api.transcribe_router import router as transcribe_router
from api.testAttempt_controller import router as test_attempt_router
from api.auth_controller import router as auth_router
from api.user_controller import router as user_router

app = FastAPI()


# call method to create database
create_tables()



origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "App is running now!"}


# all routes of app
app.include_router(question_router)
app.include_router(category_router)
app.include_router(transcribe_router)
app.include_router(test_attempt_router)
app.include_router(auth_router)
app.include_router(user_router)