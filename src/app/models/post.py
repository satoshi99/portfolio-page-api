from uuid import uuid4
from sqlalchemy import Column, String, Boolean, ForeignKey, Table
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType

from .mixins import TimestampMixin
from database import Base


tag_post_map_table = Table(
    "tag_post_map",
    Base.metadata,
    Column("tag_id", UUIDType(binary=False), ForeignKey("tags.id")),
    Column("post_id", UUIDType(binary=False), ForeignKey("posts.id"))
)


class Tag(Base, TimestampMixin):
    __tablename__ = "tags"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid4)
    title = Column(String(50), nullable=False, unique=True)
    slug = Column(String(50), nullable=True, unique=True)
    posts = relationship("Post", secondary=tag_post_map_table, back_populates="tags")


class Post(Base, TimestampMixin):
    __tablename__ = "posts"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid4)
    title = Column(String(200), nullable=False)
    url_slug = Column(String(200), nullable=True, unique=True)
    thumbnail = Column(String(200), nullable=True)
    description = Column(MEDIUMTEXT, nullable=True)
    content = Column(MEDIUMTEXT, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    author_id = Column(UUIDType(binary=False), ForeignKey("admins.id", ondelete="CASCADE"), nullable=True)
    tags = relationship("Tag", secondary=tag_post_map_table, back_populates="posts")
