from typing import List
from uuid import UUID

from sqlalchemy import desc
from sqlalchemy.orm import Session

from models import Post
from schemas import post_schema
from .domain import update_process
from .domain.transformer import slug_transformer
from utils.logger import setup_logger
import datetime

log_folder = f"log/{datetime.date.today()}.log"
logger = setup_logger(log_folder=log_folder, modname=__name__)


class PostCrud:

    def get_my_posts(self, admin_id: UUID, db: Session) -> List[Post]:
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

    def get_public_posts(self, db: Session) -> List[Post]:
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

    def get_post(self, post_id: UUID, db: Session) -> Post:
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

    def create_post(self, admin_id: UUID, data: post_schema.PostCreate, db: Session) -> Post:
        if not data.url_slug:
            data = data.copy()
            data.url_slug = slug_transformer(data.title)

        new_post = Post(**data.dict(), author_id=admin_id)
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post

    def update_post(self, db_post: Post, new_post: post_schema.PostUpdate, db: Session) -> Post:
        logger.info({
            "action": "Update post",
            "data": new_post.is_public,
            "status": "Run"
        })
        try:
            db_post = update_process(db_post, new_post)
            db.commit()

        except Exception as e:
            raise e

        return db_post

    def delete_post(self, db_post: Post, db: Session):
        try:
            db.delete(db_post)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
