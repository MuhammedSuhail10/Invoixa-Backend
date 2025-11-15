from ninja.security import HttpBearer
from user.models import *
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class AsyncJWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            if user_id and User.objects.filter(id=user_id).exists():
                user = User.objects.get(id=user_id)
                return user 
            return None
        except jwt.ExpiredSignatureError:
            return None
        except Exception as e:
            return None