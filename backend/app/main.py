from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import user_router
import os

app = FastAPI(title="My API", version="1.0.0")

origins = [
    "http://localhost:3001",
    os.getenv("FRONTEND_URL", ""),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o for o in origins if o],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # OPTIONS を明示
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
    ],
)

app.include_router(user_router)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI"}