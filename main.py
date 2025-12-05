# main.py
from fastapi import FastAPI

from core.database import create_tables
from api.category_controller import router as category_router
from api.question_controller import router as question_router

app = FastAPI()


# call method to create database
create_tables()

@app.get("/")
def read_root():
    return {"message": "App is running now!"}


# all routes of app
app.include_router(question_router)
app.include_router(category_router)