from uuid import UUID
from sqlalchemy.orm import Session
from typing import List
from schemas import tag as tag_schema
from models import Post
from cruds.post import PostCrud
from cruds.tag import TagCrud

from exceptions import ObjectNotFoundError


class MapPostAndTags:

    post_crud = PostCrud()
    tag_crud = TagCrud()

    def create_map(self, tag_ids: List[UUID], db_post: Post, db: Session) -> Post:
        for tag_id in tag_ids:
            db_tag = self.tag_crud.get_tag(tag_id, db)
            if not db_tag:
                raise ObjectNotFoundError(output_message="The tag was not found by ID")

            db_post.tags.append(db_tag)

        db.commit()
        return db_post

    def delete_map(self, tags: List[tag_schema.TagUpdate], db_post: Post, db: Session) -> Post:
        for tag in tags:
            db_tag = self.tag_crud.get_tag_by_title(tag.title, db)
            db_post.tags.remove(db_tag)
        db.commit()
        return db_post

    def update_map(self, input_tag_ids: List[UUID], db_post: Post, db: Session) -> Post:
        db_tag_id_list = [tag.id for tag in db_post.tags]  # The title list that has already added to map
        input_tag_id_list = [tag_id for tag_id in input_tag_ids]  # The title list that want to create the new map of tags

        # tags that except have already added to map
        new_tag_id_list = [tag_id for tag_id in input_tag_id_list if tag_id not in db_tag_id_list]
        if new_tag_id_list:
            db_post = self.create_map(new_tag_id_list, db_post, db)

        # tags that have removed from existing map
        remove_tags = [tag for tag in db_post.tags if tag.id not in input_tag_id_list]
        if remove_tags:
            db_post = self.delete_map(remove_tags, db_post, db)

        return db_post
