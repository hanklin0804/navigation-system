# 🤝 貢獻指南 Contributing Guide

感謝您對台灣導航系統的興趣！我們歡迎所有形式的貢獻，包括程式碼、文檔、問題回報和功能建議。

## 📋 貢獻方式

### 🐛 回報問題 (Issues)
- 使用 [Issue 模板](https://github.com/your-username/taiwan-navigation-system/issues/new/choose)
- 提供詳細的錯誤描述和重現步驟
- 包含系統環境資訊 (OS, Docker 版本等)
- 附上相關的日誌或截圖

### 💡 建議功能 (Feature Requests)
- 描述功能的使用場景和需求
- 解釋為什麼這個功能對用戶有價值
- 提供可能的實作方式或參考

### 🔧 提交程式碼 (Pull Requests)
- Fork 專案到您的 GitHub 帳號
- 建立功能分支進行開發
- 遵循編碼規範和測試要求
- 提交 Pull Request 並填寫模板

## 🌿 分支策略 (Branching Strategy)

我們使用 **Git Flow** 工作流程：

### 主要分支
- `main` - 穩定的生產版本
- `develop` - 開發版本，包含最新功能
- `release/*` - 發布準備分支
- `hotfix/*` - 緊急修復分支

### 功能分支
- `feature/*` - 新功能開發
- `bugfix/*` - 錯誤修復
- `docs/*` - 文檔更新
- `refactor/*` - 代碼重構

### 分支命名規範
```bash
feature/user-authentication
bugfix/chat-websocket-connection
docs/api-documentation-update
refactor/database-optimization
release/v2.1.0
hotfix/critical-security-patch
```

## 🔄 開發流程

### 1. 設定開發環境

```bash
# Fork 並複製專案
git clone https://github.com/your-username/taiwan-navigation-system.git
cd taiwan-navigation-system

# 設定上游倉庫
git remote add upstream https://github.com/original-owner/taiwan-navigation-system.git

# 建立開發環境
cp .env.sample .env
chmod +x setup.sh
./setup.sh
```

### 2. 建立功能分支

```bash
# 從 develop 建立新分支
git checkout develop
git pull upstream develop
git checkout -b feature/your-feature-name
```

### 3. 開發和測試

```bash
# 進行開發...

# 執行測試
docker compose exec django-1 python manage.py test

# 檢查代碼風格
docker compose exec django-1 flake8 .
docker compose exec django-1 black --check .
```

### 4. 提交變更

```bash
# 暫存變更
git add .

# 提交變更 (使用規範的提交訊息)
git commit -m "feat: add user authentication system"

# 推送到您的 fork
git push origin feature/your-feature-name
```

### 5. 建立 Pull Request

- 前往 GitHub 建立 Pull Request
- 選擇目標分支為 `develop`
- 填寫 PR 模板
- 等待代碼審查

## 📝 編碼規範

### Python (Django Backend)
- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 編碼風格
- 使用 [Black](https://black.readthedocs.io/) 進行代碼格式化
- 使用 [flake8](https://flake8.pycqa.org/) 進行 linting
- 函數和類別需要詳細的 docstring

```python
def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    計算兩點之間的地理距離
    
    Args:
        lat1: 起點緯度
        lng1: 起點經度
        lat2: 終點緯度
        lng2: 終點經度
        
    Returns:
        距離（公里）
    """
    # 實作...
```

### JavaScript (Frontend)
- 使用 ES6+ 語法
- 變數和函數使用 camelCase
- 常數使用 UPPER_SNAKE_CASE
- 添加適當的註解

```javascript
/**
 * 處理用戶登入
 * @param {string} username - 用戶名
 * @param {string} password - 密碼
 * @returns {Promise<Object>} 登入結果
 */
async function handleLogin(username, password) {
    // 實作...
}
```

### CSS
- 使用 BEM 命名規範
- 移動優先的響應式設計
- 使用 CSS 變數定義顏色和間距

```css
.navigation-system__header {
    background-color: var(--primary-color);
}

.navigation-system__button--primary {
    padding: var(--spacing-medium);
}
```

## 🧪 測試要求

### 後端測試
- 為新功能編寫單元測試
- API 端點需要集成測試
- 測試覆蓋率應保持在 80% 以上

```python
# tests/test_authentication.py
class AuthenticationTestCase(TestCase):
    def test_user_registration(self):
        """測試用戶註冊功能"""
        response = self.client.post('/api/auth/register/', {
            'username': 'testuser',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        })
        self.assertEqual(response.status_code, 201)
```

### 前端測試
- 關鍵功能需要手動測試
- 跨瀏覽器兼容性測試
- 響應式設計測試

## 📚 文檔要求

### API 文檔
- 使用 OpenAPI/Swagger 規範
- 包含請求/響應範例
- 說明錯誤代碼和處理方式

### 代碼文檔
- 複雜邏輯需要詳細註解
- 新功能需要更新相關文檔
- README 需要保持最新

## 🚀 發布流程

### 版本號規範
使用 [語義化版本](https://semver.org/lang/zh-TW/)：
- `MAJOR.MINOR.PATCH`
- `2.1.0` - 新功能
- `2.1.1` - 錯誤修復
- `3.0.0` - 破壞性變更

### 發布檢查清單
- [ ] 所有測試通過
- [ ] 文檔已更新
- [ ] 版本號已更新
- [ ] CHANGELOG 已更新
- [ ] 安全性檢查完成

## 💬 溝通管道

- **Issues**: 問題回報和功能建議
- **Discussions**: 一般討論和問答
- **Pull Requests**: 代碼審查和討論

## 🙏 行為準則

我們承諾為所有參與者提供友善、安全和歡迎的環境：

- 使用友善和包容的語言
- 尊重不同的觀點和經驗
- 優雅地接受建設性批評
- 專注於對社群最有利的事情
- 對其他社群成員展現同理心

違反行為準則的行為可能導致暫時或永久禁止參與專案。

## 📞 聯繫方式

如有任何問題，請隨時聯繫：
- 開啟 [Issue](https://github.com/your-username/taiwan-navigation-system/issues)
- 發起 [Discussion](https://github.com/your-username/taiwan-navigation-system/discussions)

感謝您的貢獻！🎉