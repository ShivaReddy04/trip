from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services.user_service import get_profile, update_profile, change_user_password
from app.utils.decorators import login_required

users_bp = Blueprint('users', __name__, template_folder='../templates')


@users_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    user = get_profile(session['user_id'])
    return render_template('pages/profile.html', user=user)


@users_bp.route('/profile', methods=['POST'])
@login_required
def update_profile_route():
    data = {
        'firstName': request.form.get('firstName', ''),
        'lastName': request.form.get('lastName', ''),
        'phone': request.form.get('phone', ''),
        'street': request.form.get('street', ''),
        'city': request.form.get('city', ''),
        'state': request.form.get('state', ''),
        'country': request.form.get('country', ''),
        'zipCode': request.form.get('zipCode', ''),
        'currency': request.form.get('currency', 'USD'),
        'language': request.form.get('language', 'en'),
        'notifications': request.form.get('notifications', ''),
    }
    update_profile(session['user_id'], data)
    flash('Profile updated successfully.', 'success')
    return redirect(url_for('users.profile'))


@users_bp.route('/profile/avatar', methods=['POST'])
@login_required
def upload_avatar():
    flash('Avatar upload is a demo feature.', 'info')
    return redirect(url_for('users.profile'))


@users_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    current = request.form.get('currentPassword', '')
    new = request.form.get('newPassword', '')
    confirm = request.form.get('confirmPassword', '')

    if not current or not new:
        flash('All fields are required.', 'danger')
        return redirect(url_for('users.profile'))
    if new != confirm:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('users.profile'))
    if len(new) < 8:
        flash('Password must be at least 8 characters.', 'danger')
        return redirect(url_for('users.profile'))

    error = change_user_password(session['user_id'], current, new)
    if error:
        flash(error, 'danger')
    else:
        flash('Password changed successfully.', 'success')
    return redirect(url_for('users.profile'))
