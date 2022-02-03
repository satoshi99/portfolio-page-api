from decouple import config

API_TITLE = "Portfolio site"
API_VERSION = "1.0.0"
API_PREFIX = f"/api/v{API_VERSION}"

DB_USER = config("MARIADB_USER", cast=str)
DB_PASSWORD = config("MARIADB_PASSWORD")
DB_DATABASE = config("MARIADB_DATABASE", cast=str)
DB_HOST = config("MARIADB_HOST", cast=str)

CSRF_SECRET_KEY = config("CSRF_SECRET_KEY")
JWT_SECRET_KEY = config('JWT_SECRET_KEY')
ALGORITHM = config('ALGORITHM', cast=str)
JWT_EXPIRE_MINUTES = config('JWT_EXPIRE_MINUTES', cast=int)
JWT_NOT_BEFORE_SECONDS = config('JWT_NOT_BEFORE_SECONDS', cast=int)
