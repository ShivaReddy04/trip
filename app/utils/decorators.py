from functools import wraps
from flask import session, jsonify, redirect, url_for, request, flash
from app.models.user import find_user_by_id


def _wants_json():
    """Return True if the request expects a JSON response."""
    return (
        request.is_json
        or request.content_type == 'application/json'
        or 'application/json' in (request.accept_mimetypes or '')
        or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    )


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        uid = session.get('user_id')
        if not uid:
            if request.path.startswith('/api/') or _wants_json():
                return jsonify({'error': 'Authentication required'}), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.full_path))
        return f(*args, **kwargs)
    return decorated


def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            uid = session.get('user_id')
            if not uid:
                if request.path.startswith('/api/') or _wants_json():
                    return jsonify({'error': 'Authentication required'}), 401
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            user = find_user_by_id(uid)
            if not user or user.role not in roles:
                if request.path.startswith('/api/') or _wants_json():
                    return jsonify({'error': 'Insufficient permissions'}), 403
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated
    return decorator


def vendor_required(f):
    @wraps(f)
    @roles_required('vendor', 'admin')
    def decorated(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    @roles_required('admin')
    def decorated(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated
