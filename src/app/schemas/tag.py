from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID


class TagBase(BaseModel):
    title: str
    slug: Optional[str]


class TagCreate(TagBase):
    pass


class TagUpdate(TagCreate):
    title: Optional[str]


class TagInDBBase(TagBase):
    id: UUID

    class Config:
        orm_mode = True


class Tag(TagInDBBase):
    pass


class TagInDB(TagInDBBase):
    pass
