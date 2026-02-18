from app.models.user import find_user_by_id, update_user, verify_password, change_password


def get_profile(user_id):
    return find_user_by_id(user_id)


def update_profile(user_id, data):
    update_data = {}
    if 'firstName' in data:
        update_data['profile.firstName'] = data['firstName']
    if 'lastName' in data:
        update_data['profile.lastName'] = data['lastName']
    if 'phone' in data:
        update_data['profile.phone'] = data['phone']
    if 'street' in data:
        update_data['profile.address.street'] = data['street']
    if 'city' in data:
        update_data['profile.address.city'] = data['city']
    if 'state' in data:
        update_data['profile.address.state'] = data['state']
    if 'country' in data:
        update_data['profile.address.country'] = data['country']
    if 'zipCode' in data:
        update_data['profile.address.zipCode'] = data['zipCode']
    if 'currency' in data:
        update_data['preferences.currency'] = data['currency']
    if 'language' in data:
        update_data['preferences.language'] = data['language']
    if 'notifications' in data:
        update_data['preferences.notifications'] = data['notifications'] == 'on'
    if update_data:
        return update_user(user_id, update_data)
    return find_user_by_id(user_id)


def change_user_password(user_id, current_password, new_password):
    user = find_user_by_id(user_id)
    if not verify_password(current_password, user.password):
        return 'Current password is incorrect.'
    change_password(user_id, new_password)
    return None
