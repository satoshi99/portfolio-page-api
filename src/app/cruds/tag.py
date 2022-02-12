from sqlalchemy.orm import Session
from typing import List, Union
from uuid import UUID
from models import Tag
from schemas import tag_schema
from .domain import update_process
from .domain.transformer import slug_transformer
from errors import ObjectNotFoundError, BadRequestError

from utils.logger import setup_logger
import datetime

log_folder = f"log/{datetime.date.today()}.log"
logger = setup_logger(log_folder=log_folder, modname=__name__)


class TagCrud:

    def get_tags(self, db: Session) -> List[Tag]:
        logger.info({
            "action": "get all tags",
            "status": "run"
        })

        tags = db.query(Tag).order_by(Tag.title).all()

        logger.info({
            "action": "get all tags",
            "status": "success"
        })

        return tags

    def get_tag(self, tag_id: UUID, db: Session) -> Tag:
        logger.info({
            "action": "get tag by id",
            "tag_id": tag_id,
            "status": "run"
        })

        db_tag = db.query(Tag).filter(Tag.id == tag_id).first()

        logger.info({
            "action": "get tag by id",
            "status": "success"
        })

        return db_tag

    def get_tag_by_title(self, tag_title: str, db: Session) -> Union[Tag, bool]:
        logger.info({
            "action": "get tag by title",
            "tag_id": tag_title,
            "status": "run"
        })

        db_tag = db.query(Tag).filter(Tag.title == tag_title).first()
        if not db_tag:
            return False

        logger.info({
            "action": "get tag by title",
            "status": "success"
        })

        return db_tag

    def create_tag(self, tag: tag_schema.TagCreate, db: Session) -> Tag:
        logger.info({
            "action": "create new tag object",
            "tag": f"{tag.title}, {tag.slug}",
            "status": "run"
        })
        if tag.slug is None:
            tag.slug = slug_transformer(tag.title)

        try:
            db_tag = Tag(title=tag.title, slug=tag.slug)
            db.add(db_tag)
            db.commit()
            db.refresh(db_tag)
        except Exception:
            logger.error("Failed insertion of new tag to db")
            db.rollback()
            raise BadRequestError(message="Failed insertion of new tag to db")

        logger.info({
            "action": "create new tag object",
            "status": "success"
        })
        return db_tag

    def update_tag(self, tag_id: UUID, new_tag: tag_schema.TagUpdate, db: Session) -> Tag:
        logger.info({
            "action": "Update tag object",
            "tag_id": tag_id,
            "new_tag": new_tag,
            "status": "run"
        })

        db_tag = self.get_tag(tag_id, db)
        if not db_tag:
            logger.error(f"Failed get tag by id: {tag_id} from db")
            raise ObjectNotFoundError(message="The Tag was not found by ID")

        try:
            db_tag = update_process(db_tag, new_tag)
            db.commit()
        except Exception as ex:
            logger.error(f"Failed update tag with title: {new_tag.title} and slug: {new_tag.slug}")
            db.rollback()
            raise ex

        logger.info({
            "action": "Update tag object",
            "status": "Success"
        })

        return db_tag

    def delete_tag(self, tag_id: UUID, db: Session) -> bool:
        logger.info({
            "action": "Delete tag object",
            "tag_id": tag_id,
            "status": "Run"
        })

        db_tag = self.get_tag(tag_id, db)
        if not db_tag:
            logger.error(f"Failed get tag by id: {tag_id} from db")
            raise ObjectNotFoundError(message="The Tag was not found by ID")

        try:
            db.delete(db_tag)
            db.commit()
        except Exception:
            logger.error("Delete tag object has failed")
            db.rollback()
            raise BadRequestError(message="Delete tag object has failed")

        if self.get_tag(tag_id, db):
            logger.warning("Delete process is done but the object has not deleted")
            return False

        logger.info({
            "action": "Delete tag object",
            "status": "Success"
        })

        return True
