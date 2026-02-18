import re
from urllib.parse import urlparse


def validate_redirect_url(url):
    """Return the URL only if it is a safe, local path. Otherwise return None."""
    if not url:
        return None
    parsed = urlparse(url)
    # Reject absolute URLs with a scheme or netloc (e.g. https://evil.com)
    # Also reject protocol-relative URLs (//evil.com)
    if parsed.scheme or parsed.netloc or url.startswith('//'):
        return None
    return url


def validate_email_address(email):
    """Simple email validation using regex."""
    if not email:
        return None, 'Email is required.'
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return email.lower().strip(), None
    return None, 'Please enter a valid email address.'


def validate_password(password):
    if len(password) < 8:
        return 'Password must be at least 8 characters long.'
    return None


def validate_required(data, fields):
    """Check that all required fields are present and non-empty."""
    errors = []
    for field in fields:
        if field not in data or not data[field]:
            errors.append(f'{field} is required.')
    return errors


def safe_int(value, default=0, min_val=None, max_val=None):
    """Convert value to int safely, returning default on failure."""
    try:
        result = int(value)
    except (ValueError, TypeError):
        return default
    if min_val is not None:
        result = max(result, min_val)
    if max_val is not None:
        result = min(result, max_val)
    return result


def safe_float(value, default=0.0, min_val=None):
    """Convert value to float safely, returning default on failure."""
    try:
        result = float(value)
    except (ValueError, TypeError):
        return default
    if min_val is not None:
        result = max(result, min_val)
    return result


def validate_rating(rating):
    try:
        rating = int(rating)
        if 1 <= rating <= 5:
            return rating, None
        return None, 'Rating must be between 1 and 5.'
    except (ValueError, TypeError):
        return None, 'Rating must be a number.'
