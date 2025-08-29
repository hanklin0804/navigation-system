#!/bin/bash
set -e

echo "🧪 開始執行測試..."

# 快速測試 (Models + Serializers)
echo "📦 執行 Model 測試..."
docker exec django-1 python manage.py test geouser.tests.UserLocationModelTest chat.tests.MessageModelTest --verbosity=2 --settings=test_settings

echo "🔄 執行 Serializer 測試..."
docker exec django-1 python manage.py test geouser.tests.UserLocationSerializerTest --verbosity=2 --settings=test_settings

# 完整測試 (包含 Views)
echo "🌐 執行 View 測試..."
docker exec django-1 python manage.py test geouser.tests.UserLocationViewTest --verbosity=2 --settings=test_settings

# WebSocket 測試
echo "💬 執行 WebSocket 測試..."
docker exec django-1 python manage.py test chat.tests.ChatConsumerTest --verbosity=2 --settings=test_settings

# 整合測試
echo "🔗 執行整合測試..."
docker exec django-1 python manage.py test tests.test_integration --verbosity=2 --settings=test_settings

echo "✅ 所有測試完成！"