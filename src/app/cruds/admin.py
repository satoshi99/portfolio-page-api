from uuid import UUID
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import Union
from models import admin as model
from schemas import admin as schema
from .base import BaseCRUD

import logging
from logging import LogRecord


class NoPasswordLogFilter(logging.Filter):
    def filter(self, record: LogRecord) -> bool:
        message = record.getMessage()
        return "password" not in message


logger = logging.getLogger(__name__)
log_file = logging.FileHandler("log/crud_admin.log")
logger.addHandler(log_file)
logger.addFilter(NoPasswordLogFilter())


class AdminCRUD(BaseCRUD):

    def get_admin(self, key: Union[UUID, str]) -> model.Admin:
        logger.info({
            "action": "get admin model by id or email",
            "key": type(key),
            "status": "run"
        })

        if type(key) == UUID:
            db_admin = self.db.query(model.Admin).filter(model.Admin.id == key).first()
        else:
            db_admin = self.db.query(model.Admin).filter(model.Admin.email == key).first()

        if not db_admin:
            logger.error(f"Failed to get admin by {type(key)} (UUID: admin_id, str: email) from DB")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Admin user not found"
            )

        logger.info({
            "action": "get admin model by id or email",
            "key": type(key),
            "status": "success"
        })

        return db_admin

    # def get_admin_by_email(self, email: str) -> Union[schema.AdminInDB, bool]:
    #     db_admin = self.get_admin(key=email)
    #     return schema.AdminInDB(**jsonable_encoder(db_admin))
    #
    # def get_admin_by_id(self, admin_id: UUID) -> Union[schema.AdminInDB, bool]:
    #     db_admin = self.get_admin(key=admin_id)
    #     return schema.AdminInDB(**jsonable_encoder(db_admin))

    def create_admin(self, email: str, hashed_password: str) -> schema.Admin:
        logger.info({
            "action": "insert new admin to db",
            "status": "run"
        })

        try:
            db_admin = model.Admin(email=email, hashed_password=hashed_password)
            self.db.add(db_admin)
            self.db.commit()
            self.db.refresh(db_admin)
        except Exception as e:
            logger.error("Failed create admin user")
            raise e

        logger.info({
            "action": "insert new admin to db",
            "status": "success"
        })

        return schema.Admin(**jsonable_encoder(db_admin))

    def update_admin(self, admin_id: UUID, new_data: schema.AdminUpdate) -> schema.Admin:
        logger.info({
            "action": "update admin from db",
            "admin_id": admin_id,
            "new_data": new_data,
            "status": "run"
        })

        db_admin = self.get_admin(key=admin_id)

        try:
            if new_data.email:
                db_admin.email = new_data.email
            self.db.commit()
        except Exception as e:
            logger.error("Failed update admin user")
            raise e

        logger.info({
            "action": "update admin from db",
            "admin_id": admin_id,
            "new_data": new_data,
            "status": "success"
        })

        return schema.Admin(**jsonable_encoder(db_admin))

    def delete_admin(self, admin_id: UUID) -> bool:
        logger.info({
            "action": "delete admin from db",
            "admin_id": admin_id,
            "status": "run"
        })

        db_admin = self.get_admin(key=admin_id)

        try:
            self.db.delete(db_admin)
            self.db.commit()
        except Exception as e:
            logger.error("Failed delete admin user from DB")
            raise e

        if not self.get_admin(key=admin_id):
            logger.info({
                "action": "delete admin from db",
                "admin_id": admin_id,
                "status": "success"
            })
            return True
        else:
            logger.info({
                "action": "delete admin from db",
                "admin_id": admin_id,
                "status": "Delete process is done but the object has not deleted"
            })
            return False
