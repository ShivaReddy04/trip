from datetime import datetime, timezone
from sqlalchemy.orm.attributes import flag_modified
from app.extensions import db


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('packages.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), default='')
    content = db.Column(db.Text, default='')
    helpful_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='approved')
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # JSON columns
    images = db.Column(db.JSON, default=list)
    vendor_reply = db.Column(db.JSON, nullable=True)
    helpful_by = db.Column(db.JSON, default=list)  # list, not set

    # CamelCase aliases
    @property
    def _id(self):
        return self.id

    @property
    def packageId(self):
        return self.package_id

    @property
    def userId(self):
        return self.user_id

    @property
    def bookingId(self):
        return self.booking_id

    @property
    def helpfulCount(self):
        return self.helpful_count

    @property
    def vendorReply(self):
        return self.vendor_reply

    @property
    def createdAt(self):
        return self.created_at

    def get(self, key, default=None):
        return getattr(self, key, default)

    def __getitem__(self, key):
        return getattr(self, key)

    def __contains__(self, key):
        return hasattr(self, key)

    def __repr__(self):
        return f'<Review {self.id} rating={self.rating}>'


# ---------------------------------------------------------------------------
# Wrapper functions
# ---------------------------------------------------------------------------

def create_review(data):
    try:
        pkg_id = int(data['packageId'])
    except (ValueError, TypeError):
        pkg_id = data['packageId']
    try:
        uid = int(data['userId'])
    except (ValueError, TypeError):
        uid = data['userId']
    try:
        bid = int(data['bookingId'])
    except (ValueError, TypeError):
        bid = data['bookingId']

    review = Review(
        package_id=pkg_id,
        user_id=uid,
        booking_id=bid,
        rating=int(data['rating']),
        title=data.get('title', ''),
        content=data.get('content', ''),
        images=data.get('images', []),
        helpful_count=0,
        helpful_by=[],
        vendor_reply=None,
        status='approved',
    )
    db.session.add(review)
    db.session.commit()
    return review


def find_review_by_id(review_id):
    try:
        return db.session.get(Review, int(review_id))
    except (ValueError, TypeError):
        return None


def get_package_reviews(package_id, page=1, limit=10):
    try:
        pid = int(package_id)
    except (ValueError, TypeError):
        pid = package_id
    q = Review.query.filter_by(package_id=pid, status='approved').order_by(Review.created_at.desc())
    total = q.count()
    results = q.offset((page - 1) * limit).limit(limit).all()
    return results, total


def get_user_reviews(user_id, page=1, limit=10):
    try:
        uid = int(user_id)
    except (ValueError, TypeError):
        uid = user_id
    q = Review.query.filter_by(user_id=uid).order_by(Review.created_at.desc())
    total = q.count()
    results = q.offset((page - 1) * limit).limit(limit).all()
    return results, total


def add_vendor_reply(review_id, content):
    r = find_review_by_id(review_id)
    if r:
        r.vendor_reply = {'content': content, 'repliedAt': datetime.now(timezone.utc).isoformat()}
        flag_modified(r, 'vendor_reply')
        db.session.commit()
    return r


def mark_helpful(review_id, user_id):
    r = find_review_by_id(review_id)
    if not r:
        return None, 'Review not found.'
    helpful = r.helpful_by or []
    # Convert user_id for comparison
    uid_str = str(user_id)
    uid_int = None
    try:
        uid_int = int(user_id)
    except (ValueError, TypeError):
        pass
    if uid_str in [str(x) for x in helpful]:
        return None, 'You have already marked this review as helpful.'
    helpful.append(uid_int if uid_int is not None else user_id)
    r.helpful_by = helpful
    r.helpful_count = len(helpful)
    flag_modified(r, 'helpful_by')
    db.session.commit()
    return r, None


def get_rating_summary(package_id):
    try:
        pid = int(package_id)
    except (ValueError, TypeError):
        pid = package_id
    reviews = Review.query.filter_by(package_id=pid, status='approved').all()
    distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for r in reviews:
        distribution[r.rating] = distribution.get(r.rating, 0) + 1
    total = len(reviews)
    rating_sum = sum(r.rating for r in reviews)
    average = round(rating_sum / total, 1) if total > 0 else 0
    return {'average': average, 'total': total, 'distribution': distribution}


def check_existing_review(user_id, booking_id):
    try:
        uid = int(user_id)
    except (ValueError, TypeError):
        uid = user_id
    try:
        bid = int(booking_id)
    except (ValueError, TypeError):
        bid = booking_id
    return Review.query.filter_by(user_id=uid, booking_id=bid).first()
