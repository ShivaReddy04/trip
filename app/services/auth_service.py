from app.models.user import create_user, find_user_by_email, verify_password


def register_user(data):
    existing = find_user_by_email(data['email'])
    if existing:
        return None, 'Email already registered.'
    user = create_user(data)
    return user, None


def login_user(email, password):
    user = find_user_by_email(email)
    if not user:
        return None, 'Invalid email or password.'
    if not user.is_active:
        return None, 'Account is deactivated.'
    if not verify_password(password, user.password):
        return None, 'Invalid email or password.'
    return user, None
