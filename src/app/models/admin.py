from uuid import uuid4

from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType

from database import Base
from .mixins import TimestampMixin


class Admin(Base, TimestampMixin):
    __tablename__ = "admins"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid4)
    email = Column(String(255), nullable=False, unique=True)
    email_verified = Column(Boolean, nullable=False, default=False)
    salt = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, default=True)
    posts = relationship("Post", backref="admin")
