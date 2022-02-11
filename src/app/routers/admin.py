from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_csrf_protect import CsrfProtect

from sqlalchemy.orm import Session

from schemas import admin_schema, auth_schema, ResponseMsg
from models import Admin
from cruds import admin_crud
from database import get_db
from services import auth_service
from utils.env import API_PREFIX

from errors import error_responses, AlreadyRegisteredError, JwtExpiredSignatureError, UnauthorizedAdminError

router = APIRouter(prefix="/admin")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{API_PREFIX}/admin/token")


async def get_current_admin(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> Admin:

    admin_id = auth_service.decode_jwt(token)
    db_admin = admin_crud.get_admin_by_id(admin_id, db)

    return db_admin


async def get_current_active_admin(
        current_admin: admin_schema.Admin = Depends(get_current_admin)
) -> Admin:
    if not current_admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not current_admin.is_active or not current_admin.email_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not an active user.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return current_admin


@router.get("/csrftoken", response_model=auth_schema.Csrf,
            responses={
                200: {"description": "CSRF Token Requested"},
                400: {
                    # "model": Errors,
                    "description": "Bad Request",
                    "content": {
                        'application/json': {
                            'example': {
                                'detail': "The server cannot or will not process the request"
                            }
                        }
                    }
                }
            }
            )
def get_csrf_token(csrf_protect: CsrfProtect = Depends()):
    csrf_token = csrf_protect.generate_csrf()
    return {"csrf_token": csrf_token}


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=admin_schema.Admin,
             responses={
                 201: {"description": "Temporary Admin Created"},
                 **error_responses([AlreadyRegisteredError])
             })
async def create_admin_temporary(
        new_admin: admin_schema.AdminCreate,
        request: Request,
        csrf_protect: CsrfProtect = Depends(),
        db: Session = Depends(get_db)
):
    auth_service.verify_csrf(request, csrf_protect)
    if admin_crud.get_admin_by_email(new_admin.email, db):
        raise AlreadyRegisteredError(message="Requested Email already registered")
    return admin_crud.create_admin(new_admin, db)


@router.post("/verify-email/{admin_id}", status_code=status.HTTP_201_CREATED, response_model=admin_schema.Admin)
async def verify_email_and_register_admin(
        admin_id: UUID,
        request: Request,
        csrf_protect: CsrfProtect = Depends(),
        db: Session = Depends(get_db)
):
    auth_service.verify_csrf(request, csrf_protect)
    db_admin = admin_crud.get_admin_by_id(admin_id, db)
    if not db_admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found by request id",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return admin_crud.activate_admin(db_admin, db)


@router.post("/token", status_code=status.HTTP_201_CREATED, response_model=auth_schema.Token)
async def login_for_access_token(
        response: Response,
        request: Request,
        csrf_protect: CsrfProtect = Depends(),
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    auth_service.verify_csrf(request, csrf_protect)
    db_admin = admin_crud.get_admin_by_email(form_data.username, db)
    if not db_admin or not auth_service.verify_password(form_data.password, db_admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_service.create_access_token({"sub": jsonable_encoder(db_admin.id)})
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_200_OK, response_model=ResponseMsg)
async def logout(response: Response, request: Request, csrf_protect: CsrfProtect = Depends()):
    auth_service.verify_csrf(request, csrf_protect)
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged-out"}


@router.get("/myinfo", status_code=status.HTTP_200_OK, response_model=admin_schema.AdminWithPosts,
            responses={
                200: {"description": "Admin Requested with JWT Signature"},
                **error_responses([JwtExpiredSignatureError, UnauthorizedAdminError])
            }
            )
async def get_admin(response: Response, current_admin: Admin = Depends(get_current_active_admin)):
    auth_service.update_jwt(current_admin.id, response)
    return current_admin


@router.put("/update", status_code=status.HTTP_200_OK, response_model=admin_schema.Admin)
async def update_admin(
        new_data: admin_schema.AdminUpdate,
        request: Request,
        response: Response,
        csrf_protect: CsrfProtect = Depends(),
        current_admin: Admin = Depends(get_current_active_admin),
        db: Session = Depends(get_db)
):
    auth_service.verify_csrf(request, csrf_protect)
    auth_service.update_jwt(current_admin.id, response)
    return admin_crud.update_admin(current_admin, new_data, db)


@router.put("/update-password", status_code=status.HTTP_200_OK, response_model=ResponseMsg)
async def update_password_admin(
        password_data: admin_schema.PasswordUpdate,
        request: Request,
        response: Response,
        csrf_protect: CsrfProtect = Depends(),
        current_admin: Admin = Depends(get_current_active_admin),
        db: Session = Depends(get_db)
):
    auth_service.verify_csrf(request, csrf_protect)
    if not auth_service.verify_password(password_data.current_password, current_admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect current password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    auth_service.update_jwt(current_admin.id, response)
    if admin_crud.update_password(password_data.new_password, current_admin, db):
        return {"message": "Successfully updated password"}
    else:
        return {"message": "Failed updated password"}


@router.put("/reset-password", status_code=status.HTTP_200_OK, response_model=ResponseMsg)
async def reset_password_admin(
        new_admin: admin_schema.AdminCreate,
        request: Request,
        csrf_protect: CsrfProtect = Depends(),
        db: Session = Depends(get_db)
):
    auth_service.verify_csrf(request, csrf_protect)
    db_admin = admin_crud.get_admin_by_email(new_admin.email, db)
    if admin_crud.update_password(new_admin.password, db_admin, db):
        return {"message": "Successfully updated password"}
    else:
        return {"message": "Failed updated password"}


@router.delete("/delete", status_code=status.HTTP_200_OK, response_model=ResponseMsg)
async def delete_admin(
        request: Request,
        csrf_protect: CsrfProtect = Depends(),
        current_admin: Admin = Depends(get_current_active_admin),
        db: Session = Depends(get_db)
):
    auth_service.verify_csrf(request, csrf_protect)
    result = admin_crud.delete_admin(current_admin, db)
    if result:
        return {"message": "Successfully Admin Deleted"}
    else:
        return {"message": "Failed Admin Delete"}
