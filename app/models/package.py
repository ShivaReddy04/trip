from datetime import datetime, timezone
from slugify import slugify
from sqlalchemy.orm.attributes import flag_modified
from app.extensions import db
from app.utils.validators import safe_int, safe_float


class Package(db.Model):
    __tablename__ = 'packages'

    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(300), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    difficulty = db.Column(db.String(30), default='moderate')
    status = db.Column(db.String(20), default='draft', index=True)
    featured = db.Column(db.Boolean, default=False)
    rating_average = db.Column(db.Float, default=0)
    rating_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # JSON columns
    pricing = db.Column(db.JSON, default=dict)
    availability = db.Column(db.JSON, default=dict)
    duration = db.Column(db.JSON, default=dict)
    highlights = db.Column(db.JSON, default=list)
    inclusions = db.Column(db.JSON, default=list)
    exclusions = db.Column(db.JSON, default=list)
    images = db.Column(db.JSON, default=list)
    videos = db.Column(db.JSON, default=list)
    destinations = db.Column(db.JSON, default=list)
    itinerary = db.Column(db.JSON, default=list)
    tags = db.Column(db.JSON, default=list)

    # Relationships
    bookings = db.relationship('Booking', backref='package', lazy='dynamic', foreign_keys='Booking.package_id')
    reviews = db.relationship('Review', backref='package', lazy='dynamic', foreign_keys='Review.package_id')

    # CamelCase aliases
    @property
    def _id(self):
        return self.id

    @property
    def vendorId(self):
        return self.vendor_id

    @property
    def createdAt(self):
        return self.created_at

    @property
    def rating(self):
        return {'average': self.rating_average, 'count': self.rating_count}

    def get(self, key, default=None):
        return getattr(self, key, default)

    def __getitem__(self, key):
        return getattr(self, key)

    def __contains__(self, key):
        return hasattr(self, key)

    def __repr__(self):
        return f'<Package {self.title}>'


# ---------------------------------------------------------------------------
# Wrapper functions
# ---------------------------------------------------------------------------

def create_package(vendor_id, data):
    slug_val = slugify(data['title']) + '-' + str(int(datetime.now(timezone.utc).timestamp()))
    try:
        vid = int(vendor_id)
    except (ValueError, TypeError):
        vid = vendor_id

    pkg = Package(
        vendor_id=vid,
        title=data['title'],
        slug=slug_val,
        description=data['description'],
        highlights=data.get('highlights', []),
        category=data['category'],
        destinations=data.get('destinations', []),
        itinerary=data.get('itinerary', []),
        pricing={
            'basePrice': safe_float(data['pricing']['basePrice'], default=0, min_val=0),
            'currency': data['pricing'].get('currency', 'USD'),
            'perPersonPrice': data['pricing'].get('perPersonPrice', True),
            'groupDiscounts': data['pricing'].get('groupDiscounts', []),
            'seasonalPricing': data['pricing'].get('seasonalPricing', []),
        },
        inclusions=data.get('inclusions', []),
        exclusions=data.get('exclusions', []),
        images=data.get('images', []),
        videos=[],
        availability={
            'startDate': data['availability']['startDate'],
            'endDate': data['availability']['endDate'],
            'blackoutDates': [],
            'maxGroupSize': safe_int(data['availability']['maxGroupSize'], default=10, min_val=1),
            'minGroupSize': safe_int(data['availability'].get('minGroupSize', 1), default=1, min_val=1),
        },
        duration={
            'days': safe_int(data['duration']['days'], default=1, min_val=1),
            'nights': safe_int(data['duration']['nights'], default=0, min_val=0),
        },
        difficulty=data.get('difficulty', 'moderate'),
        rating_average=0,
        rating_count=0,
        status=data.get('status', 'draft'),
        featured=data.get('featured', False),
        tags=data.get('tags', []),
    )
    db.session.add(pkg)
    db.session.commit()
    return pkg


def find_package_by_slug(slug):
    return Package.query.filter_by(slug=slug).first()


def find_package_by_id(package_id):
    try:
        return db.session.get(Package, int(package_id))
    except (ValueError, TypeError):
        return None


def update_package(package_id, data):
    pkg = find_package_by_id(package_id)
    if not pkg:
        return None
    json_fields = {'pricing', 'availability', 'duration', 'highlights', 'inclusions',
                   'exclusions', 'images', 'videos', 'destinations', 'itinerary', 'tags'}
    for key, val in data.items():
        setattr(pkg, key, val)
        if key in json_fields:
            flag_modified(pkg, key)
    db.session.commit()
    return pkg


def delete_package(package_id):
    pkg = find_package_by_id(package_id)
    if pkg:
        db.session.delete(pkg)
        db.session.commit()


def search_packages(filters, page=1, limit=10, sort_by='createdAt', sort_order='desc'):
    q = Package.query.filter(Package.status == 'published')

    if filters.get('query'):
        search = f"%{filters['query'].lower()}%"
        q = q.filter(Package.title.ilike(search))
    if filters.get('category'):
        q = q.filter(Package.category == filters['category'])
    if filters.get('difficulty'):
        q = q.filter(Package.difficulty == filters['difficulty'])
    if filters.get('featured'):
        q = q.filter(Package.featured == True)
    if filters.get('rating'):
        q = q.filter(Package.rating_average >= float(filters['rating']))

    # JSON column filters — fetch and filter in Python for SQLite compat
    results = q.all()

    if filters.get('minPrice'):
        min_p = float(filters['minPrice'])
        results = [p for p in results if (p.pricing or {}).get('basePrice', 0) >= min_p]
    if filters.get('maxPrice'):
        max_p = float(filters['maxPrice'])
        results = [p for p in results if (p.pricing or {}).get('basePrice', 0) <= max_p]
    if filters.get('duration'):
        dur = int(filters['duration'])
        results = [p for p in results if (p.duration or {}).get('days') == dur]
    if filters.get('destination'):
        d = filters['destination'].lower()
        results = [p for p in results if any(d in dest.get('name', '').lower() for dest in (p.destinations or []))]

    # Sort
    key_map = {
        'price': lambda p: (p.pricing or {}).get('basePrice', 0),
        'rating': lambda p: p.rating_average,
        'duration': lambda p: (p.duration or {}).get('days', 0),
        'createdAt': lambda p: p.created_at or datetime.min.replace(tzinfo=timezone.utc),
    }
    reverse = sort_order == 'desc'
    results.sort(key=key_map.get(sort_by, key_map['createdAt']), reverse=reverse)

    total = len(results)
    start = (page - 1) * limit
    return results[start:start + limit], total


def get_featured_packages(limit=6):
    return Package.query.filter_by(status='published', featured=True).limit(limit).all()


def get_popular_packages(limit=6):
    return Package.query.filter_by(status='published').order_by(Package.rating_average.desc()).limit(limit).all()


def get_vendor_packages(vendor_id, page=1, limit=10):
    try:
        vid = int(vendor_id)
    except (ValueError, TypeError):
        vid = vendor_id
    q = Package.query.filter_by(vendor_id=vid).order_by(Package.created_at.desc())
    total = q.count()
    results = q.offset((page - 1) * limit).limit(limit).all()
    return results, total


def update_package_rating(package_id):
    from app.models.review import Review
    pkg = find_package_by_id(package_id)
    if not pkg:
        return
    reviews = Review.query.filter_by(package_id=pkg.id, status='approved').all()
    if reviews:
        avg = round(sum(r.rating for r in reviews) / len(reviews), 1)
        pkg.rating_average = avg
        pkg.rating_count = len(reviews)
    else:
        pkg.rating_average = 0
        pkg.rating_count = 0
    db.session.commit()
