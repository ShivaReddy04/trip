from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services.auth_service import register_user, login_user
from app.utils.validators import validate_email_address, validate_password, validate_redirect_url

auth_bp = Blueprint('auth', __name__, template_folder='../templates')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')

    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')

    if not email or not password:
        flash('Please enter email and password.', 'danger')
        return render_template('auth/login.html'), 400

    user, error = login_user(email, password)
    if error:
        flash(error, 'danger')
        return render_template('auth/login.html'), 401

    session.permanent = True
    session['user_id'] = user.id
    flash(f'Welcome back, {user.profile["firstName"]}!', 'success')
    next_url = validate_redirect_url(request.args.get('next'))
    if next_url:
        return redirect(next_url)
    if user.role == 'vendor':
        return redirect(url_for('vendor.dashboard'))
    return redirect(url_for('home'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('auth/register.html')

    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirmPassword', '')
    first_name = request.form.get('firstName', '').strip()
    last_name = request.form.get('lastName', '').strip()
    role = request.form.get('role', 'traveler')
    company_name = request.form.get('companyName', '').strip()

    errors = []
    normalized_email, email_error = validate_email_address(email)
    if email_error:
        errors.append(email_error)
    password_error = validate_password(password)
    if password_error:
        errors.append(password_error)
    if password != confirm_password:
        errors.append('Passwords do not match.')
    if not first_name:
        errors.append('First name is required.')
    if not last_name:
        errors.append('Last name is required.')
    if role == 'vendor' and not company_name:
        errors.append('Company name is required for vendor accounts.')

    if errors:
        for e in errors:
            flash(e, 'danger')
        return render_template('auth/register.html'), 400

    data = {
        'email': normalized_email or email,
        'password': password,
        'role': role,
        'profile': {'firstName': first_name, 'lastName': last_name},
    }
    if role == 'vendor':
        data['vendor'] = {'companyName': company_name}

    user, error = register_user(data)
    if error:
        flash(error, 'danger')
        return render_template('auth/register.html'), 409

    session.permanent = True
    session['user_id'] = user.id
    flash('Account created successfully! Welcome to TripPlanner.', 'success')
    if role == 'vendor':
        return redirect(url_for('vendor.dashboard'))
    return redirect(url_for('home'))


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template('auth/forgot_password.html')
    flash('If an account with that email exists, a reset link has been sent.', 'info')
    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'GET':
        return render_template('auth/reset_password.html')
    flash('Password has been reset successfully.', 'success')
    return redirect(url_for('auth.login'))
