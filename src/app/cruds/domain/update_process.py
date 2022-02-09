from schemas.post import PostUpdate
from schemas.tag import TagUpdate
from schemas.admin import AdminUpdate
from models import Post, Tag, Admin
from utils.logger import setup_logger
import datetime

log_folder = f"log/{datetime.date.today()}.log"
logger = setup_logger(log_folder=log_folder, modname=__name__)


class UpdateProcess:

    def update_post(self, db_post: Post, new_post: PostUpdate) -> Post:
        if new_post.title:
            db_post.title = new_post.title
        if new_post.url_slug:
            db_post.url_slug = new_post.url_slug
        if new_post.thumbnail:
            db_post.thumbnail = new_post.thumbnail
        if new_post.description:
            db_post.description = new_post.description
        if new_post.content:
            db_post.content = new_post.content
        if new_post.is_public is not None:
            logger.info({"action": "update is_public", "data": new_post.is_public})
            db_post.is_public = new_post.is_public
            logger.info({"action": "update is_public", "updated_data": db_post.is_public})

        return db_post

    def update_tag(self, db_tag: Tag, new_tag: TagUpdate) -> Tag:
        if new_tag.title:
            db_tag.title = new_tag.title
        if new_tag.slug:
            db_tag.slug = new_tag.slug

        return db_tag

    def update_admin(self, db_admin: Admin, new_admin: AdminUpdate) -> Admin:
        if new_admin.email:
            db_admin.email = new_admin.email
        return db_admin
