# 📚 API 文檔 API Documentation

台灣導航系統提供完整的 RESTful API 和 WebSocket 介面，支援用戶認證、位置管理、即時通訊等功能。

## 🔗 API 基本資訊

- **Base URL**: `https://your-domain.com/api/`
- **認證方式**: Token Authentication
- **內容格式**: JSON
- **編碼**: UTF-8

## 🔑 認證機制

### Token 認證

所有需要認證的 API 請求都必須在 Header 中包含 Token：

```http
Authorization: Token your-token-here
```

### 取得 Token

通過登入 API 取得 Token：

```bash
curl -X POST https://your-domain.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your-username", "password": "your-password"}'
```

## 👤 認證 API

### 1. 用戶註冊

註冊新用戶帳號。

**端點**: `POST /api/auth/register/`

**請求參數**:
```json
{
  "username": "string (required)",
  "email": "string (required)",
  "password": "string (required, min: 8)",
  "password_confirm": "string (required)"
}
```

**成功回應** (201):
```json
{
  "user": {
    "id": 1,
    "username": "newuser",
    "email": "newuser@example.com",
    "date_joined": "2025-07-12T10:30:00Z",
    "last_login": null
  },
  "token": "abc123...",
  "message": "註冊成功"
}
```

**錯誤回應** (400):
```json
{
  "username": ["此欄位為必填欄位。"],
  "password": ["密碼確認不一致"]
}
```

### 2. 用戶登入

使用用戶名和密碼登入。

**端點**: `POST /api/auth/login/`

**請求參數**:
```json
{
  "username": "string (required)",
  "password": "string (required)"
}
```

**成功回應** (200):
```json
{
  "user": {
    "id": 1,
    "username": "user123",
    "email": "user@example.com",
    "date_joined": "2025-07-12T10:30:00Z",
    "last_login": "2025-07-12T11:00:00Z"
  },
  "token": "def456...",
  "message": "登入成功"
}
```

### 3. 用戶登出

登出並撤銷 Token。

**端點**: `POST /api/auth/logout/`

**認證**: Required

**成功回應** (200):
```json
{
  "message": "登出成功"
}
```

### 4. 取得用戶資料

取得當前認證用戶的資料。

**端點**: `GET /api/auth/user/`

**認證**: Required

**成功回應** (200):
```json
{
  "id": 1,
  "username": "user123",
  "email": "user@example.com",
  "date_joined": "2025-07-12T10:30:00Z",
  "last_login": "2025-07-12T11:00:00Z"
}
```

## 📍 位置管理 API

### 1. 設定/更新位置

設定或更新用戶的地理位置。

**端點**: `POST /api/users/`

**認證**: Required

**請求參數**:
```json
{
  "lat": 25.0330,
  "lng": 121.5654
}
```

**成功回應** (200):
```json
{
  "username": "user123",
  "lat": 25.0330,
  "lng": 121.5654,
  "created_at": "2025-07-12T11:15:00Z",
  "message": "已建立", // 或 "已更新"
  "served_by": "django-1"
}
```

### 2. 搜尋附近用戶

根據指定半徑搜尋附近的其他用戶。

**端點**: `GET /api/users/nearby/`

**認證**: Required

**查詢參數**:
- `radius` (optional): 搜尋半徑（公里），預設值為 2

**範例請求**:
```bash
GET /api/users/nearby/?radius=5
```

**成功回應** (200):
```json
{
  "center": {
    "lat": 25.0330,
    "lng": 121.5654
  },
  "radius_km": 5.0,
  "nearby": [
    {
      "username": "user456",
      "lat": 25.0335,
      "lng": 121.5650,
      "created_at": "2025-07-12T10:45:00Z"
    },
    {
      "username": "user789",
      "lat": 25.0325,
      "lng": 121.5660,
      "created_at": "2025-07-12T11:00:00Z"
    }
  ]
}
```

## 💬 WebSocket API

### 即時聊天

建立 WebSocket 連線以進行即時聊天。

**端點**: `wss://your-domain.com/ws/chat/{sender_username}/{recipient_username}/`

**認證**: 透過 URL 參數或連線時驗證

#### 連線範例

```javascript
const ws = new WebSocket('wss://your-domain.com/ws/chat/user1/user2/');

ws.onopen = function(event) {
    console.log('WebSocket 連線已建立');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('收到訊息:', data);
};

ws.onclose = function(event) {
    console.log('WebSocket 連線已關閉');
};
```

#### 發送訊息

```javascript
const message = {
    message: "你好！這是一條測試訊息"
};
ws.send(JSON.stringify(message));
```

#### 接收訊息格式

```json
{
  "sender_name": "user1",
  "message": "你好！這是一條測試訊息"
}
```

## 🚨 錯誤處理

### HTTP 狀態碼

| 狀態碼 | 說明 |
|--------|------|
| 200 | 請求成功 |
| 201 | 資源建立成功 |
| 400 | 請求參數錯誤 |
| 401 | 認證失敗 |
| 403 | 權限不足 |
| 404 | 資源不存在 |
| 409 | 資源衝突 |
| 500 | 伺服器內部錯誤 |

### 錯誤回應格式

```json
{
  "error": "錯誤描述",
  "detail": "詳細錯誤資訊",
  "code": "ERROR_CODE"
}
```

### 常見錯誤

#### 認證錯誤 (401)
```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### 權限錯誤 (403)
```json
{
  "detail": "You do not have permission to perform this action."
}
```

#### 驗證錯誤 (400)
```json
{
  "username": ["此欄位為必填欄位。"],
  "password": ["確保此欄位至少包含 8 個字元。"]
}
```

## 📊 API 限制

### 請求頻率限制

| 端點類型 | 限制 |
|----------|------|
| 認證 API | 10 requests/minute |
| 位置 API | 60 requests/minute |
| 搜尋 API | 30 requests/minute |

### 資料限制

| 參數 | 限制 |
|------|------|
| 用戶名長度 | 3-150 字元 |
| 密碼長度 | 8-128 字元 |
| 搜尋半徑 | 0.1-50 公里 |
| 聊天訊息 | 1-1000 字元 |

## 🧪 測試 API

### 使用 cURL

```bash
# 註冊用戶
curl -X POST https://your-domain.com/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "testpass123", "password_confirm": "testpass123"}'

# 登入
curl -X POST https://your-domain.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'

# 設定位置
curl -X POST https://your-domain.com/api/users/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your-token-here" \
  -d '{"lat": 25.0330, "lng": 121.5654}'

# 搜尋附近用戶
curl -X GET "https://your-domain.com/api/users/nearby/?radius=5" \
  -H "Authorization: Token your-token-here"
```

### 使用 Python requests

```python
import requests

BASE_URL = "https://your-domain.com/api"

# 註冊
response = requests.post(f"{BASE_URL}/auth/register/", json={
    "username": "testuser",
    "email": "test@example.com", 
    "password": "testpass123",
    "password_confirm": "testpass123"
})

# 登入
response = requests.post(f"{BASE_URL}/auth/login/", json={
    "username": "testuser",
    "password": "testpass123"
})
token = response.json()["token"]

# 設定位置
headers = {"Authorization": f"Token {token}"}
response = requests.post(f"{BASE_URL}/users/", 
    json={"lat": 25.0330, "lng": 121.5654},
    headers=headers
)
```

## 📖 互動式文檔

系統提供兩種互動式 API 文檔：

- **Swagger UI**: `https://your-domain.com/swagger/`
- **ReDoc**: `https://your-domain.com/redoc/`

這些工具允許您：
- 瀏覽所有可用的 API 端點
- 查看詳細的請求/回應格式
- 直接在瀏覽器中測試 API
- 下載 OpenAPI 規範檔案

## 🔄 版本控制

API 版本透過 URL 路徑控制：

- 當前版本: `/api/` (v1)
- 未來版本: `/api/v2/`, `/api/v3/` 等

## 📞 支援

如需 API 相關協助：

1. 查看 [互動式文檔](https://your-domain.com/swagger/)
2. 搜尋或建立 [Issue](https://github.com/your-username/taiwan-navigation-system/issues)
3. 參與 [Discussions](https://github.com/your-username/taiwan-navigation-system/discussions)