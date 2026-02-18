from datetime import datetime, timezone
from app.extensions import db


class AiItinerary(db.Model):
    __tablename__ = 'ai_itineraries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    saved_as_package = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # JSON columns
    input_data = db.Column(db.JSON, default=dict)
    generated_itinerary = db.Column(db.JSON, default=dict)
    rush_hour_predictions = db.Column(db.JSON, default=list)

    # CamelCase / compatibility aliases
    @property
    def _id(self):
        return self.id

    @property
    def userId(self):
        return self.user_id

    @property
    def input(self):
        return self.input_data

    @property
    def generatedItinerary(self):
        return self.generated_itinerary

    @property
    def rushHourPredictions(self):
        return self.rush_hour_predictions

    @property
    def savedAsPackage(self):
        return self.saved_as_package

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
        return f'<AiItinerary {self.id}>'


# ---------------------------------------------------------------------------
# Wrapper functions
# ---------------------------------------------------------------------------

def create_ai_itinerary(data):
    try:
        uid = int(data['userId'])
    except (ValueError, TypeError):
        uid = data['userId']

    itinerary = AiItinerary(
        user_id=uid,
        input_data=data.get('input', {}),
        generated_itinerary=data.get('generatedItinerary', {}),
        rush_hour_predictions=data.get('rushHourPredictions', []),
        saved_as_package=False,
    )
    db.session.add(itinerary)
    db.session.commit()
    return itinerary


def get_user_itineraries(user_id, page=1, limit=10):
    try:
        uid = int(user_id)
    except (ValueError, TypeError):
        uid = user_id
    q = AiItinerary.query.filter_by(user_id=uid).order_by(AiItinerary.created_at.desc())
    total = q.count()
    results = q.offset((page - 1) * limit).limit(limit).all()
    return results, total


def find_itinerary_by_id(itinerary_id):
    try:
        return db.session.get(AiItinerary, int(itinerary_id))
    except (ValueError, TypeError):
        return None
