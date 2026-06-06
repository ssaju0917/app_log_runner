from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import user_router
import os

app = FastAPI(title="My API", version="1.0.0")

# 許可するオリジン（環境変数から取得）
origins = [
    "http://localhost:3001",                              # ローカル開発用
    os.getenv("FRONTEND_URL", ""),                        # 本番Vercel URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o for o in origins if o],              # 空文字を除外
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI"}