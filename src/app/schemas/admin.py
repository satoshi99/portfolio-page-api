from pydantic import BaseModel, EmailStr, constr, validator
from typing import List, Optional
from uuid import UUID
from .post import Post


class AdminBase(BaseModel):
    email: EmailStr


class PasswordCreate(BaseModel):
    password: constr(min_length=7, max_length=100)
    password_confirm: str

    @validator("password_confirm")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("Password do not match")
        return v


class AdminCreate(PasswordCreate):
    email: EmailStr


class AdminUpdate(AdminBase):
    email: Optional[EmailStr]


class PasswordUpdate(PasswordCreate):
    current_password: str


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
