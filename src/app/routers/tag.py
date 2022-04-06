from uuid import UUID
from typing import List, Union

from fastapi import APIRouter, Depends, status, Request, Response
from fastapi_csrf_protect import CsrfProtect

from sqlalchemy.orm import Session

from schemas import tag_schema, admin_schema, post_schema, ResponseMsg
from cruds import tag_crud
from database import get_db
from services import auth_service
from .admin import get_current_active_admin

from exceptions import error_responses, ObjectNotFoundError, AlreadyRegisteredError, jwt_errors_list, \
    ValidationError, csrf_errors_list

router = APIRouter(prefix="/tags")


@router.get("",
            status_code=status.HTTP_200_OK,
            response_model=Union[List[tag_schema.Tag], ResponseMsg],
            responses={200: {"description": "All Tags Requested"}})
async def get_tags(db: Session = Depends(get_db)):
    tags = tag_crud.get_tags(db)
    if not tags:
        return {"message": "No registered tags"}

    return tags


@router.get("/{tag_id}",
            status_code=status.HTTP_200_OK,
            response_model=post_schema.TagWithPosts,
            responses={
                200: {"description": "Tag requested by ID"},
                **error_responses([
                    ObjectNotFoundError(message_list=["The tag was not found by ID"]),
                    ValidationError()
                ])
            })
async def get_tag_with_posts(tag_id: UUID, db: Session = Depends(get_db)):
    tag = tag_crud.get_tag(tag_id, db)
    if not tag:
        raise ObjectNotFoundError(output_message="The tag was not found by ID")

    return tag


@router.post("/create",
             status_code=status.HTTP_201_CREATED,
             response_model=tag_schema.Tag,
             responses={
                 201: {"description": "Tag Created"},
                 **error_responses([
                     AlreadyRegisteredError(message_list=["The Tag already registered"]),
                     ObjectNotFoundError(message_list=["The admin user was not found", "The admin user is not active"]),
                     *jwt_errors_list, *csrf_errors_list
                 ])
             })
async def create_tag(
        new_tag: tag_schema.TagCreate,
        request: Request,
        response: Response,
        csrf_protect: CsrfProtect = Depends(),
        current_admin: admin_schema.Admin = Depends(get_current_active_admin),
        db: Session = Depends(get_db)
):
    auth_service.verify_csrf(request, csrf_protect)
    auth_service.update_jwt(current_admin.id, response)
    if tag_crud.get_tag_by_title(new_tag.title, db):
        raise AlreadyRegisteredError(output_message="The Tag already registered")
    return tag_crud.create_tag(new_tag, db)


@router.put("/{tag_id}", status_code=status.HTTP_200_OK, response_model=tag_schema.Tag,
            responses={
                200: {"description": "Tag Updated"},
                **error_responses([
                    AlreadyRegisteredError(message_list=["The Tag already registered"]),
                    ObjectNotFoundError(message_list=[
                        "The Tag was not found by ID",
                        "The admin user was not found",
                        "The admin user is not active"]),
                    *jwt_errors_list, *csrf_errors_list
                ])
            })
async def update_tag(
        tag_id: UUID,
        new_tag: tag_schema.TagUpdate,
        request: Request,
        response: Response,
        csrf_protect: CsrfProtect = Depends(),
        current_admin: admin_schema.Admin = Depends(get_current_active_admin),
        db: Session = Depends(get_db)
):
    auth_service.verify_csrf(request, csrf_protect)
    auth_service.update_jwt(current_admin.id, response)
    if tag_crud.get_tag_by_title(new_tag.title, db):
        raise AlreadyRegisteredError(output_message="The Tag already registered")

    return tag_crud.update_tag(tag_id, new_tag, db)


@router.delete("{tag_id}",
               status_code=status.HTTP_200_OK,
               response_model=ResponseMsg,
               responses={
                   200: {"description": "Tag Deleted"},
                   **error_responses([
                       *jwt_errors_list,
                       *csrf_errors_list,
                       ObjectNotFoundError(message_list=[
                           "The Tag was not found by ID",
                           "The admin user was not found",
                           "The admin user is not active"])
                   ])
               })
async def delete_tag(
        tag_id: UUID,
        request: Request,
        response: Response,
        csrf_protect: CsrfProtect = Depends(),
        current_admin: admin_schema.Admin = Depends(get_current_active_admin),
        db: Session = Depends(get_db)
):
    auth_service.verify_csrf(request, csrf_protect)
    auth_service.update_jwt(current_admin.id, response)
    result = tag_crud.delete_tag(tag_id, db)
    if result:
        return {"message": "Successfully Tag Deleted"}
    else:
        return {"message": "Failed delete tag object"}
