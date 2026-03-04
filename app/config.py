import os
from datetime import timedelta


class BaseConfig:
    """Common configuration for all environments"""

    # 🔐 Core security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # 🗄️ Database (SQLite default, PostgreSQL via DATABASE_URL)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "trip.db"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 💳 Payment webhook secrets
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')
    RAZORPAY_WEBHOOK_SECRET = os.getenv('RAZORPAY_WEBHOOK_SECRET', '')

    # 🗺️ Google Maps
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')

    # 🍪 Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(BaseConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


# Used in __init__.py
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
