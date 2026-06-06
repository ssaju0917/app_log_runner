from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.config import settings
from app import crud
from supabase import create_client
import os
import uuid

router = APIRouter(prefix="/users", tags=["users"])

# Supabase クライアントの初期化
supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)

BUCKET_NAME = "avatars"

@router.get("/", response_model=list[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """ユーザー一覧取得"""
    return crud.get_users(db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """ユーザー1件取得"""
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """ユーザー作成"""
    return crud.create_user(db, user=user)

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """ユーザー更新（PUT）"""
    updated = crud.update_user(db, user_id=user_id, user=user)
    if updated is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated

@router.post("/{user_id}/avatar", response_model=dict)
async def upload_avatar(user_id: int, file: UploadFile = File(...)):
    """プロフィール画像を Supabase Storage にアップロード"""

    # 拡張子チェック
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"許可されていない拡張子です。使用可能: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # ファイルサイズチェック（5MB上限）
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="ファイルサイズは5MB以下にしてください")

    # ファイル名をUUIDで一意に生成
    filename = f"user_{user_id}_{uuid.uuid4().hex}{ext}"

    # content_type の設定
    content_type_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    content_type = content_type_map.get(ext, "application/octet-stream")

    # Supabase Storage にアップロード
    supabase.storage.from_(BUCKET_NAME).upload(
        path=filename,
        file=contents,
        file_options={"content-type": content_type}
    )

    # 公開URLを取得
    public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(filename)

    return {"avatar_url": public_url}

@router.delete("/{user_id}", response_model=UserResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """ユーザー削除"""
    user = crud.delete_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user