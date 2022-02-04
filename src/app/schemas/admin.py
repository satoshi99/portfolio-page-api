from pydantic import BaseModel
from uuid import UUID


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
    pass


class AdminInDB(AdminInDBBase):
    hashed_password: str

