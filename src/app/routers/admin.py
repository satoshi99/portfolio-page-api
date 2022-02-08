from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_csrf_protect import CsrfProtect
from sqlalchemy.orm import Session
from schemas import admin as admin_schema
from schemas import auth as auth_schema
from schemas.common import ResponseMsg
from models import admin as admin_model
from cruds.admin import AdminCrud
from database import get_db
from auth import AuthJwtCsrf
from env import API_PREFIX

router = APIRouter(prefix="/admin")
crud = AdminCrud()
auth = AuthJwtCsrf()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{API_PREFIX}/admin/token")


async def get_current_admin(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> admin_model.Admin:
    admin_id = auth.decode_jwt(token)
    db_admin = crud.get_admin_by_id(admin_id, db)
    if not db_admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin user not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return db_admin


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=admin_schema.Admin)
async def create_admin(
        new_admin: admin_schema.AdminCreate,
        request: Request,
        csrf_protect: CsrfProtect = Depends(),
        db: Session = Depends(get_db)
):
    auth.verify_csrf(request, csrf_protect)
    if crud.get_admin_by_email(new_admin.email, db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    hashed_password = auth.get_password_hash(new_admin.password)
    return crud.create_admin(new_admin.email, hashed_password, db)


@router.post("/token", status_code=status.HTTP_201_CREATED, response_model=auth_schema.Token)
async def login_for_access_token(
        response: Response,
        request: Request,
        csrf_protect: CsrfProtect = Depends(),
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    auth.verify_csrf(request, csrf_protect)
    db_admin = crud.get_admin_by_email(form_data.username, db)
    if not db_admin or not auth.verify_password(form_data.password, db_admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth.create_access_token({"sub": jsonable_encoder(db_admin.id)})
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_200_OK, response_model=ResponseMsg)
async def logout(response: Response, request: Request, csrf_protect: CsrfProtect = Depends()):
    auth.verify_csrf(request, csrf_protect)
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged-out"}


@router.get("/myinfo", status_code=status.HTTP_200_OK, response_model=admin_schema.Admin)
async def get_admin(current_admin: admin_model.Admin = Depends(get_current_admin)):
    return current_admin


@router.put("/update", status_code=status.HTTP_200_OK, response_model=admin_schema.Admin)
async def update_admin(
        new_data: admin_schema.AdminUpdate,
        request: Request,
        csrf_protect: CsrfProtect = Depends(),
        current_admin: admin_model.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    auth.verify_csrf(request, csrf_protect)
    return crud.update_admin(current_admin, new_data, db)


@router.delete("/delete", status_code=status.HTTP_200_OK, response_model=ResponseMsg)
async def delete_admin(
        request: Request,
        csrf_protect: CsrfProtect = Depends(),
        current_admin: admin_model.Admin = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    auth.verify_csrf(request, csrf_protect)
    result = crud.delete_admin(current_admin, db)
    if result:
        return {"message": "Successfully Admin Deleted"}
    else:
        return {"message": "Failed Admin Delete"}
