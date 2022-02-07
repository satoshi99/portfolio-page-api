from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Union
from uuid import UUID
from models import Tag
from schemas import tag as schema
import logging
from .domain.transformer import slug_transformer

logger = logging.getLogger(__name__)
log_file = logging.FileHandler("log/crud_tag.log")
logger.addHandler(log_file)


class TagCrud:

    @staticmethod
    def get_tags(db: Session) -> Union[List[Tag], bool]:
        logger.info({
            "action": "get all tags",
            "status": "run"
        })

        tags = db.query(Tag).all()
        if len(tags) == 0:
            logger.info({
                "action": "get all tags",
                "status": "Read objects but it's empty"
            })
            return False

        logger.info({
            "action": "get all tags",
            "status": "success"
        })

        return tags

    @staticmethod
    def get_tag(tag_id: UUID, db: Session) -> Union[Tag, bool]:
        logger.info({
            "action": "get tag by id",
            "tag_id": tag_id,
            "status": "run"
        })

        db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not db_tag:
            return False

        logger.info({
            "action": "get tag by id",
            "status": "success"
        })

        return db_tag

    @staticmethod
    def get_tag_by_title(tag_title: str, db: Session) -> Union[Tag, bool]:
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

    @staticmethod
    def create_tag(tag: schema.TagCreate, db: Session) -> Tag:
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
        except Exception as e:
            logger.error("Failed insertion of new tag to db")
            db.rollback()
            raise e

        logger.info({
            "action": "create new tag object",
            "status": "success"
        })
        return db_tag

    def update_tag(self, tag_id: UUID, new_tag: schema.TagUpdate, db: Session) -> Tag:
        logger.info({
            "action": "Update tag object",
            "tag_id": tag_id,
            "new_tag": new_tag,
            "status": "run"
        })

        db_tag = self.get_tag(tag_id, db)
        if not db_tag:
            logger.error(f"Failed get tag by id: {tag_id} from db")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag Not Found"
            )

        try:
            if new_tag.title:
                db_tag.title = new_tag.title
            if new_tag.slug:
                db_tag.slug = new_tag.slug
            db.commit()
        except Exception as e:
            logger.error(f"Failed update tag with title: {new_tag.title} and slug: {new_tag.slug}")
            db.rollback()
            raise e

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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag Not Found"
            )

        try:
            db.delete(db_tag)
            db.commit()
        except Exception as e:
            logger.error("Delete tag object has failed")
            db.rollback()
            raise e

        if self.get_tag(tag_id, db):
            logger.warning("Delete process is done but the object has not deleted")
            return False

        logger.info({
            "action": "Delete tag object",
            "status": "Success"
        })

        return True
