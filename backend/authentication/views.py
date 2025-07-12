from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer
from drf_spectacular.utils import extend_schema

@extend_schema(
    request=UserRegistrationSerializer,
    responses={201: UserProfileSerializer}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """使用者註冊API"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token = Token.objects.get(user=user)
        user_data = UserProfileSerializer(user).data
        return Response({
            'user': user_data,
            'token': token.key,
            'message': '註冊成功'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    request=UserLoginSerializer,
    responses={200: UserProfileSerializer}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """使用者登入API"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user_data = UserProfileSerializer(user).data
        return Response({
            'user': user_data,
            'token': token.key,
            'message': '登入成功'
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """使用者登出API"""
    try:
        # 刪除用戶的 token
        request.user.auth_token.delete()
        return Response({'message': '登出成功'}, status=status.HTTP_200_OK)
    except:
        return Response({'error': '登出失敗'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_view(request):
    """取得使用者資料API"""
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)
