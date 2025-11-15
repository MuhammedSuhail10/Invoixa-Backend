from ninja import Schema, ModelSchema
from typing import *

class Message(Schema):
    message: str

class TokenSchema(Schema):
    access: str
    refresh: str
    name: str

class TokenRefreshSchema(Schema):
    refresh: str

class UserCreateSchema(Schema):
    username: str
    password: str
    name: str
    phone_number: str
    email: Optional[str] = None

class LoginSchema(Schema):
    username: str
    password: str