from datetime import datetime, timedelta
import uuid
from uuid import UUID
from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi_csrf_protect import CsrfProtect

from cruds.admin import AdminCrud
from env import CSRF_SECRET_KEY, JWT_SECRET_KEY, JWT_EXPIRE_MINUTES, JWT_NOT_BEFORE_SECONDS, ALGORITHM


class AuthJwtCsrf:
    admin_crud = AdminCrud()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password) -> str:
        return self.pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict) -> str:
        to_encode = data.copy()
        to_encode.update({
            "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES),
            "nbf": datetime.utcnow() - timedelta(seconds=JWT_NOT_BEFORE_SECONDS),
            "iat": datetime.utcnow(),
            "jti": str(uuid.uuid4()),
            "iss": "not-todo-app.com",
        })
        return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def decode_jwt(token: str) -> UUID:
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

    # def verify_and_update_jwt(self, token: str) -> Union[str, bool]:
    #     admin_id = self.decode_jwt(token)
    #     db_admin = self.admin_crud.get_admin(admin_id)
    #     if not db_admin:
    #         return False
    #
    #     return self.create_access_token({"sub": db_admin.id})

