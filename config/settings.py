"""
Django settings for ai-workbench project.

Generated by 'django-admin startproject' using Django 5.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
import secrets
from pathlib import Path
import sentry_sdk
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# PROJECT_ROOT = root_dir = os.path.dirname(os.path.abspath(__file__))

# Sets the SYSTEM_PROMPT variable to the value of config/SYSTEM_PROMPT.txt
with open(BASE_DIR / "config" / "SYSTEM_PROMPT.txt", "r") as f:
    SYSTEM_PROMPT = f.read().strip()

# Before using your Heroku app in production, make sure to review Django's deployment checklist:
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# Django requires a unique secret key for each Django app, that is used by several of its
# security features. To simplify initial setup (without hardcoding the secret in the source
# code) we set this to a random value every time the app starts. However, this will mean many
# Django features break whenever an app restarts (for example, sessions will be logged out).
# In your production Heroku apps you should set the `DJANGO_SECRET_KEY` config var explicitly.
# Make sure to use a long unique value, like you would for a password. See:
# https://docs.djangoproject.com/en/5.1/ref/settings/#std-setting-SECRET_KEY
# https://devcenter.heroku.com/articles/config-vars
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    default=secrets.token_urlsafe(nbytes=64),
)

GOOGLE_DOC_SYSTEM_PROMPT = """
You are an AI Agent optimized to update Google Documents based on the users request.
"""

# The `DYNO` env var is set on Heroku CI, but it's not a real Heroku app, so we have to
# also explicitly exclude CI:
# https://devcenter.heroku.com/articles/heroku-ci#immutable-environment-variables
PRODUCTION = "DYNO" in os.environ and not "CI" in os.environ

IS_HEROKU_APP = PRODUCTION

# SECURITY WARNING: don't run with debug turned on in production!
if not PRODUCTION:
    DEBUG = True

# On Heroku, it's safe to use a wildcard for `ALLOWED_HOSTS``, since the Heroku router performs
# validation of the Host header in the incoming HTTP request. On other platforms you may need to
# list the expected hostnames explicitly in production to prevent HTTP Host header attacks. See:
# https://docs.djangoproject.com/en/5.1/ref/settings/#std-setting-ALLOWED_HOSTS
if PRODUCTION:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = [".localhost", "127.0.0.1", "[::1]", "0.0.0.0"]


if PRODUCTION:
    BASE_URL = "https://ai-workbench-c743dbb30500.herokuapp.com"
else:
    BASE_URL = "http://localhost:8000"

# Application definition

INSTALLED_APPS = [
    # Use WhiteNoise's runserver implementation instead of the Django default, for dev-prod parity.
    "whitenoise.runserver_nostatic",
    # Uncomment this and the entry in `urls.py` if you wish to use the Django admin feature:
    # https://docs.djangoproject.com/en/5.1/ref/contrib/admin/
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "web",
    "django_rq",
    "llm",
    "tools",
    "channels",
    "ai_agents",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Django doesn't support serving static assets in a production-ready way, so we use the
    # excellent WhiteNoise package to do so instead. The WhiteNoise middleware must be listed
    # after Django's `SecurityMiddleware` so that security redirects are still performed.
    # See: https://whitenoise.readthedocs.io
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

if PRODUCTION:
    # In production on Heroku the database configuration is derived from the `DATABASE_URL`
    # environment variable by the dj-database-url package. `DATABASE_URL` will be set
    # automatically by Heroku when a database addon is attached to your Heroku app. See:
    # https://devcenter.heroku.com/articles/provisioning-heroku-postgres#application-config-vars
    # https://github.com/jazzband/dj-database-url
    DATABASES = {
        "default": dj_database_url.config(
            env="DATABASE_URL",
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True,
        ),
    }
else:
    # When running locally in development or in CI, a sqlite database file will be used instead
    # to simplify initial setup. Longer term it's recommended to use Postgres locally too.
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "static/"

STORAGES = {
    # Enable WhiteNoise's GZip and Brotli compression of static assets:
    # https://whitenoise.readthedocs.io/en/latest/django.html#add-compression-and-caching-support
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Don't store the original (un-hashed filename) version of static files, to reduce slug size:
# https://whitenoise.readthedocs.io/en/latest/django.html#WHITENOISE_KEEP_ONLY_HASHED_FILES
WHITENOISE_KEEP_ONLY_HASHED_FILES = True


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

RQ_QUEUES = {
    'default': {
        'URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0'), # If you're on Heroku
        'DEFAULT_TIMEOUT': 500,
        # 'HOST': 'localhost',
        # 'PORT': 6379,
        # 'DB': 0,
        # 'USERNAME': 'some-user',
        # 'PASSWORD': 'some-password',
        # 'DEFAULT_TIMEOUT': 360,
        # 'REDIS_CLIENT_KWARGS': {    # Eventual additional Redis connection arguments
        #     'ssl_cert_reqs': None,
        # },
        # 'SERIALIZER': 'rq.serializers.JSONSerializer',
    },
    'high': {
        'URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0'), # If you're on Heroku
        'DEFAULT_TIMEOUT': 500,
    },
    'medium': {
        'URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0'), # If you're on Heroku
        'DEFAULT_TIMEOUT': 500,
    },
    'low': {
        'URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0'), # If you're on Heroku
        'DEFAULT_TIMEOUT': 500,
        # 'SERIALIZER': 'rq.serializers.JSONSerializer',
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "rq_console": {
            "format": "%(asctime)s %(message)s",
            "datefmt": "%H:%M:%S",
        },
    },
    "handlers": {
        "rq_console": {
            "level": "DEBUG",
            "class": "rq.logutils.ColorizingStreamHandler",
            "formatter": "rq_console",
            "exclude": ["%(asctime)s"],
        },
    },
    # 'loggers': {
    #     "rq.worker": {
    #         "handlers": ["rq_console", "sentry"],
    #         "level": "DEBUG"
    #     },
    # }
}

RQ_SHOW_ADMIN_LINK = True

SESSION_COOKIE_NAME = "tokenname_sessionid"

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

AI_CHANNEL_ID = 1286389011144773632

DOCUMENT_ID = "1jHYLQRL0CAolpTHTMm-7Jy-a9XcrZsw868ArZ1IHfHs"

TOOL_DEFINITIONS = [
    {
        "name": "get_time",
        "description": "Get the current time when the user specifically asks for it. Only used when requesting the current time.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_runtime_environment",
        "description": """
          Return the current runtime environment (e.g production, staging, development).
          Only used when requesting explicity about the runtime environment.
        """,
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
        {
        "name": "get_web_page_summary",
        "description": "Use this tool to browse a web page for a URL provided by the user and summarize the content of the page",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The url of the web page to be summarized"
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "get_search_results",
        "description": "Get search results from the serper API for a given query",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to be used"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_background_jobs",
        "description": "Call this tool if the user asks you what you are working on or doing in general. Background jobs are the only thing you could be doing besides responding synchronously in the thread.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "update_google_document",
        "description": "Call this tool if you are asked to update a google document.",
        "input_schema": {
            "type": "object",
            "properties": {
                "google_doc_id": {
                    "type": "string",
                    "description": f"ID of google document to be updated and shared by the user. If not URL is provided the default document ID will be used: {DOCUMENT_ID}"
                }
            },
            "required": ["google_doc_id"]
        }
    },
    {
        "name": "read_google_document",
        "description": "Read the contents of a Google Document to respod to the user's request.",
        "input_schema": {
            "type": "object",
            "properties": {
                "google_doc_id": {
                    "type": "string",
                    "description": f"ID of google document to be updated and shared by the user. If not URL is provided the default document ID will be used: {DOCUMENT_ID}"
                }
            },
            "required": ["google_doc_id"]
        }
    },
    {
        "name": "read_project_overview",
        "description": "Read the project overview document to respond to questions about your implementation",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": f"What the user requested to know about the project."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": 'open_pull_request',
        "description": 'Invoke this tool when asked to make a pull request',
        "input_schema": {
            "type": 'object',
            "properties": {'description': {'type': 'string', 'description': 'Description of the pull request'}},
            "required": ['description'],
        },
    },
]

if PRODUCTION and os.getenv('SENTRY_DSN') != '':
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for tracing.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
    )

CREDENTIALS_ENCRYPTION_KEY = os.getenv('CREDENTIALS_ENCRYPTION_KEY')