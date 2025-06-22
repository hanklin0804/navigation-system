#!/bin/bash
set -e

# ============ 設定變數 ============
PBF_URL="https://download.geofabrik.de/asia/taiwan-latest.osm.pbf"
PBF_FILE="osm_data/taiwan.pbf"
OSRM_DIR="osm_data/osrm_files"
OSRM_DATA="${OSRM_DIR}/taiwan.osrm.properties"
ENV_FILE=".env"
ENV_SAMPLE=".env.sample"
IMPORT_DONE=".import_done"  # 標記檔案，代表 tile-server 已經 import 過

echo "🚦 啟動導航系統建置腳本..."

# ============ 建立 .env ============
if [ ! -f "$ENV_FILE" ]; then
  echo "📁 建立 .env 檔案..."
  cp "$ENV_SAMPLE" "$ENV_FILE"
fi

# ============ 下載台灣 PBF ============
if [ ! -f "$PBF_FILE" ]; then
  echo "🌏 下載台灣地圖資料..."
  mkdir -p osm_data
  curl -L -o "$PBF_FILE" "$PBF_URL"
fi

# ============ OSRM 預處理 ============
if [ ! -f "$OSRM_DATA" ]; then
  echo "🧠 處理 OSRM 檔案..."
  mkdir -p "$OSRM_DIR"
  mv "$PBF_FILE" "$OSRM_DIR/"

  docker run --rm -v ${PWD}/${OSRM_DIR}:/data osrm/osrm-backend \
    osrm-extract -p /opt/car.lua /data/taiwan.pbf

  docker run --rm -v ${PWD}/${OSRM_DIR}:/data osrm/osrm-backend \
    osrm-partition /data/taiwan.osrm

  docker run --rm -v ${PWD}/${OSRM_DIR}:/data osrm/osrm-backend \
    osrm-customize /data/taiwan.osrm

  mv "${OSRM_DIR}/taiwan.pbf" "$PBF_FILE"
fi

# ============ tile server Import/Run ============
if [ ! -f "$IMPORT_DONE" ]; then
  echo "🗺️ Tile server 首次 import..."

  docker run --rm \
    -v osm-tile-data:/data/database \
    -v $PWD/osm_data/taiwan.pbf:/data/region.osm.pbf:ro \
    overv/openstreetmap-tile-server import

  # 標記已完成 import
  echo "✅" > "$IMPORT_DONE"

  echo "🚀 Import 完成，現在用 run 模式啟動 tile-server..."
  docker compose up -d tile-server --command "run"
else
  echo "🚀 Tile server 使用 run 模式啟動..."
  docker compose up -d tile-server --command "run"
fi


# ============ 啟動其他服務 ============
echo "🧱 啟動其他 docker-compose 服務..."
docker compose up -d --build --scale django=3
