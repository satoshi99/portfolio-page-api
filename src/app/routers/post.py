from fastapi import APIRouter, status, HTTPException, Depends, Request, Response
from fastapi_csrf_protect import CsrfProtect
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from database import get_db
from schemas import post as post_schema
from schemas import tag as tag_schema
from schemas import admin as admin_schema
from schemas.common import ResponseMsg
from cruds.post import PostCrud
from .admin import get_current_admin
from cruds.domain.update_map_post_tag import update_map_post_and_tags
from cruds.domain.transformer import slug_transformer
from auth import AuthJwtCsrf

router = APIRouter(prefix="/posts")
crud = PostCrud()
auth = AuthJwtCsrf()


@router.get("", status_code=status.HTTP_200_OK, response_model=List[post_schema.Post])
async def get_my_posts(
        response: Response,
        current_admin: admin_schema.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    auth.update_jwt(current_admin.id, response)
    return crud.get_my_posts(current_admin.id, db)


@router.get("/public", status_code=status.HTTP_200_OK, response_model=List[post_schema.PostPublic])
async def get_public_posts(db: Session = Depends(get_db)):
    posts = crud.get_public_posts(db)
    return posts


@router.get("/{post_id}", status_code=status.HTTP_200_OK, response_model=post_schema.Post)
async def get_post(post_id: UUID, db: Session = Depends(get_db)):
    post = crud.get_post(post_id, db)
    return post


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=post_schema.Post)
async def create_post(
        data: post_schema.PostCreate,
        tags: List[tag_schema.TagCreate],
        request: Request,
        response: Response,
        csrf_protect: CsrfProtect = Depends(),
        current_admin: admin_schema.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    auth.verify_csrf(request, csrf_protect)
    auth.update_jwt(current_admin.id, response)
    if not data.url_slug:
        data = data.copy()
        data.url_slug = slug_transformer(data.title)
    db_post = crud.create_post(current_admin.id, data, db)
    if tags:
        db_post = crud.create_map_post_and_tags(tags, db_post, db)
    return db_post


@router.put("/{post_id}", status_code=status.HTTP_200_OK, response_model=post_schema.Post)
async def update_post(
        post_id: UUID,
        data: post_schema.PostUpdate,
        tags: List[tag_schema.TagCreate],
        request: Request,
        response: Response,
        csrf_protect: CsrfProtect = Depends(),
        current_admin: admin_schema.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    auth.verify_csrf(request, csrf_protect)
    auth.update_jwt(current_admin.id, response)
    posts = current_admin.posts
    db_post = [post for post in posts if post.id == post_id]
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    db_post = crud.update_post(db_post[0], data, db)

    if tags and not db_post.tags:
        db_post = crud.create_map_post_and_tags(tags, db_post, db)
    elif tags:
        db_post = update_map_post_and_tags(tags, db_post, db)
    return db_post


@router.delete("{post_id}", status_code=status.HTTP_200_OK, response_model=ResponseMsg)
async def delete_post(
        post_id: UUID,
        request: Request,
        response: Response,
        csrf_protect: CsrfProtect = Depends(),
        current_admin: admin_schema.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    auth.verify_csrf(request, csrf_protect)
    auth.update_jwt(current_admin.id, response)
    posts = current_admin.posts
    db_post = [post for post in posts if post.id == post_id]
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    crud.delete_post(db_post[0], db)

    if not crud.get_post(post_id, db):
        return {"message": "Successfully Post Deleted"}
    else:
        return {"message": "Failed delete"}
