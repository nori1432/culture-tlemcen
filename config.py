import os
from dotenv import load_dotenv
from sqlalchemy.pool import NullPool

load_dotenv()

_db_url = os.getenv(
    'DATABASE_URL',
    'mysql+pymysql://root:@localhost:3306/tlemcen_tour'
)

# Aiven (and most cloud MySQL) requires SSL for remote connections.
# We skip CA-certificate verification so no cert file is needed on Vercel.
_connect_args = {}
if 'aivencloud.com' in _db_url:
    _connect_args = {
        'ssl_disabled': False,
        'ssl_verify_cert': False,
        'ssl_verify_identity': False,
    }


class Config:
    # ── Database ──────────────────────────────────────────────────────────
    # Set DATABASE_URL in Vercel env vars.
    # Format: mysql+pymysql://avnadmin:PASSWORD@HOST:PORT/defaultdb
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # NullPool: each serverless invocation opens and closes its own connection.
    SQLALCHEMY_ENGINE_OPTIONS = {
        'poolclass': NullPool,
        'connect_args': _connect_args,
    }

    # ── Security ──────────────────────────────────────────────────────────
    SECRET_KEY = os.getenv('SECRET_KEY', 'tlemcen-smart-tour-secret-2024')

    # ── JSON ──────────────────────────────────────────────────────────────
    JSON_AS_ASCII = False  # Preserve Arabic characters in JSON responses

    # ── Image serving ─────────────────────────────────────────────────────
    # In production (Vercel): set IMAGE_BASE_URL to your Vercel project URL.
    # Example: https://tlemcen-api.vercel.app/images
    # Locally: leave empty — the stored localhost URL is returned as-is.
    IMAGE_BASE_URL = os.getenv('IMAGE_BASE_URL', '')
