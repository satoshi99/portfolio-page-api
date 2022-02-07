from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Union
from schemas import tag as tag_schema
from schemas.common import ResponseMsg
from cruds.tag import TagCrud
from database import get_db

router = APIRouter(prefix="/tags")
crud = TagCrud()


@router.get("", responses=status.HTTP_200_OK, response_model=Union[List[tag_schema.Tag], ResponseMsg])
async def get_tags(db: Session = Depends(get_db)):
    tags = crud.get_tags(db)
    if not tags:
        return {"message": "No registered tags"}

    return tags


@router.get("/{tag_id}", responses=status.HTTP_200_OK, response_model=tag_schema.Tag)
async def get_tag(tag_id: UUID, db: Session = Depends(get_db)):
    tag = crud.get_tag(tag_id, db)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    return tag


@router.post("/create", responses=status.HTTP_201_CREATED, response_model=tag_schema.Tag)
async def create_tag(new_tag: tag_schema.TagCreate, db: Session = Depends(get_db)):
    return crud.create_tag(new_tag, db)


@router.put("/{tag_id}", responses=status.HTTP_201_CREATED, response_model=tag_schema.Tag)
async def update_post(tag_id: UUID, new_tag: tag_schema.TagUpdate, db: Session = Depends(get_db)):
    return crud.update_tag(tag_id, new_tag, db)


@router.delete("{tag_id}", responses=status.HTTP_200_OK, response_model=ResponseMsg)
async def delete_post(tag_id: UUID, db: Session = Depends(get_db)):
    result = crud.delete_tag(tag_id, db)
    if result:
        return {"message": "Successfully Tag Deleted"}
    else:
        return {"message": "Failed delete tag object"}
