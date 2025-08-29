#!/bin/bash
set -e

echo "🔍 執行覆蓋率檢查..."

# 檢查並安裝 coverage
echo "📦 檢查 coverage 套件..."
docker exec django-1 pip list | grep coverage || docker exec django-1 pip install coverage

# 執行覆蓋率分析
echo "🧪 執行測試並收集覆蓋率資料..."
docker exec django-1 coverage run --source='.' manage.py test geouser chat tests --settings=test_settings

# 生成報告
echo "📊 生成覆蓋率報告..."
docker exec django-1 coverage report

# 生成詳細報告
echo "📋 生成詳細報告..."
docker exec django-1 coverage report --show-missing

# 生成 HTML 報告
echo "🌐 生成 HTML 報告..."
docker exec django-1 coverage html

# 複製 HTML 報告到本地
echo "📁 複製 HTML 報告到本地..."
docker cp django-1:/app/htmlcov ./htmlcov

echo "✅ 覆蓋率檢查完成！"
echo "💡 本地 HTML 報告位置: htmlcov/index.html"
echo "🌐 開啟方式: 在瀏覽器中打開 file:///path/to/navigation-system/htmlcov/index.html"