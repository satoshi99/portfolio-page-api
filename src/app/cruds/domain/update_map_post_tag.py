from sqlalchemy.orm import Session
from typing import List
from schemas import tag as tag_schema
from models import Post
from cruds.post import PostCrud

post_crud = PostCrud()


def update_map_post_and_tags(
        new_tags: List[tag_schema.TagCreate],
        db_post: Post, db: Session
) -> Post:
    db_tags_title = [tag.title for tag in db_post.tags]  # The title list that has already added to map
    new_tags_title = [tag.title for tag in new_tags]  # The title list that want to create the new map of tags

    # tags that except have already added to map
    new_add_tags = [tag for tag in new_tags if tag.title not in db_tags_title]
    if new_add_tags:
        db_post = post_crud.create_map_post_and_tags(new_add_tags, db_post, db)

    # tags that have removed from existing map
    remove_tags = [tag for tag in db_post.tags if tag.title not in new_tags_title]
    if remove_tags:
        db_post = post_crud.delete_map_post_and_tags(remove_tags, db_post, db)

    return db_post
