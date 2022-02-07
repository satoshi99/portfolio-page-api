from pydantic import BaseModel
from typing import List, Dict
from uuid import UUID
from .post import Post


class AdminBase(BaseModel):
    email: str


class AdminCreate(AdminBase):
    password: str


class AdminUpdate(AdminBase):
    pass


class AdminInDBBase(AdminBase):
    id: UUID

    class Config:
        orm_mode = True


class Admin(AdminInDBBase):
    posts: List[Post]


class AdminInDB(AdminInDBBase):
    hashed_password: str

