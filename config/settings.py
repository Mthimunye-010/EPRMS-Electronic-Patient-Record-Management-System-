"""Django settings for the Electronic Patient Record Management System."""

import os
import secrets
from pathlib import Path
from django.utils.csp import CSP

BASE_DIR = Path(__file__).resolve().parent.parent

# A local-only fallback keeps the student project runnable. Production must set DJANGO_SECRET_KEY.
DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() == "true"
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = secrets.token_urlsafe(50)
    else:
        raise RuntimeError("DJANGO_SECRET_KEY must be set when DEBUG=False.")
if not DEBUG and (len(SECRET_KEY) < 50 or "replace-this" in SECRET_KEY.lower()):
    raise RuntimeError("Production requires a unique, high-entropy DJANGO_SECRET_KEY.")

ALLOWED_HOSTS = [h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "accounts", "core", "patients", "records", "audit",
    "django_otp", "django_otp.plugins.otp_totp",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.csp.ContentSecurityPolicyMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "audit.middleware.CurrentUserMiddleware",
    "audit.middleware.InactivityTimeoutMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.debug",
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "accounts.context_processors.security_context",
    ]},
}]

WSGI_APPLICATION = "config.wsgi.application"

DB_ENGINE = os.environ.get("DJANGO_DB_ENGINE", "sqlite").lower()
if DB_ENGINE == "sqlite":
    if not DEBUG:
        raise RuntimeError("Production must use PostgreSQL; SQLite is for local development only.")
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
else:
    db_host = os.environ.get("DJANGO_DB_HOST", "localhost")
    db_options = {}
    sslmode = os.environ.get("DJANGO_DB_SSLMODE")
    local_db_hosts = {"localhost", "127.0.0.1", "::1"}
    if not DEBUG and db_host not in local_db_hosts:
        sslmode = sslmode or ""
        sslrootcert = os.environ.get("DJANGO_DB_SSLROOTCERT")
        if sslmode != "verify-full" or not sslrootcert:
            raise RuntimeError("Remote production PostgreSQL requires DJANGO_DB_SSLMODE=verify-full and DJANGO_DB_SSLROOTCERT.")
    if sslmode:
        db_options["sslmode"] = sslmode
    if os.environ.get("DJANGO_DB_SSLROOTCERT"):
        db_options["sslrootcert"] = os.environ["DJANGO_DB_SSLROOTCERT"]
    DATABASES = {"default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["DJANGO_DB_NAME"],
        "USER": os.environ["DJANGO_DB_USER"],
        "PASSWORD": os.environ["DJANGO_DB_PASSWORD"],
        "HOST": db_host,
        "PORT": os.environ.get("DJANGO_DB_PORT", "5432"),
        "OPTIONS": db_options,
    }}

AUTH_USER_MODEL = "accounts.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "core:dashboard"
LOGOUT_REDIRECT_URL = "accounts:login"
OTP_LOGIN_URL = "accounts:login"
OTP_TOTP_THROTTLE_FACTOR = 1

LANGUAGE_CODE = "en-za"
TIME_ZONE = "Africa/Johannesburg"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Session and browser security. The short timeout reduces exposure on unattended hospital workstations.
SESSION_COOKIE_AGE = 60 * 15
SESSION_INACTIVITY_TIMEOUT = 60 * 15
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
SECURE_CSP = {
    "default-src": [CSP.SELF],
    "script-src": [CSP.SELF, "https://cdn.jsdelivr.net"],
    "style-src": [CSP.SELF, "https://cdn.jsdelivr.net"],
    "img-src": [CSP.SELF, "data:"],
    "font-src": [CSP.SELF, "data:", "https://cdn.jsdelivr.net"],
    "connect-src": [CSP.SELF],
    "object-src": [CSP.NONE],
    "base-uri": [CSP.SELF],
    "form-action": [CSP.SELF],
    "frame-ancestors": [CSP.NONE],
}
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
