from decouple import config
from passlib.context import CryptContext

DB_URL = config('DB_URL', default="sqlite:///./mydb.sqlite", cast=str)
APP_ENV = config('APP_ENV', default='DEV', cast=str)
SECRET_KEY = config('SECRET_KEY', default='secret', cast=str)
COOKIE_NAME = config('COOKIE_NAME', default="auth_token", cast=str)
TOKEN_EXPIRE_MINUTES = config('TOKEN_EXPIRE_MINUTES', default=30, cast=int)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")