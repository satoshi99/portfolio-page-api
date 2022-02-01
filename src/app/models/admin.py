from uuid import uuid4

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType

from database import Base
from .mixins import TimestampMixin


class Admin(Base, TimestampMixin):
    __tablename__ = "admins"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid4)
    email = Column(String(100), nullable=False, unique=True)
    hashed_password = Column(String(100), nullable=False, unique=True)
    posts = relationship("Post", backref="admin")
