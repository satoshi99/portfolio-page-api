from typing import Dict, List


class ApiException(Exception):
    status_code: int = 400
    error_code: str = "Api Error"
    headers: Dict = None

    def __init__(self, output_message: str = "Api error message", message_list: List[str] = None):
        self.output_message = output_message
        if not message_list:
            self.message_list = [self.output_message]
        else:
            self.message_list = message_list


class BadRequestError(ApiException):
    status_code = 400
    error_code = "Bad Request"

    def __init__(
            self,
            output_message: str = "The server cannot or will not process the request",
            message_list: List[str] = None
    ):
        super().__init__(output_message, message_list)
        if not message_list:
            self.message_list = [output_message]


class AlreadyRegisteredError(ApiException):
    status_code = 400
    error_code = "Already Registered"

    def __init__(
            self,
            output_message: str = "The request has already registered",
            message_list: List[str] = None
    ):
        super().__init__(output_message, message_list)
        if not message_list:
            self.message_list = [output_message]


class ObjectNotFoundError(ApiException):
    status_code = 404
    error_code = "Object Not Found"

    def __init__(
            self,
            output_message: str = "The requested object was not found",
            message_list: List[str] = None
    ):
        super().__init__(output_message, message_list)
        if not message_list:
            self.message_list = [output_message]
