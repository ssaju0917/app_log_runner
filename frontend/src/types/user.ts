// GET レスポンス用
export type User = {
  id: number;
  name: string;
  email: string;
  is_active: boolean;
  birth_date: string | null;   // 追加
  bio: string | null;          // 追加
  avatar_url: string | null;   // 追加
  created_at: string;
};

// POST リクエスト用
export type UserCreate = {
  name: string;
  email: string;
};

// PUT リクエスト用（追加）
export type UserUpdate = {
  name: string;
  email: string;
  birth_date: string | null;
  bio: string | null;
  avatar_url: string | null;
};