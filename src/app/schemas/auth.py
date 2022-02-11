from pydantic import BaseModel
from typing import Union, Optional
from uuid import UUID
from utils.env import CSRF_SECRET_KEY


class CsrfSettings(BaseModel):
    secret_key: str = CSRF_SECRET_KEY


class Csrf(BaseModel):
    csrf_token: Union[str, None]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[UUID] = None



