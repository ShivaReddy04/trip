from datetime import datetime, timezone
import uuid
from sqlalchemy.orm.attributes import flag_modified
from app.extensions import db


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    package_id = db.Column(db.Integer, db.ForeignKey('packages.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    status = db.Column(db.String(20), default='pending', index=True)
    total_amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='USD')
    special_requests = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # JSON columns
    travelers = db.Column(db.JSON, default=list)
    travel_dates = db.Column(db.JSON, default=dict)
    payment = db.Column(db.JSON, default=dict)
    cancellation = db.Column(db.JSON, nullable=True)

    # Relationships
    reviews = db.relationship('Review', backref='booking', lazy='dynamic', foreign_keys='Review.booking_id')

    # CamelCase aliases
    @property
    def _id(self):
        return self.id

    @property
    def bookingId(self):
        return self.booking_id

    @property
    def packageId(self):
        return self.package_id

    @property
    def userId(self):
        return self.user_id

    @property
    def vendorId(self):
        return self.vendor_id

    @property
    def totalAmount(self):
        return self.total_amount

    @property
    def travelDates(self):
        return self.travel_dates

    @property
    def specialRequests(self):
        return self.special_requests

    @property
    def createdAt(self):
        return self.created_at

    @property
    def updatedAt(self):
        return self.updated_at

    def get(self, key, default=None):
        return getattr(self, key, default)

    def __getitem__(self, key):
        return getattr(self, key)

    def __contains__(self, key):
        return hasattr(self, key)

    def __repr__(self):
        return f'<Booking {self.booking_id}>'


# ---------------------------------------------------------------------------
# Wrapper functions
# ---------------------------------------------------------------------------

def generate_booking_id():
    year = datetime.now(timezone.utc).year
    short = uuid.uuid4().hex[:8].upper()
    return f'TRP-{year}-{short}'


def create_booking(data):
    try:
        pkg_id = int(data['packageId'])
    except (ValueError, TypeError):
        pkg_id = data['packageId']
    try:
        uid = int(data['userId'])
    except (ValueError, TypeError):
        uid = data['userId']
    try:
        vid = int(data['vendorId'])
    except (ValueError, TypeError):
        vid = data['vendorId']

    booking = Booking(
        booking_id=generate_booking_id(),
        package_id=pkg_id,
        user_id=uid,
        vendor_id=vid,
        travelers=data['travelers'],
        travel_dates={'start': data['travelDates']['start'], 'end': data['travelDates']['end']},
        total_amount=float(data['totalAmount']),
        currency=data.get('currency', 'USD'),
        payment={'status': 'pending', 'method': None, 'transactionId': None, 'paidAmount': 0, 'refundAmount': 0, 'history': []},
        status='pending',
        special_requests=data.get('specialRequests', ''),
        cancellation=None,
    )
    db.session.add(booking)
    db.session.commit()
    return booking


def find_booking_by_id(booking_id):
    try:
        return db.session.get(Booking, int(booking_id))
    except (ValueError, TypeError):
        return None


def get_user_bookings(user_id, status=None, page=1, limit=10):
    try:
        uid = int(user_id)
    except (ValueError, TypeError):
        uid = user_id
    q = Booking.query.filter_by(user_id=uid)
    if status:
        q = q.filter_by(status=status)
    q = q.order_by(Booking.created_at.desc())
    total = q.count()
    results = q.offset((page - 1) * limit).limit(limit).all()
    return results, total


def get_vendor_bookings(vendor_id, status=None, page=1, limit=10):
    try:
        vid = int(vendor_id)
    except (ValueError, TypeError):
        vid = vendor_id
    q = Booking.query.filter_by(vendor_id=vid)
    if status:
        q = q.filter_by(status=status)
    q = q.order_by(Booking.created_at.desc())
    total = q.count()
    results = q.offset((page - 1) * limit).limit(limit).all()
    return results, total


def update_booking(booking_id, data):
    b = find_booking_by_id(booking_id)
    if not b:
        return None
    json_fields = {'travelers', 'travel_dates', 'payment', 'cancellation'}
    for key, val in data.items():
        setattr(b, key, val)
        if key in json_fields:
            flag_modified(b, key)
    b.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return b


def cancel_booking(booking_id, reason=''):
    b = find_booking_by_id(booking_id)
    if b:
        b.status = 'cancelled'
        b.cancellation = {
            'reason': reason,
            'requestedAt': datetime.now(timezone.utc).isoformat(),
            'processedAt': None,
            'refundStatus': 'pending',
        }
        b.updated_at = datetime.now(timezone.utc)
        flag_modified(b, 'cancellation')
        db.session.commit()
    return b


def confirm_booking(booking_id):
    return update_booking(booking_id, {'status': 'confirmed'})


def complete_booking(booking_id):
    return update_booking(booking_id, {'status': 'completed'})


def get_vendor_stats(vendor_id):
    try:
        vid = int(vendor_id)
    except (ValueError, TypeError):
        vid = vendor_id
    bookings = Booking.query.filter_by(vendor_id=vid).all()
    stats = {'total': 0, 'pending': 0, 'confirmed': 0, 'completed': 0, 'cancelled': 0, 'totalRevenue': 0}
    for b in bookings:
        stats['total'] += 1
        stats[b.status] = stats.get(b.status, 0) + 1
        if b.status in ('confirmed', 'completed'):
            stats['totalRevenue'] += (b.payment or {}).get('paidAmount', 0)
    return stats


def calculate_total_amount(package, traveler_count, travel_start=None):
    pricing = package.pricing or {}
    base = pricing.get('basePrice', 0)
    total = base * traveler_count if pricing.get('perPersonPrice', True) else base
    discounts = sorted(pricing.get('groupDiscounts', []), key=lambda d: d.get('minSize', 0), reverse=True)
    for disc in discounts:
        if traveler_count >= disc.get('minSize', 0):
            total *= (1 - disc.get('discount', 0) / 100)
            break
    return round(total, 2)
