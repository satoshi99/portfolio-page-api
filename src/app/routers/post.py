from uuid import UUID
from typing import List

from fastapi import APIRouter, status, Depends, Request, Response
from fastapi_csrf_protect import CsrfProtect

from sqlalchemy.orm import Session

from database import get_db
from schemas import post_schema, admin_schema, ResponseMsg
from cruds import post_crud
from cruds.domain import MapPostAndTags
from services import auth_service
from .admin import get_current_active_admin
from exceptions import error_responses, ObjectNotFoundError, AlreadyRegisteredError, jwt_errors_list, csrf_errors_list

router = APIRouter(prefix="/posts")


@router.get("",
            status_code=status.HTTP_200_OK,
            response_model=List[post_schema.Post],
            responses={
                200: {"description": "My Posts Requested"},
                **error_responses([
                    ObjectNotFoundError(message_list=["The admin user was not found", "The admin user is not active"]),
                    *jwt_errors_list
                ])
            })
async def get_my_posts(
        response: Response,
        current_admin: admin_schema.Admin = Depends(get_current_active_admin),
        db: Session = Depends(get_db)
):
    auth_service.update_jwt(current_admin.id, response)
    posts = post_crud.get_my_posts(current_admin.id, db)
    return posts


@router.get("/public",
            status_code=status.HTTP_200_OK,
            response_model=List[post_schema.PostPublic],
            responses={200: {"description": "Public Posts Requested"}})
async def get_public_posts(db: Session = Depends(get_db)):
    posts = post_crud.get_public_posts(db)
    return posts


@router.get("/{post_id}",
            status_code=status.HTTP_200_OK,
            response_model=post_schema.Post,
            responses={
                200: {"description": "The Post Requested"},
                **error_responses([ObjectNotFoundError(message_list=["The post was not found by ID"])])
            })
async def get_post(post_id: UUID, db: Session = Depends(get_db)):
    post = post_crud.get_post(post_id, db)
    if not post:
        raise ObjectNotFoundError(output_message="The post was not found by ID")
    return post


@router.post("/create",
             status_code=status.HTTP_201_CREATED,
             response_model=post_schema.Post,
             responses={
                 201: {"description": "The Post Created"},
                 **error_responses([
                     AlreadyRegisteredError(message_list=["The url-slug has already registered"]),
                     ObjectNotFoundError(message_list=[
                         "The admin user was not found",
                         "The admin user is not active",
                         "The tag was not found by ID"]),
                     *jwt_errors_list, *csrf_errors_list
                 ])
             })
async def create_post(
        post_data: post_schema.PostCreate,
        tag_ids: List[UUID],
        request: Request,
        response: Response,
        csrf_protect: CsrfProtect = Depends(),
        current_admin: admin_schema.Admin = Depends(get_current_active_admin),
        db: Session = Depends(get_db)
):
    auth_service.verify_csrf(request, csrf_protect)
    auth_service.update_jwt(current_admin.id, response)
    db_post = post_crud.create_post(current_admin.id, post_data, db)
    if tag_ids:
        map_post_tags = MapPostAndTags()
        db_post = map_post_tags.create_map(tag_ids, db_post, db)
    return db_post


@router.put("/{post_id}",
            status_code=status.HTTP_200_OK,
            response_model=post_schema.Post,
            responses={
                200: {"description": "The Post Updated"},
                **error_responses([
                    *jwt_errors_list,
                    *csrf_errors_list,
                    AlreadyRegisteredError(message_list=["The post was not found by ID"]),
                    ObjectNotFoundError(message_list=[
                        "The post was not found by ID",
                        "The tag was not found by ID",
                        "The admin user was not found",
                        "The admin user is not active"])
                ])
            })
async def update_post(
        post_id: UUID,
        post_data: post_schema.PostUpdate,
        tag_ids: List[UUID],
        request: Request,
        response: Response,
        csrf_protect: CsrfProtect = Depends(),
        current_admin: admin_schema.AdminWithPosts = Depends(get_current_active_admin),
        db: Session = Depends(get_db)
):
    auth_service.verify_csrf(request, csrf_protect)
    auth_service.update_jwt(current_admin.id, response)
    posts = current_admin.posts
    db_post = [post for post in posts if post.id == post_id]
    if not db_post:
        raise ObjectNotFoundError(output_message="The post was not found by ID")
    db_post = post_crud.update_post(db_post[0], post_data, db)

    map_post_tags = MapPostAndTags()
    if tag_ids and not db_post.tags:
        db_post = map_post_tags.create_map(tag_ids, db_post, db)
    elif tag_ids:
        db_post = map_post_tags.update_map(tag_ids, db_post, db)
    return db_post


@router.delete("/{post_id}",
               status_code=status.HTTP_200_OK,
               response_model=ResponseMsg,
               responses={
                   200: {"description": "The Post Deleted"},
                   **error_responses([
                       ObjectNotFoundError(message_list=[
                           "The post was not found by ID",
                           "The admin user was not found",
                           "The admin user is not active"]),
                       *jwt_errors_list, *csrf_errors_list
                   ])
               })
async def delete_post(
        post_id: UUID,
        request: Request,
        response: Response,
        csrf_protect: CsrfProtect = Depends(),
        current_admin: admin_schema.AdminWithPosts = Depends(get_current_active_admin),
        db: Session = Depends(get_db)
):
    auth_service.verify_csrf(request, csrf_protect)
    auth_service.update_jwt(current_admin.id, response)
    posts = current_admin.posts
    db_post = [post for post in posts if post.id == post_id]
    if not db_post:
        raise ObjectNotFoundError(output_message="The post was not found by ID")

    post_crud.delete_post(db_post[0], db)

    if not post_crud.get_post(post_id, db):
        return {"message": "Successfully Post Deleted"}
    else:
        return {"message": "Failed delete"}
