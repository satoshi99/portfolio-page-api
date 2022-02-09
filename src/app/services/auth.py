from datetime import datetime, timedelta
import uuid
from uuid import UUID

from fastapi import HTTPException, status, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi_csrf_protect import CsrfProtect

import bcrypt
from jose import JWTError, jwt
from passlib.context import CryptContext

from schemas import admin_schema
from env import JWT_SECRET_KEY, JWT_EXPIRE_MINUTES, JWT_NOT_BEFORE_SECONDS, ALGORITHM, SECRET_SALT


class AuthService:

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_csrf(self, request: Request, csrf_protect: CsrfProtect) -> None:
        csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
        csrf_protect.validate_csrf(csrf_token)

    def verify_password(self, plain_password: str, salt: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password + salt + SECRET_SALT, hashed_password)

    def get_password_hash(self, password: str, salt: str) -> str:
        return self.pwd_context.hash(password + salt + SECRET_SALT)

    def create_salt_and_hashed_password(self, password: str) -> admin_schema.AdminPasswordHash:
        salt = bcrypt.gensalt().decode()
        hashed_password = self.get_password_hash(password, salt)
        return admin_schema.AdminPasswordHash(hashed_password=hashed_password, salt=salt)

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        to_encode.update({
            "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES),
            "nbf": datetime.utcnow() - timedelta(seconds=JWT_NOT_BEFORE_SECONDS),
            "iat": datetime.utcnow(),
            "jti": str(uuid.uuid4()),
            "iss": "not-todo-app.com",
        })
        return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

    def decode_jwt(self, token: str) -> UUID:
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=ALGORITHM)
            user_id: UUID = payload.get("sub")
            return user_id
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="The JWT has expired"
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

    def update_jwt(self, admin_id: UUID, response: Response) -> None:
        try:
            new_token = self.create_access_token({"sub": jsonable_encoder(admin_id)})
            response.set_cookie(
                key="access_token", value=f"Bearer {new_token}", httponly=True
            )
        except Exception as ex:
            raise ex
