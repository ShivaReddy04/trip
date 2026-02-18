from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm.attributes import flag_modified
from app.extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='traveler')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # JSON columns for nested data
    profile = db.Column(db.JSON, default=dict)
    preferences = db.Column(db.JSON, default=dict)
    vendor = db.Column(db.JSON, nullable=True)

    # Relationships
    packages = db.relationship('Package', backref='owner', lazy='dynamic', foreign_keys='Package.vendor_id')
    bookings = db.relationship('Booking', backref='user', lazy='dynamic', foreign_keys='Booking.user_id')
    reviews = db.relationship('Review', backref='author', lazy='dynamic', foreign_keys='Review.user_id')

    # CamelCase aliases for template compatibility
    @property
    def _id(self):
        return self.id

    @property
    def isActive(self):
        return self.is_active

    @property
    def createdAt(self):
        return self.created_at

    def get(self, key, default=None):
        """Dict-like .get() for backward compatibility."""
        return getattr(self, key, default)

    def __getitem__(self, key):
        """Dict-like bracket access for backward compatibility."""
        return getattr(self, key)

    def __contains__(self, key):
        return hasattr(self, key)

    def __repr__(self):
        return f'<User {self.email}>'


# ---------------------------------------------------------------------------
# Wrapper functions (same signatures as before)
# ---------------------------------------------------------------------------

def create_user(data):
    user = User(
        email=data['email'].lower().strip(),
        password=generate_password_hash(data['password']),
        role=data.get('role', 'traveler'),
        profile={
            'firstName': data['profile']['firstName'],
            'lastName': data['profile']['lastName'],
            'phone': data['profile'].get('phone', ''),
            'avatar': '',
            'address': {'street': '', 'city': '', 'state': '', 'country': '', 'zipCode': ''},
        },
        preferences={'currency': 'USD', 'language': 'en', 'notifications': True},
        is_active=True,
    )
    if data.get('role') == 'vendor' and data.get('vendor'):
        user.vendor = {
            'companyName': data['vendor']['companyName'],
            'description': data['vendor'].get('description', ''),
            'logo': '', 'verified': False, 'documents': [], 'bankDetails': None,
        }
    db.session.add(user)
    db.session.commit()
    return user


def find_user_by_email(email):
    email = email.lower().strip()
    return User.query.filter_by(email=email).first()


def find_user_by_id(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (ValueError, TypeError):
        return None


def update_user(user_id, update_data):
    user = find_user_by_id(user_id)
    if not user:
        return None
    json_cols_touched = set()
    for key, val in update_data.items():
        parts = key.split('.')
        if len(parts) == 1:
            setattr(user, key, val)
        else:
            # Nested update into a JSON column
            col_name = parts[0]
            obj = getattr(user, col_name)
            if obj is None:
                obj = {}
                setattr(user, col_name, obj)
            for p in parts[1:-1]:
                obj = obj.setdefault(p, {})
            obj[parts[-1]] = val
            json_cols_touched.add(col_name)
    for col in json_cols_touched:
        flag_modified(user, col)
    db.session.commit()
    return user


def verify_password(plain_password, stored_password):
    return check_password_hash(stored_password, plain_password)


def change_password(user_id, new_password):
    user = find_user_by_id(user_id)
    if user:
        user.password = generate_password_hash(new_password)
        db.session.commit()
