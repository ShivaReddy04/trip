import os
from flask import Flask
from .config import config_by_name
from .extensions import csrf, cors, db, migrate   # ⭐ added db & migrate


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    from .utils.helpers import SafeJSONProvider

    app = Flask(__name__)
    app.json_provider_class = SafeJSONProvider
    app.json = SafeJSONProvider(app)
    app.config.from_object(config_by_name[config_name])

    # ⭐ Initialize database FIRST
    db.init_app(app)
    migrate.init_app(app, db)

    # Initialize existing extensions
    csrf.init_app(app)
    cors.init_app(app)

    # Exempt webhook endpoints from CSRF
    csrf.exempt('app.routes.payments.stripe_webhook')
    csrf.exempt('app.routes.payments.razorpay_webhook')

    # Template context – inject current_user from session
    @app.context_processor
    def inject_globals():
        from flask import session
        from app.models.user import find_user_by_id
        user = None
        uid = session.get('user_id')
        if uid:
            user = find_user_by_id(uid)
        return dict(
            current_user=user,
            google_maps_api_key=app.config.get('GOOGLE_MAPS_API_KEY', ''),
            stripe_publishable_key=app.config.get('STRIPE_PUBLISHABLE_KEY', ''),
        )

    # ⭐ Import models so migrations can detect them
    from app.models import User, Package, Booking, Review, AiItinerary  # noqa: F401

    # Register Blueprints
    from .routes.auth import auth_bp
    from .routes.users import users_bp
    from .routes.packages import packages_bp
    from .routes.bookings import bookings_bp
    from .routes.payments import payments_bp
    from .routes.reviews import reviews_bp
    from .routes.ai import ai_bp
    csrf.exempt(ai_bp)
    from .routes.maps import maps_bp
    from .routes.uploads import uploads_bp
    from .routes.vendor import vendor_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(packages_bp, url_prefix='/packages')
    app.register_blueprint(bookings_bp, url_prefix='/bookings')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(reviews_bp, url_prefix='/api/reviews')
    app.register_blueprint(ai_bp, url_prefix='/ai')
    app.register_blueprint(maps_bp, url_prefix='/api/maps')
    app.register_blueprint(uploads_bp, url_prefix='/api/uploads')
    app.register_blueprint(vendor_bp, url_prefix='/vendor')

    # Home route — redirect to the appropriate page
    @app.route('/')
    def home():
        from flask import session, redirect, url_for
        from app.models.user import find_user_by_id
        uid = session.get('user_id')
        if uid:
            user = find_user_by_id(uid)
            if user and user.role == 'vendor':
                return redirect(url_for('vendor.dashboard'))
            return redirect(url_for('maps.home_page'))
        return redirect(url_for('auth.login'))

    return app
