
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.database import create_tables
from api.category_controller import router as category_router
from api.question_controller import router as question_router
from api.transcribe_router import router as transcribe_router
from api.test_attempt_controller import router as test_attempt_router
from api.auth_controller import router as auth_router
from api.user_controller import router as user_router
from api.contact_controller import router as contact_router
from api.survey_options_controller import router as survey_options_router
from api.assessment_class_range_controller import router as assessment_class_range_router
from api.report_controller import router as report_router
from api.emotion_detection_controller import router as emotion_detection_router

app = FastAPI()


# call method to create database
create_tables()



origins = [
    "http://localhost:3000",
    "http://localhost:8080",
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
app.include_router(transcribe_router)
app.include_router(contact_router)


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(category_router)
app.include_router(question_router)
app.include_router(survey_options_router)
app.include_router(assessment_class_range_router)
app.include_router(test_attempt_router)
app.include_router(emotion_detection_router)
app.include_router(report_router)
