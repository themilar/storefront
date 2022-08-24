from .base import *
import django_on_heroku

django_on_heroku.settings(locals())


ALLOWED_HOSTS += [
    "agile-fortress-60729.herokuapp.com",
]

DATABASES = {
    "default": {
        "ENGINE": "django_psdb_engine",
        "NAME": os.environ.get("DB_NAME"),
        "HOST": os.environ.get("DB_HOST"),
        "PORT": os.environ.get("DB_PORT"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "OPTIONS": {"ssl": {"ca": os.environ.get("MYSQL_ATTR_SSL_CA")}},
    }
}
