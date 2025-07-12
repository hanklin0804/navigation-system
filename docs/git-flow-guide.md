# 🌿 Git Flow 指南

## 📋 分支策略概覽

台灣導航系統採用 **Git Flow** 工作流程，確保代碼品質和發布穩定性。

```
main (生產)     ●─────●─────●─────●
                │     │     │     │
develop (開發)  ●─●─●─●─●─●─●─●─●─●
                │ │ │   │ │   │ │
feature/*       │ ●─●─●─┘ │   │ │
                │         │   │ │
release/*       │         ●─●─┘ │
                │               │
hotfix/*        ●─●─●───────────┘
```

## 🌱 分支類型

### 主要分支

#### `main` 分支
- **用途**: 穩定的生產版本
- **保護**: 只能透過 PR 合併
- **來源**: `release/*` 和 `hotfix/*` 分支
- **自動標籤**: 每次合併自動建立版本標籤

#### `develop` 分支  
- **用途**: 開發整合分支
- **保護**: 需要 PR 審查
- **來源**: `feature/*` 分支合併
- **目標**: 準備下一個發布版本

### 輔助分支

#### `feature/*` 分支
```bash
# 建立功能分支
git checkout develop
git pull origin develop
git checkout -b feature/user-profile-management

# 開發完成後
git push origin feature/user-profile-management
# 建立 PR 到 develop
```

**命名規範**:
- `feature/user-authentication`
- `feature/realtime-chat`
- `feature/route-optimization`

#### `release/*` 分支
```bash
# 準備發布
git checkout develop
git checkout -b release/v2.1.0

# 修復 bug、更新版本號、文檔
git commit -m "chore: prepare release v2.1.0"

# 合併到 main 和 develop
git checkout main
git merge --no-ff release/v2.1.0
git tag -a v2.1.0 -m "Release version 2.1.0"

git checkout develop  
git merge --no-ff release/v2.1.0
```

#### `hotfix/*` 分支
```bash
# 緊急修復
git checkout main
git checkout -b hotfix/critical-security-fix

# 修復完成
git checkout main
git merge --no-ff hotfix/critical-security-fix
git tag -a v2.0.1 -m "Hotfix version 2.0.1"

git checkout develop
git merge --no-ff hotfix/critical-security-fix
```

## 🔒 分支保護規則

### Main 分支保護
```yaml
保護設定:
  - 需要 Pull Request 審查: ✅
  - 需要管理員審查: ✅  
  - 限制推送: ✅
  - 需要狀態檢查通過: ✅
  - 需要分支為最新: ✅
  - 包含管理員: ✅
```

### Develop 分支保護
```yaml
保護設定:
  - 需要 Pull Request 審查: ✅
  - 需要至少 1 個審查: ✅
  - 需要狀態檢查通過: ✅
  - 允許強制推送: ❌
```

## 📝 提交訊息規範

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### 提交類型
- `feat`: 新功能
- `fix`: 錯誤修復
- `docs`: 文檔變更
- `style`: 代碼格式 (不影響邏輯)
- `refactor`: 重構
- `perf`: 效能優化
- `test`: 測試相關
- `chore`: 建置過程或輔助工具變更

### 範例
```bash
feat(auth): add user registration API
fix(chat): resolve WebSocket connection issue
docs(readme): update installation instructions
```

## 🔄 工作流程

### 1. 開發新功能
```bash
# 1. 從 develop 建立功能分支
git checkout develop
git pull origin develop
git checkout -b feature/new-awesome-feature

# 2. 開發和提交
git add .
git commit -m "feat: implement awesome new feature"

# 3. 推送並建立 PR
git push origin feature/new-awesome-feature
```

### 2. 程式碼審查
- 提交 PR 到 `develop` 分支
- 通過自動化測試
- 至少 1 個團隊成員審查
- 解決所有評論和建議

### 3. 合併策略
- **Feature → Develop**: Squash and merge
- **Release → Main**: Merge commit (保留歷史)
- **Hotfix → Main**: Merge commit

## 🚀 發布流程

### 準備發布
```bash
# 1. 建立 release 分支
git checkout develop
git checkout -b release/v2.1.0

# 2. 更新版本資訊
echo "v2.1.0" > VERSION
git add VERSION
git commit -m "chore: bump version to v2.1.0"

# 3. 最終測試和修復
# ... 進行測試，修復發現的問題

# 4. 合併到 main
git checkout main
git merge --no-ff release/v2.1.0
git tag -a v2.1.0 -m "Release version 2.1.0"

# 5. 合併回 develop
git checkout develop
git merge --no-ff release/v2.1.0

# 6. 清理分支
git branch -d release/v2.1.0
git push origin --delete release/v2.1.0
```

## 🔧 GitHub 設定建議

### 分支保護設定步驟

1. **前往 Repository Settings**
   - Settings → Branches → Add rule

2. **Main 分支規則**
   ```
   Branch name pattern: main
   ✅ Require a pull request before merging
   ✅ Require approvals (1)
   ✅ Dismiss stale PR approvals when new commits are pushed
   ✅ Require review from code owners
   ✅ Require status checks to pass before merging
   ✅ Require branches to be up to date before merging
   ✅ Include administrators
   ✅ Restrict pushes that create files larger than 100MB
   ```

3. **Develop 分支規則**
   ```
   Branch name pattern: develop  
   ✅ Require a pull request before merging
   ✅ Require approvals (1)
   ✅ Require status checks to pass before merging
   ✅ Require branches to be up to date before merging
   ```

### 自動化工作流程 (GitHub Actions)

建議在 `.github/workflows/` 目錄建立：
- `ci.yml` - 持續整合測試
- `release.yml` - 自動化發布流程
- `security.yml` - 安全性掃描

## 📊 分支管理最佳實踐

### Do's ✅
- 定期合併 develop 到 feature 分支
- 使用描述性的分支名稱
- 小而頻繁的提交
- 詳細的 PR 描述
- 及時清理合併後的分支

### Don'ts ❌
- 直接推送到 main 或 develop
- 長時間不合併的大型 feature
- 模糊的提交訊息
- 跳過代碼審查
- 在 feature 分支上進行 force push

## 🆘 緊急情況處理

### 回滾發布
```bash
# 如果需要回滾最新發布
git checkout main
git revert <commit-hash>
git push origin main
```

### 修復衝突
```bash
# 如果合併時出現衝突
git status
# 手動解決衝突文件
git add .
git commit -m "resolve merge conflicts"
```

## 📞 支援

如有 Git Flow 相關問題：
1. 查看 [Git Flow 官方文檔](https://nvie.com/posts/a-successful-git-branching-model/)
2. 在 [Discussions](https://github.com/hanklin0804/navigation-system/discussions) 提問
3. 建立 [Issue](https://github.com/hanklin0804/navigation-system/issues) 尋求協助