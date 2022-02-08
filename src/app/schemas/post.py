from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from .tag import Tag


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
    created_at: datetime
    updated_at: datetime
    tags: Optional[List[Tag]]


class PostPublic(Post):
    is_public: bool = True


class PostInDB(PostInDBBase):
    pass


class TagWithPosts(Tag):
    posts: Optional[List[Post]]
