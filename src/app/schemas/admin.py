from pydantic import BaseModel, EmailStr, constr
from typing import List
from uuid import UUID
from .post import Post


class AdminBase(BaseModel):
    email: EmailStr


class AdminCreate(AdminBase):
    password: constr(min_length=7, max_length=50)


class AdminUpdate(AdminBase):
    pass


class AdminPasswordHash(BaseModel):
    hashed_password: str
    salt: str


class AdminInDBBase(AdminBase):
    id: UUID
    email_verified: bool = False
    is_active: bool = True
    is_superuser: bool = False

    class Config:
        orm_mode = True


class Admin(AdminInDBBase):
    posts: List[Post]


class AdminInDB(AdminInDBBase):
    hashed_password: str
    salt: str

