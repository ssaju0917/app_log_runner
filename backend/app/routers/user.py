from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.config import settings
from app import crud
import os
import uuid

router = APIRouter(prefix="/users", tags=["users"])

BUCKET_NAME  = "avatars"
# コンテナ内から Next.js の public/avatars/ を参照するパス
LOCAL_AVATAR_DIR = "/app/public/avatars"

def _is_supabase_configured() -> bool:
    """Supabase の環境変数が設定されているか確認"""
    return bool(settings.supabase_url and settings.supabase_service_role_key)

def _upload_to_supabase(contents: bytes, filename: str, content_type: str) -> str:
    """Supabase Storage にアップロードして公開URLを返す"""
    from supabase import create_client
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    supabase.storage.from_(BUCKET_NAME).upload(
        path=filename,
        file=contents,
        file_options={"content-type": content_type}
    )
    return supabase.storage.from_(BUCKET_NAME).get_public_url(filename)

def _upload_to_local(contents: bytes, filename: str) -> str:
    """ローカルの public/avatars/ に保存してパスを返す"""
    os.makedirs(LOCAL_AVATAR_DIR, exist_ok=True)
    save_path = os.path.join(LOCAL_AVATAR_DIR, filename)
    with open(save_path, "wb") as f:
        f.write(contents)
    return f"/avatars/{filename}"


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
    """プロフィール画像アップロード
    - Supabase 設定あり → Supabase Storage に保存
    - Supabase 設定なし → ローカルの public/avatars/ に保存
    """

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

    content_type_map = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png",  ".gif": "image/gif",
        ".webp": "image/webp",
    }
    content_type = content_type_map.get(ext, "application/octet-stream")

    # Supabase 設定の有無で保存先を振り分け
    if _is_supabase_configured():
        avatar_url = _upload_to_supabase(contents, filename, content_type)
    else:
        avatar_url = _upload_to_local(contents, filename)

    return {"avatar_url": avatar_url}

@router.delete("/{user_id}", response_model=UserResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """ユーザー削除"""
    user = crud.delete_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user