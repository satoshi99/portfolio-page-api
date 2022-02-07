from sqlalchemy.orm import Session

from typing import List
from uuid import UUID

from models import Post
from schemas import post as post_schema
from schemas import tag as tag_schema
from cruds.tag import TagCrud

tag_crud = TagCrud()


class PostCrud:

    @staticmethod
    def get_posts(db: Session) -> List[Post]:
        posts = db.query(Post).all()
        return posts

    @staticmethod
    def get_post(post_id: UUID, db: Session) -> Post:
        post = db.query(Post).filter(Post.id == post_id).first()
        return post

    @staticmethod
    def create_post(admin_id: UUID, data: post_schema.PostCreate, db: Session) -> Post:
        new_post = Post(**data.dict(), author_id=admin_id)
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post

    @staticmethod
    def update_post(db_post: Post, data: post_schema.PostUpdate, db: Session) -> Post:

        try:
            if data.title:
                db_post.title = data.title
            if data.url_slug:
                db_post.url_slug = data.url_slug
            if data.thumbnail:
                db_post.thumbnail = data.thumbnail
            if data.description:
                db_post.description = data.description
            if data.content:
                db_post.content = data.content
            if data.is_public:
                db_post.is_public = data.is_public

            db.commit()

        except Exception as e:
            raise e

        return db_post

    @staticmethod
    def delete_post(db_post: Post, db: Session):
        try:
            db.delete(db_post)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def create_map_post_and_tags(tags: List[tag_schema.TagCreate], db_post: Post, db: Session) -> Post:
        for tag in tags:
            db_tag = tag_crud.get_tag_by_title(tag.title, db)
            if db_tag:
                db_post.tags.append(db_tag)
            else:
                new_tag = tag_crud.create_tag(tag, db)
                db_post.tags.append(new_tag)

        db.commit()
        return db_post

    @staticmethod
    def delete_map_post_and_tags(tags: List[tag_schema.TagUpdate], db_post: Post, db: Session):
        for tag in tags:
            db_tag = tag_crud.get_tag_by_title(tag.title, db)
            db_post.tags.remove(db_tag)
        db.commit()
        return db_post

