from .core_errors import ApiException
from typing import List


class JwtExpiredSignatureError(ApiException):
    status_code = 401
    error_code = "Expired Signature"
    headers = {"WWW-Authenticate": "Bearer"}

    def __init__(
            self,
            output_message: str = "The JWT signature has expired",
            message_list: List[str] = None
    ):
        super().__init__(output_message, message_list)
        if not message_list:
            self.message_list = [output_message]


class UnauthorizedAdminError(ApiException):
    status_code = 401
    error_code = "Unauthorized Admin"
    headers = {"WWW-Authenticate": "Bearer"}

    def __init__(
            self,
            output_message: str = "Not authenticated",
            message_list: List[str] = None
    ):
        super().__init__(output_message, message_list)
        if not message_list:
            self.message_list = [output_message]


jwt_errors_list = [JwtExpiredSignatureError(), UnauthorizedAdminError()]
