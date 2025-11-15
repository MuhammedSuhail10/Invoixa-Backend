from ninja import Router, PatchDict, UploadedFile, File
from django.contrib.auth import get_user_model
from .schema import *
from typing import *
from .models import *
from ninja_jwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Q
from ninja.responses import codes_4xx
from asgiref.sync import sync_to_async
from ninja_jwt.tokens import RefreshToken, AccessToken
from django.contrib.auth.hashers import check_password
import random
from django.core.cache import cache

User = get_user_model()
user_api = Router(tags=["User"])

@user_api.post("/create-user", response={201: Message, 401: Message}, auth=None)
async def create_user(request, data: UserCreateSchema):
    if await User.objects.filter(Q(username=data.username) | Q(username=data.phone_number)).aexists():
        return 401, {"message": "User with this phone number already exists"}
    user = await sync_to_async(User.objects.create_user)(**data.dict())
    return 201, {"message": "User created successfully", "user_id": user.id}

@user_api.post("/login", response={200: TokenSchema, 401: Message}, auth=None)
async def login(request, data: LoginSchema):
    user = await sync_to_async(authenticate)(username=data.username, password=data.password)
    if not user:
        return 401, {"message": "Invalid username or password"}
    access_token = AccessToken.for_user(user)
    refresh_token = RefreshToken.for_user(user)
    return 200, {
        "access": str(access_token),
        "refresh": str(refresh_token),
        "name": user.name,
    }

@user_api.post("/refresh-token", response={200: TokenSchema, 401: Message}, auth=None)
async def refresh_token(request, data: TokenRefreshSchema):
    try:
        # refresh_token = RefreshToken(data.refresh)
        access_token = AccessToken.for_user(refresh_token.user)
        return 200, {
            "access": str(access_token),
            "refresh": str(refresh_token),
            "name": refresh_token.user.name,
        }
    except Exception as e:
        return 401, {"message": "Invalid refresh token"}