from uuid import UUID
import datetime

from sqlalchemy.orm import Session

from models import Admin
from schemas import admin_schema
from .domain import update_process
from services import auth_service
from utils.logger import setup_logger
from .domain.logging_utils import NoPasswordLogFilter


log_folder = f"log/{datetime.date.today()}.log"
logger = setup_logger(log_folder=log_folder, log_filter=NoPasswordLogFilter(), modname=__name__)


class AdminCrud:

    def get_admin_by_id(self, admin_id: UUID, db: Session) -> Admin:
        logger.info({
            "action": "get admin model by id",
            "admin_id": admin_id,
            "status": "run"
        })

        db_admin = db.query(Admin).filter(Admin.id == admin_id).first()

        logger.info({
            "action": "get admin model by id",
            "status": "success"
        })

        return db_admin

    def get_admin_by_email(self, email: str, db: Session) -> Admin:
        logger.info({
            "action": "get admin model by email",
            "status": "run"
        })

        db_admin = db.query(Admin).filter(Admin.email == email).first()

        logger.info({
            "action": "get admin model by email",
            "status": "success"
        })

        return db_admin

    def create_admin(self, new_admin: admin_schema.AdminCreate, db: Session) -> Admin:
        logger.info({
            "action": "insert new admin to db",
            "status": "run"
        })

        admin_password_hash = auth_service.create_salt_and_hashed_password(new_admin.password)

        try:
            db_admin = Admin(
                email=new_admin.email,
                hashed_password=admin_password_hash.hashed_password,
                salt=admin_password_hash.salt
            )
            db.add(db_admin)
            db.commit()
            db.refresh(db_admin)
        except Exception as e:
            logger.error("Failed create admin user")
            db.rollback()
            raise e

        logger.info({
            "action": "insert new admin to db",
            "status": "success"
        })

        return db_admin

    def update_admin(self, current_admin: Admin, new_admin: admin_schema.AdminUpdate, db: Session) -> Admin:
        logger.info({
            "action": "update admin from db",
            "current_admin": current_admin.id,
            "status": "run"
        })

        try:
            db_admin = update_process(current_admin, new_admin)
            db.commit()
        except Exception as ex:
            logger.error("Failed update admin user")
            db.rollback()
            raise ex

        logger.info({
            "action": "update admin from db",
            "status": "success"
        })

        return db_admin

    def delete_admin(self, current_admin: Admin, db: Session) -> bool:
        logger.info({
            "action": "delete admin from db",
            "current_admin": current_admin.id,
            "status": "run"
        })

        try:
            db.delete(current_admin)
            db.commit()
        except Exception as e:
            logger.error("Failed delete admin user from DB")
            db.rollback()
            raise e

        if not self.get_admin_by_id(current_admin.id, db):
            logger.info({
                "action": "delete admin from db",
                "status": "success"
            })
            return True
        else:
            logger.info({
                "action": "delete admin from db",
                "status": "Delete process is done but the object has not deleted"
            })
            return False
