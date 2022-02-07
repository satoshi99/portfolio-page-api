from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

from .tag import Tag, TagCreate


class PostBase(BaseModel):
    title: str
    url_slug: Optional[str]
    thumbnail: Optional[str]
    description: Optional[str]
    content: str
    is_public: bool = False


class PostCreate(PostBase):
    pass


class PostUpdate(PostCreate):
    title: Optional[str]
    content: Optional[str]
    is_public: Optional[bool]


class PostInDBBase(PostBase):
    id: UUID

    class Config:
        orm_mode = True


class Post(PostInDBBase):
    tags: Optional[List[Tag]]


class PostInDB(PostInDBBase):
    pass
