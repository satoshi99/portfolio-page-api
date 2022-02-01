from uuid import uuid4
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType

from .mixins import TimestampMixin
from database import Base


class TagPostMapTable(Base):
    __tablename__ = "tag_post_map"

    tag_id = Column(UUIDType(binary=False), ForeignKey("tags.id"), primary_key=True)
    post_id = Column(UUIDType(binary=False), ForeignKey("posts.id"), primary_key=True)


class Tag(Base, TimestampMixin):
    __tablename__ = "tags"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid4)
    title = Column(String(50), nullable=False, unique=True)
    slug = Column(String(50), nullable=True, unique=True)
    posts = relationship("Post", secondary=TagPostMapTable, back_populates="tag")


class Post(Base, TimestampMixin):
    __tablename__ = "posts"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid4)
    title = Column(String(100), nullable=False)
    thumbnail = Column(String(200), nullable=True)
    description = Column(MEDIUMTEXT, nullable=True)
    content = Column(MEDIUMTEXT, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    author_id = Column(UUIDType(binary=False), ForeignKey("admins.id", ondelete="CASCADE"), nullable=True)
    tags = relationship("Tag", secondary=TagPostMapTable, back_populates="post")
