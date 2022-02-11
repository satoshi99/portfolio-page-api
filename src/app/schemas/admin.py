from pydantic import BaseModel, EmailStr, constr
from typing import List
from uuid import UUID
from .post import Post


class AdminBase(BaseModel):
    email: EmailStr


class AdminCreate(AdminBase):
    password: constr(min_length=7, max_length=100)


class AdminUpdate(AdminBase):
    email_verified: bool = False
    is_active: bool = False


class PasswordUpdate(BaseModel):
    current_password: str
    new_password: constr(min_length=7, max_length=100)


class AdminInDBBase(AdminBase):
    id: UUID
    email_verified: bool = False
    is_active: bool = False

    class Config:
        orm_mode = True


class Admin(AdminInDBBase):
    pass


class AdminWithPosts(AdminInDBBase):
    posts: List[Post]


class AdminInDB(AdminInDBBase):
    hashed_password: str
