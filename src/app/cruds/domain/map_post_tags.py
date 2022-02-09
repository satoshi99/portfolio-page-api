from sqlalchemy.orm import Session
from typing import List
from schemas import tag as tag_schema
from models import Post
from cruds.post import PostCrud
from cruds.tag import TagCrud


class MapPostAndTags:

    post_crud = PostCrud()
    tag_crud = TagCrud()

    def create_map(self, tags: List[tag_schema.TagCreate], db_post: Post, db: Session) -> Post:
        for tag in tags:
            db_tag = self.tag_crud.get_tag_by_title(tag.title, db)
            if db_tag:
                db_post.tags.append(db_tag)
            else:
                new_tag = self.tag_crud.create_tag(tag, db)
                db_post.tags.append(new_tag)

        db.commit()
        return db_post

    def delete_map(self, tags: List[tag_schema.TagUpdate], db_post: Post, db: Session) -> Post:
        for tag in tags:
            db_tag = self.tag_crud.get_tag_by_title(tag.title, db)
            db_post.tags.remove(db_tag)
        db.commit()
        return db_post

    def update_map(self, new_tags: List[tag_schema.TagCreate], db_post: Post, db: Session) -> Post:
        db_tags_title = [tag.title for tag in db_post.tags]  # The title list that has already added to map
        new_tags_title = [tag.title for tag in new_tags]  # The title list that want to create the new map of tags

        # tags that except have already added to map
        new_add_tags = [tag for tag in new_tags if tag.title not in db_tags_title]
        if new_add_tags:
            db_post = self.create_map(new_add_tags, db_post, db)

        # tags that have removed from existing map
        remove_tags = [tag for tag in db_post.tags if tag.title not in new_tags_title]
        if remove_tags:
            db_post = self.delete_map(remove_tags, db_post, db)

        return db_post
