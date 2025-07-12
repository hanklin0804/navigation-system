# 📦 安裝指南 Installation Guide

本文檔提供台灣導航系統的詳細安裝和配置說明。

## 🔧 系統需求

### 硬體需求
- **CPU**: 4 核心或以上
- **RAM**: 8GB 或以上（推薦 16GB）
- **磁碟空間**: 20GB 可用空間
- **網路**: 穩定的網際網路連線

### 軟體需求
- **Docker**: 24.0 或以上版本
- **Docker Compose**: v2.0 或以上版本
- **Git**: 用於複製專案
- **作業系統**: Linux (Ubuntu 20.04+), macOS, Windows 10+ with WSL2

## 🚀 快速安裝

### 1. 複製專案

```bash
git clone https://github.com/your-username/taiwan-navigation-system.git
cd taiwan-navigation-system
```

### 2. 環境設定

```bash
# 複製環境變數範例檔案
cp .env.sample .env

# 編輯環境變數 (可選)
nano .env
```

### 3. 執行安裝腳本

```bash
chmod +x setup.sh
./setup.sh
```

這個腳本會自動：
- 下載台灣 OSM 地圖資料
- 處理 OSRM 路線規劃檔案
- 生成 SSL 自簽名憑證
- 啟動所有 Docker 容器

### 4. 初始化資料庫

```bash
# 等待容器完全啟動後執行
docker compose exec django-1 python manage.py migrate
```

### 5. 建立管理員帳號 (可選)

```bash
docker compose exec django-1 python manage.py createsuperuser
```

## 🔧 手動安裝

如果您想要更多控制權，可以手動執行安裝步驟：

### 1. 下載 OSM 資料

```bash
mkdir -p osm_data
cd osm_data
wget https://download.geofabrik.de/asia/taiwan-latest.osm.pbf -O taiwan.pbf
cd ..
```

### 2. 處理 OSRM 檔案

```bash
docker run -t -v "${PWD}/osm_data:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/taiwan.pbf
docker run -t -v "${PWD}/osm_data:/data" osrm/osrm-backend osrm-partition /data/taiwan.osrm
docker run -t -v "${PWD}/osm_data:/data" osrm/osrm-backend osrm-customize /data/taiwan.osrm

# 移動檔案到正確位置
mkdir -p osm_data/osrm_files
mv osm_data/taiwan.osrm* osm_data/osrm_files/
```

### 3. 生成 SSL 憑證

```bash
mkdir -p certbot/conf/selfsigned

# 取得您的 IP 地址
YOUR_IP=$(hostname -I | awk '{print $1}')

# 生成憑證
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout certbot/conf/selfsigned/privkey.pem \
    -out certbot/conf/selfsigned/fullchain.pem \
    -config <(echo "[req]"; echo "distinguished_name=req"; echo "[san]"; echo "subjectAltName=IP:${YOUR_IP}") \
    -extensions san
```

### 4. 啟動服務

```bash
docker compose up -d --build
```

## ⚙️ 配置說明

### 環境變數配置

主要的環境變數說明：

| 變數名 | 預設值 | 說明 |
|--------|--------|------|
| `POSTGRES_USER` | user | PostgreSQL 使用者名 |
| `POSTGRES_PASSWORD` | password | PostgreSQL 密碼 |
| `POSTGRES_DB` | db | 資料庫名稱 |
| `DJANGO_SECRET_KEY` | - | Django 密鑰（必須設定）|
| `DJANGO_DEBUG` | True | 除錯模式 |
| `SERVER_IP` | localhost | 伺服器 IP 地址 |

### 前端 API 地址配置

編輯 `frontend/app.js` 文件，更新 API 地址：

```javascript
// 將以下 IP 地址更改為您的伺服器 IP
const API_BASE_URL = 'https://YOUR_IP_ADDRESS';
```

### Nginx 配置

如需自訂 Nginx 設定，可編輯 `nginx/nginx.conf` 文件。

## 🔍 驗證安裝

### 1. 檢查容器狀態

```bash
docker compose ps
```

所有容器應該顯示為 "Up" 狀態。

### 2. 檢查服務

- **前端**: https://your-ip-address
- **API 文檔**: https://your-ip-address/swagger/
- **Django Admin**: https://your-ip-address/admin/

### 3. 測試 API

```bash
# 測試用戶註冊
curl -X POST https://your-ip-address/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "email": "test@example.com", "password": "testpass123", "password_confirm": "testpass123"}' \
  -k
```

## 🐛 常見問題

### Q: 容器啟動失敗
**A**: 檢查 Docker 版本和可用記憶體。確保至少有 8GB RAM。

### Q: OSM 資料下載失敗
**A**: 檢查網路連線，或手動下載檔案到 `osm_data/` 目錄。

### Q: SSL 憑證錯誤
**A**: 瀏覽器會警告自簽名憑證不安全，點選"繼續瀏覽"即可。

### Q: API 回應 404 錯誤
**A**: 檢查 `frontend/app.js` 中的 IP 地址是否正確設定。

## 📊 效能調整

### 資料庫優化

```bash
# 調整 PostgreSQL 設定
docker compose exec db psql -U user -d db -c "
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
SELECT pg_reload_conf();
"
```

### Docker 資源限制

在 `docker-compose.yml` 中調整容器資源：

```yaml
services:
  django-1:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

## 🔄 更新和維護

### 更新專案

```bash
git pull origin main
docker compose down
docker compose up -d --build
docker compose exec django-1 python manage.py migrate
```

### 備份資料

```bash
# 備份資料庫
docker compose exec db pg_dump -U user db > backup_$(date +%Y%m%d).sql

# 備份檔案
tar -czf backup_files_$(date +%Y%m%d).tar.gz osm_data/ certbot/
```

### 日誌管理

```bash
# 查看日誌
docker compose logs django-1
docker compose logs nginx

# 清理日誌
docker system prune -f
```

## 🚨 安全建議

### 生產環境設定

1. **更改預設密碼**: 
   ```bash
   export POSTGRES_PASSWORD=$(openssl rand -base64 32)
   ```

2. **生成新的 Django SECRET_KEY**:
   ```bash
   python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   ```

3. **關閉除錯模式**:
   ```bash
   export DJANGO_DEBUG=False
   ```

4. **設定防火牆**:
   ```bash
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```

### SSL 憑證

生產環境建議使用 Let's Encrypt 免費憑證：

```bash
# 安裝 certbot
sudo apt install certbot

# 取得憑證
sudo certbot certonly --standalone -d your-domain.com
```

## 📞 支援

如果安裝過程中遇到問題：

1. 查看 [常見問題](../README.md#常見問題)
2. 搜尋或建立 [Issue](https://github.com/your-username/taiwan-navigation-system/issues)
3. 參與 [Discussions](https://github.com/your-username/taiwan-navigation-system/discussions)