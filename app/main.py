import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from fastapi.logger import logger as fastapi_logger
from app.routers import data

app = FastAPI(debug=True)

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8081",
    "http://localhost:3000",
    "http://localhost:3001",
    "https://actively-take-home.vercel.app",
    "http://actively-take-home.vercel.app/",
    "https://automl-client.vercel.app",
    "http://automl-client.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gunicorn_error_logger = logging.getLogger("gunicorn.error")
gunicorn_logger = logging.getLogger("gunicorn")
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.handlers = gunicorn_error_logger.handlers

fastapi_logger.handlers = gunicorn_error_logger.handlers
fastapi_logger.setLevel(logging.DEBUG)

app.include_router(data.router)


@app.get("/")
def root():
    return {"message": "Welcome to the AutoML Server"}
