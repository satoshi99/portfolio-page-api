import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError

from schemas.auth import CsrfSettings
from routers import admin_router, post_router, tag_router
from utils.env import API_TITLE, API_VERSION, API_PREFIX, CORS_ORIGIN_WHITELIST
from exceptions import ApiException

logging.basicConfig(level=logging.INFO)


app = FastAPI(title=API_TITLE, version=API_VERSION)

app.include_router(
    admin_router, prefix=API_PREFIX, tags=["admin"])
app.include_router(
    post_router, prefix=API_PREFIX, tags=["posts"])
app.include_router(
    tag_router, prefix=API_PREFIX, tags=["tags"])

origins = CORS_ORIGIN_WHITELIST
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": 422,
            "code": "Validation Error",
            "message": exc.errors()
        }
    )


@app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": exc.status_code,
            "code": "Could Not Verify CSRF Token",
            "message": exc.message
        }
    )


@app.exception_handler(ApiException)
async def api_exception_handler(request: Request, exc: ApiException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": exc.status_code,
            "code": exc.error_code,
            "message": exc.output_message
        },
        headers=exc.headers
    )
