"""Centralized configuration module for POSEIDON System.

Uses environment variables (optionally loaded from a `.env` file) so the same
codebase can run locally with SQLite, on staging with PostgreSQL, or in any
other environment by simply tweaking env vars (handy for Docker / uWSGI / CI).

Available env vars (all optional):

SECRET_KEY          – Flask secret key.
DB_TYPE             – 'postgres' | 'sqlite' | (anything else defaults to generic DATABASE_URL)
POSTGRES_URI        – Full SQLAlchemy URI to Postgres DB.
SQLITE_URI          – Full SQLAlchemy URI to SQLite DB.
DATABASE_URL        – Generic SQLAlchemy URI (over-rides others when DB_TYPE not specified).
BCRYPT_LOG_ROUNDS   – Int, default 15.
MAIL_*              – SMTP settings (see Config class below).
DEBUG / FLASK_ENV   – Standard Flask flags.

Create a file named `.env` in the project root when running locally; it will be
loaded automatically thanks to python-dotenv.
"""

import os
from dotenv import load_dotenv

# ---------------------------------------------------------
# Load environment variables from .env (if present)
# ---------------------------------------------------------
BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))  # silently fails if file missing

TOP_LEVEL_DIR = os.path.abspath(os.curdir)  # convenience constant


# ---------------------------------------------------------
# Helper – resolve DB URI via env hierarchy
# ---------------------------------------------------------

def _get_database_uri() -> str:
    """Return an SQLAlchemy-compatible database URI.

    Resolution order:
    1. If DB_TYPE is 'postgres', use POSTGRES_URI (else fallback to DATABASE_URL).
    2. If DB_TYPE is 'sqlite', use SQLITE_URI (else fallback to default local file).
    3. Otherwise, use DATABASE_URL or default local SQLite.
    """

    db_type = (os.getenv('DB_TYPE') or '').lower()

    if db_type == 'postgres':
        return (
            os.getenv('POSTGRES_URI')
            or os.getenv('DATABASE_URL')
            or 'postgresql://user:password@localhost:5432/poseidon_db'
        )

    if db_type == 'sqlite':
        return (
            os.getenv('SQLITE_URI')
            or 'sqlite:///' + os.path.join(BASEDIR, 'instance/poseidon.db')
        )

    # Generic / fallback
    return (
        os.getenv('DATABASE_URL')
        or 'sqlite:///' + os.path.join(BASEDIR, 'instance/poseidon.db')
    )


# ---------------------------------------------------------
# Base Configuration
# ---------------------------------------------------------

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True

    SECRET_KEY = os.getenv('SECRET_KEY', 'ganti-dengan-secret-key-yang-aman-di-produksi')
    SQLALCHEMY_DATABASE_URI = _get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security / hashing
    BCRYPT_LOG_ROUNDS = int(os.getenv('BCRYPT_LOG_ROUNDS', 15))

    # Mail (optional – only if you enable e-mail features)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.mandrillapp.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'false').lower() in {'true', '1'}
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'false').lower() in {'true', '1'}
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'your-mandrill-username')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'your-mandrill-password')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'your@default-mail.com')
