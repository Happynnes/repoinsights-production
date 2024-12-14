from datetime import timedelta
from pathlib import Path
import os
import mimetypes
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

STATIC_URL = "/static/"

develop = os.environ.get("DEVELOP", True)
debug = True
FRONTEND_URL = os.environ["FRONTEND_URL"]

mimetypes.add_type("text/css", ".css", True)
mimetypes.add_type("text/javascript", ".js", True)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if debug else False

ALLOWED_HOSTS = [
    "146.83.216.228",
    "localhost",
    "backend.repoinsights.app",
    "repoinsights.app",
    "127.0.0.1",
]

CONSOLIDADA_DATABASE = os.environ["CONSOLIDADA_DB"]
CONSOLIDADA_USER = os.environ["CONSOLIDADA_USER"]
CONSOLIDADA_IP = os.environ["CONSOLIDADA_IP"]
CONSOLIDADA_PASSWORD = os.environ["CONSOLIDADA_PASS"]
CONSOLIDADA_PORT = os.environ["CONSOLIDADA_PORT"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "django_extensions",
    # Local apps
    "social",
    "metabase",
    "users",
    "repoinsights",
    "githubuser",
    "rabbitmq",
    "superset"
]


MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost",
    "http://146.83.216.228:5173",
    "http://127.0.0.1",
    "https://repoinsights.app",
]

CORS_ALLOW_CREDENTIALS = True


CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost",
    "http://127.0.0.1",
    "https://repoinsights.app",
    "https://*.repoinsights.app",
]


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"

default = {}
if develop:
    default = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
else:
    default = {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASS"],
        "HOST": os.environ["DB_IP"],
        "PORT": os.environ["DB_PORT"],
    }


DATABASES = {
    "default": default,
    "repoinsights": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "ghtorrent_restore_2015",
        "USER": CONSOLIDADA_USER,
        "PASSWORD": CONSOLIDADA_PASSWORD,
        "HOST": CONSOLIDADA_IP,
        "PORT": CONSOLIDADA_PORT,
        "READ_ONLY": True,
    },
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


GITHUB_CLIENT_ID = os.environ["GITHUB_CLIENT_ID"]
GITHUB_CLIENT_SECRET = os.environ["GITHUB_CLIENT_SECRET"]
GITHUB_SCOPES = ["read:user", "user:email", "read:project"]


REST_AUTH_SERIALIZERS = {
    "USER_DETAILS_SERIALIZER": "social.serializers.UserSerializer",
}


AUTH_USER_MODEL = "users.CustomUser"
METABASE_URL = os.environ["METABASE_URL"]
MB_ADMIN_USER = os.environ["MB_ADMIN_USER"]
MB_ADMIN_PASS = os.environ["MB_ADMIN_PASS"]
METABASE_SECRET_KEY = os.environ["METABASE_SECRET_KEY"]


SUPERSET_URL = os.environ["SUPERSET_URL"]
SUPERSET_ADMIN_USER = os.environ["SUPERSET_ADMIN_USER"]
SUPERSET_ADMIN_PASS = os.environ["SUPERSET_ADMIN_PASS"]