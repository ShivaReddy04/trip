from datetime import datetime, date
from flask.json.provider import DefaultJSONProvider


class SafeJSONProvider(DefaultJSONProvider):
    """JSON provider that serializes datetime objects to ISO format."""

    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


def format_currency(amount, currency='USD'):
    symbols = {'USD': '$', 'EUR': '€', 'GBP': '£', 'INR': '₹'}
    symbol = symbols.get(currency, currency + ' ')
    return f'{symbol}{amount:,.2f}'


def format_date(dt):
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except (ValueError, TypeError):
            return dt
    if isinstance(dt, datetime):
        return dt.strftime('%b %d, %Y')
    return str(dt)


def truncate(text, length=100):
    if not text:
        return ''
    if len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + '...'


def paginate_args(request):
    """Extract page and limit from request args."""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    page = max(1, page)
    limit = min(max(1, limit), 100)
    return page, limit


def serialize_doc(doc):
    """Convert a document (dict or ORM instance) to JSON-safe dict."""
    if doc is None:
        return None

    # Handle ORM model instances
    from app.extensions import db
    if isinstance(doc, db.Model):
        result = {}
        for col in doc.__table__.columns:
            val = getattr(doc, col.name)
            if isinstance(val, (datetime, date)):
                val = val.isoformat()
            result[col.name] = val
        # Add camelCase aliases for ID fields
        if 'id' in result:
            result['_id'] = str(result['id'])
        for key in ('vendor_id', 'user_id', 'package_id', 'booking_id'):
            if key in result and result[key] is not None:
                # Also add camelCase version
                camel = key.split('_')
                camel_key = camel[0] + ''.join(w.capitalize() for w in camel[1:])
                result[camel_key] = str(result[key])
                result[key] = str(result[key])
        # Include special properties
        if hasattr(doc, 'input') and hasattr(doc, 'input_data'):
            result['input'] = doc.input_data
        if hasattr(doc, 'generated_itinerary'):
            result['generatedItinerary'] = doc.generated_itinerary
        if hasattr(doc, 'rush_hour_predictions'):
            result['rushHourPredictions'] = doc.rush_hour_predictions
        if hasattr(doc, 'travel_dates'):
            result['travelDates'] = doc.travel_dates
        if hasattr(doc, 'total_amount'):
            result['totalAmount'] = doc.total_amount
        if hasattr(doc, 'helpful_count'):
            result['helpfulCount'] = doc.helpful_count
        if hasattr(doc, 'vendor_reply'):
            result['vendorReply'] = doc.vendor_reply
        if hasattr(doc, 'helpful_by'):
            result['helpfulBy'] = doc.helpful_by
        if hasattr(doc, 'saved_as_package'):
            result['savedAsPackage'] = doc.saved_as_package
        return result

    # Handle plain dicts (backward compat)
    doc = dict(doc)
    for key in ('_id', 'vendorId', 'userId', 'packageId', 'bookingId'):
        if key in doc and not isinstance(doc[key], str):
            doc[key] = str(doc[key])
    return doc
