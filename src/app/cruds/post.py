from fastapi import HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from typing import List
from uuid import UUID

from models import Post
from schemas import post as post_schema
from schemas import tag as tag_schema
from cruds.tag import TagCrud

from utils.logger import setup_logger
import datetime

log_folder = f"log/{datetime.date.today()}.log"
logger = setup_logger(log_folder=log_folder, modname=__name__)


tag_crud = TagCrud()


class PostCrud:

    @staticmethod
    def get_my_posts(admin_id: UUID, db: Session) -> List[Post]:
        logger.info({
            "action": "Get my posts",
            "admin_id": admin_id,
            "status": "Run"
        })

        try:
            posts = db.query(Post)\
                .filter(Post.author_id == admin_id)\
                .order_by(desc(Post.updated_at))\
                .all()
        except Exception as ex:
            logger.error(f"Failed get my (id: {admin_id}) posts from db")
            raise ex

        logger.info({
            "action": "Get my posts",
            "status": "Success"
        })

        if not posts:
            logger.warning("My post list is empty")

        return posts

    @staticmethod
    def get_public_posts(db: Session) -> List[Post]:
        logger.info({
            "action": "Get public posts",
            "status": "Run"
        })

        try:
            posts = db.query(Post)\
                .filter(Post.is_public.is_(True))\
                .order_by(desc(Post.updated_at))\
                .all()
        except Exception as ex:
            logger.error("Failed get public posts from db")
            raise ex

        logger.info({
            "action": "Get public posts",
            "status": "Success"
        })

        if not posts:
            logger.warning("Public post list is empty")

        return posts

    @staticmethod
    def get_post(post_id: UUID, db: Session) -> Post:
        logger.info({
            "action": "Get post by id",
            "post_id": post_id,
            "status": "Run"
        })

        try:
            post = db.query(Post).filter(Post.id == post_id).first()
        except Exception as ex:
            logger.error("Failed get post by id from db")
            raise ex

        logger.info({
            "action": "Get post by id",
            "status": "Success"
        })

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
        logger.info({
            "action": "Update post",
            "data": data.is_public,
            "status": "Run"
        })
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
            if data.is_public is not None:
                logger.info({"action": "update is_public", "data": data.is_public})
                db_post.is_public = data.is_public
                logger.info({"action": "update is_public", "updated_data": db_post.is_public})

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

