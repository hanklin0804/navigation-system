from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

class UserRegistrationSerializer(serializers.ModelSerializer):
    """使用者註冊序列化器"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("密碼確認不一致")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        # 建立對應的 Token
        Token.objects.create(user=user)
        return user

class UserLoginSerializer(serializers.Serializer):
    """使用者登入序列化器"""
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('使用者名稱或密碼錯誤')
            if not user.is_active:
                raise serializers.ValidationError('使用者帳號已停用')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('請提供使用者名稱和密碼')

class UserProfileSerializer(serializers.ModelSerializer):
    """使用者資料序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'last_login']
        read_only_fields = ['id', 'date_joined', 'last_login']
