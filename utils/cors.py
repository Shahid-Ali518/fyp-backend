from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

def allow_frontend_origin():
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:5173"
        ],
        allow_methods=["*"],
        allow_headers=["*"],
    )
