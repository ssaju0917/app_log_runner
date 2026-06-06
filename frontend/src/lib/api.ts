const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

type RequestOptions = {
  method?: "GET" | "POST" | "PUT" | "DELETE";
  body?: unknown;
};

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body } = options;

  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(error.detail || `HTTP error: ${res.status}`);
  }

  const text = await res.text();
  return text ? JSON.parse(text) : ({} as T);
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) => request<T>(path, { method: "POST", body }),
  put: <T>(path: string, body: unknown) => request<T>(path, { method: "PUT", body }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),

  // ファイルアップロード用（multipart/form-data）
  uploadAvatar: async (userId: number, file: File): Promise<{ avatar_url: string }> => {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${BASE_URL}/users/${userId}/avatar`, {
      method: "POST",
      body: formData,
      // Content-Type は FormData 使用時に自動設定されるため指定しない
    });

    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.detail || `Upload error: ${res.status}`);
    }

    return res.json();
  },
};