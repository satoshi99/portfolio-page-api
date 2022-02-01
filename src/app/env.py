from decouple import config

API_TITLE = "Portfolio site"
API_VERSION = "1.0.0"
API_PREFIX = f"/api/v{API_VERSION}"

DB_USER = config("MARIADB_USER", cast=str)
DB_PASSWORD = config("MARIADB_PASSWORD")
DB_DATABASE = config("MARIADB_DATABASE", cast=str)
DB_HOST = config("MARIADB_HOST", cast=str)
