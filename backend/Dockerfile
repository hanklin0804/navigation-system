# backend/Dockerfile
FROM python:3.10-slim

# 安裝 GeoDjango 相關的系統套件：GDAL、GEOS、PROJ 等
RUN apt-get update && apt-get install -y \
    binutils gdal-bin libproj-dev libgeos-dev \ 
    && rm -rf /var/lib/apt/lists/*  # 安裝完成後清除快取

# 設定工作目錄
WORKDIR /app

# 複製需求檔並安裝 Python 相依套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製 Django 專案程式碼
COPY . .

# 對外暴露應用埠號（例如 8000）
EXPOSE 8000

# 啟動指令：使用 Daphne 作為 ASGI 伺服器，以支援 WebSocket（Channels）
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "taxi_backend.asgi:application"]
