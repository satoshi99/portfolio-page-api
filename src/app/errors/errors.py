from typing import List, Type, Dict
from schemas import Errors


class ApiException(Exception):
    status_code: int = 400
    error_code: str = 'ApiError'
    headers: Dict = None

    def __init__(
            self,
            message: str = 'API error message'
    ):
        self.message = message


class AlreadyRegisteredError(ApiException):
    status_code = 400
    error_code = 'AlreadyRegistered'

    def __init__(
            self,
            message: str = 'The Requests have already registered in DB'
    ):
        super().__init__(message)
        self.message = message


class JwtExpiredSignatureError(ApiException):
    status_code = 401
    error_code = 'ExpiredSignature'
    headers = {"WWW-Authenticate": "Bearer"}

    def __init__(
            self,
            message: str = 'The JWT signature has expired'
    ):
        super().__init__(message)
        self.message = message


class UnauthorizedAdminError(ApiException):
    status_code = 401
    error_code = 'UnauthorizedAdmin'
    headers = {"WWW-Authenticate": "Bearer"}

    def __init__(
            self,
            message: str = 'Could not validate authentication credentials'
    ):
        super().__init__(message)
        self.message = message


class ObjectNotFoundError(ApiException):
    status_code = 404
    detail = 'ObjectNotFound'

    def __init__(
            self,
            message: str = 'Objects not found in DB'
    ):
        super().__init__(message)
        self.message = message


def error_responses(error_types: List[Type[ApiException]]) -> Dict:
    d = {}

    for error_type in error_types:
        error = error_type()
        if not d.get(error_type.status_code):
            d[error_type.status_code] = {
                'model': Errors,
                'description': f'"{error.error_code}"',
                'content': {
                    'application/json': {
                        'example': {
                            'errors': [
                                {
                                    'status': error.status_code,
                                    'code': error.error_code,
                                    'message': error.message
                                }
                            ]
                        }
                    }
                }
            }
        else:
            d[error_type.status_code]['description'] += f'<br>"{error_type.error_code}"'
            d[error_type.status_code]['content']['application/json']['example']['errors']\
                .append({'status': error.status_code, 'code': error.error_code, 'message': error.message})

    return d
