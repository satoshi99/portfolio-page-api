from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi_csrf_protect import CsrfProtect
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Union
from schemas import tag as tag_schema
from schemas import admin as admin_schema
from schemas import post as post_schema
from schemas.common import ResponseMsg
from cruds.tag import TagCrud
from database import get_db
from .admin import get_current_admin
from auth import AuthJwtCsrf

router = APIRouter(prefix="/tags")
crud = TagCrud()
auth = AuthJwtCsrf()


@router.get("", status_code=status.HTTP_200_OK, response_model=Union[List[tag_schema.Tag], ResponseMsg])
async def get_tags(db: Session = Depends(get_db)):
    tags = crud.get_tags(db)
    if not tags:
        return {"message": "No registered tags"}

    return tags


@router.get("/{tag_id}", status_code=status.HTTP_200_OK, response_model=post_schema.TagWithPosts)
async def get_tag_with_posts(tag_id: UUID, db: Session = Depends(get_db)):
    tag = crud.get_tag(tag_id, db)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    return tag


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=tag_schema.Tag)
async def create_tag(
        new_tag: tag_schema.TagCreate,
        request: Request,
        csrf_protect: CsrfProtect = Depends(),
        current_admin: admin_schema.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    auth.verify_csrf(request, csrf_protect)
    return crud.create_tag(new_tag, db)


@router.put("/{tag_id}", status_code=status.HTTP_200_OK, response_model=tag_schema.Tag)
async def update_post(
        tag_id: UUID,
        new_tag: tag_schema.TagUpdate,
        request: Request,
        csrf_protect: CsrfProtect = Depends(),
        current_admin: admin_schema.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    auth.verify_csrf(request, csrf_protect)
    return crud.update_tag(tag_id, new_tag, db)


@router.delete("{tag_id}", status_code=status.HTTP_200_OK, response_model=ResponseMsg)
async def delete_post(
        tag_id: UUID,
        request: Request,
        csrf_protect: CsrfProtect = Depends(),
        current_admin: admin_schema.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    auth.verify_csrf(request, csrf_protect)
    result = crud.delete_tag(tag_id, db)
    if result:
        return {"message": "Successfully Tag Deleted"}
    else:
        return {"message": "Failed delete tag object"}
