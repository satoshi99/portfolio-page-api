from .core_errors import ApiException
from fastapi_csrf_protect.load_config import LoadConfig

config = LoadConfig()
header_name = config.csrf_header_name
header_type = config.csrf_header_type

_error_code = "Could Not Verify CSRF Token"


class InvalidHeaderError(ApiException):
    status_code = 422
    error_code = _error_code
    message_list = [
            f'Bad headers. Expected "{header_name}" in headers',
            f'Bad {header_name} header. Expected value "<Token>"',
            f'Bad {header_name} header. Expected value "{header_type} <Token>"'
        ]


class TokenValidationError(ApiException):
    status_code = 401
    error_code = _error_code
    message_list = [
            "The CSRF token is missing.",
            "The CSRF token has expired.",
            "The CSRF token is invalid."
        ]


csrf_errors_list = [InvalidHeaderError, TokenValidationError]
