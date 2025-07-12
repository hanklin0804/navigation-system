# 台灣導航系統 - 登入註冊功能實作規劃

## 專案概述

為台灣導航系統新增完整的使用者認證功能，包含使用者註冊、登入、登出，以及相關的安全性實作。

## 目前系統狀況

- **無正式認證系統**：目前僅使用使用者名稱識別，無密碼保護
- **架構**：Django + DRF 後端，Vanilla JS 前端
- **資料庫**：PostgreSQL + PostGIS，Redis for WebSocket
- **現有模型**：`UserLocation` 模型僅包含 `name`、`location`、`created_at`

## 實作規劃 (共 10 個步驟)

### 🔴 高優先級核心功能 (步驟 1-4)

#### 步驟 1: Django User 模型設計與資料庫遷移
**預估時間**: 2-3 小時

**技術實作**:
- 擴展 Django 的內建 User 模型或建立 Profile 模型
- 修改 `UserLocation` 模型，將 `name` 欄位改為 `user` ForeignKey
- 建立資料庫遷移檔案
- 處理現有資料的遷移策略

**檔案影響**:
- `backend/geouser/models.py`
- 新增 migration 檔案

#### 步驟 2: 實作認證 API 端點
**預估時間**: 3-4 小時

**技術實作**:
- 使用 DRF 實作註冊 API (`/api/auth/register/`)
- 實作登入 API (`/api/auth/login/`)
- 實作登出 API (`/api/auth/logout/`)
- 實作使用者資訊查詢 API (`/api/auth/user/`)
- 實作密碼重設功能 (可選)

**檔案影響**:
- 新增 `backend/authentication/` app
- `backend/authentication/views.py`
- `backend/authentication/serializers.py`
- `backend/authentication/urls.py`
- `backend/taxi_backend/urls.py`

#### 步驟 3: 設定 Token 認證系統
**預估時間**: 2-3 小時

**技術實作**:
- 選擇認證方式：DRF Token Authentication 或 JWT
- 設定 token 生成和驗證機制
- 配置 token 過期時間
- 實作 token 刷新機制

**檔案影響**:
- `backend/taxi_backend/settings.py`
- `backend/authentication/authentication.py` (如果使用自定義認證)

#### 步驟 4: 修改現有 API 端點
**預估時間**: 2-3 小時

**技術實作**:
- 更新 `UserLocationCreateView` 以使用認證使用者
- 修改 `NearbyUserSearchView` 以基於認證使用者
- 更新所有相關的 serializers
- 加入權限類別保護

**檔案影響**:
- `backend/geouser/views.py`
- `backend/geouser/serializers.py`
- `backend/chat/models.py`

### 🟡 中優先級界面與整合 (步驟 5-8)

#### 步驟 5: 前端認證界面設計
**預估時間**: 3-4 小時

**技術實作**:
- 建立登入表單 HTML/CSS
- 建立註冊表單 HTML/CSS
- 設計響應式界面
- 加入表單驗證提示

**檔案影響**:
- `frontend/index.html`
- `frontend/style.css`

#### 步驟 6: 前端認證邏輯實作
**預估時間**: 4-5 小時

**技術實作**:
- 實作登入/註冊 JavaScript 函數
- 實作 token 儲存和管理 (localStorage)
- 實作自動登入檢查
- 實作登出功能
- 修改現有 API 呼叫以包含認證 headers

**檔案影響**:
- `frontend/app.js`

#### 步驟 7: API 端點權限保護
**預估時間**: 2-3 小時

**技術實作**:
- 為所有 API 端點加入 `IsAuthenticated` 權限
- 實作使用者只能存取自己資料的權限
- 設定 API 錯誤處理

**檔案影響**:
- `backend/geouser/views.py`
- `backend/chat/views.py`

#### 步驟 8: WebSocket 認證整合
**預估時間**: 3-4 小時

**技術實作**:
- 修改 `ChatConsumer` 以驗證使用者身份
- 實作 WebSocket token 認證
- 更新前端 WebSocket 連線邏輯

**檔案影響**:
- `backend/chat/consumers.py`
- `backend/chat/routing.py`
- `frontend/app.js`

### 🟢 低優先級品質保證 (步驟 9-10)

#### 步驟 9: 測試實作
**預估時間**: 3-4 小時

**技術實作**:
- 撰寫認證 API 單元測試
- 撰寫整合測試
- 測試 WebSocket 認證
- 測試前端登入流程

**檔案影響**:
- `backend/authentication/tests.py`
- `backend/geouser/tests.py`

#### 步驟 10: 文檔更新
**預估時間**: 1-2 小時

**技術實作**:
- 更新 API 文檔 (Swagger/OpenAPI)
- 更新 CLAUDE.md
- 撰寫認證使用說明

**檔案影響**:
- `CLAUDE.md`
- `authentication-implementation-plan.md`

## 技術決策

### 認證方式選擇
**建議：DRF Token Authentication**
- 理由：簡單易實作，適合目前專案規模
- 替代方案：JWT (如需要更複雜的權限控制)

### 資料庫設計
**建議：擴展現有 UserLocation 模型**
- 將 `name` 欄位改為 `user` ForeignKey 到 Django User
- 保持向後相容性的遷移策略

### 前端狀態管理
**建議：localStorage + 簡單狀態變數**
- 適合 Vanilla JS 架構
- 簡單的 token 過期檢查機制

## 風險評估與預防

### 高風險項目
1. **資料遷移**：現有使用者資料可能遺失
   - **預防**：完整備份，分階段遷移
2. **WebSocket 認證**：複雜度較高
   - **預防**：充分測試，逐步實作

### 中風險項目
1. **API 相容性**：現有 API 呼叫可能失效
   - **預防**：保持 API 版本控制
2. **前端狀態管理**：使用者體驗可能受影響
   - **預防**：平滑的登入/登出轉換

## 總預估時間

- **核心功能** (步驟 1-4)：9-13 小時
- **界面整合** (步驟 5-8)：12-16 小時
- **品質保證** (步驟 9-10)：4-6 小時

**總計：25-35 小時** (約 3-5 個工作天)

## 實作順序建議

1. **第一階段**：完成步驟 1-2 (後端核心)
2. **第二階段**：完成步驟 3-4 (認證整合)
3. **第三階段**：完成步驟 5-6 (前端界面)
4. **第四階段**：完成步驟 7-8 (安全性)
5. **第五階段**：完成步驟 9-10 (測試文檔)

## 成功標準

✅ 使用者可以註冊新帳號  
✅ 使用者可以登入/登出  
✅ 所有 API 端點都受到保護  
✅ WebSocket 連線需要認證  
✅ 前端提供友善的認證界面  
✅ 系統安全性得到提升  
✅ 現有功能正常運作  

---

*文檔建立時間：2025-07-12*  
*預計開始實作時間：待確認*