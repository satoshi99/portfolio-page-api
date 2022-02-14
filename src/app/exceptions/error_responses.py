from typing import List, Type, Dict
from schemas import Errors
from .core_errors import ApiException


def error_responses(errors: List[ApiException]) -> Dict:
    d = {}

    for error in errors:
        if not d.get(error.status_code):
            d[error.status_code] = {
                'model': Errors,
                'description': f'"{error.error_code}"',
                'content': {
                    'application/json': {
                        'example': {
                            'exceptions': [
                                {
                                    'status': error.status_code,
                                    'code': error.error_code,
                                    'message': error.message_list
                                }
                            ]
                        }
                    }
                }
            }
        else:
            d[error.status_code]['description'] += f'<br>"{error.error_code}"'
            d[error.status_code]['content']['application/json']['example']['exceptions']\
                .append({
                    'status': error.status_code,
                    'code': error.error_code,
                    'message': error.message_list
                })

    return d
