from app.models.package import (
    create_package, find_package_by_slug, find_package_by_id,
    update_package, delete_package, search_packages,
    get_featured_packages, get_popular_packages,
    get_vendor_packages
)


def create_new_package(vendor_id, data):
    """Create a new package. Returns (package, error)."""
    if not data.get('title'):
        return None, 'Title is required.'
    if not data.get('description'):
        return None, 'Description is required.'
    if not data.get('category'):
        return None, 'Category is required.'
    if not data.get('pricing', {}).get('basePrice'):
        return None, 'Base price is required.'
    if not data.get('availability', {}).get('startDate'):
        return None, 'Availability dates are required.'
    if not data.get('duration', {}).get('days'):
        return None, 'Duration is required.'

    package = create_package(vendor_id, data)
    return package, None


def get_package_detail(slug):
    return find_package_by_slug(slug)


def search_all_packages(filters, page=1, limit=10, sort_by='createdAt', sort_order='desc'):
    return search_packages(filters, page, limit, sort_by, sort_order)


def update_existing_package(package_id, vendor_id, data):
    """Update package. Returns (package, error)."""
    package = find_package_by_id(package_id)
    if not package:
        return None, 'Package not found.'
    if str(package.vendor_id) != str(vendor_id):
        return None, 'You can only edit your own packages.'

    update_data = {}
    for field in ['title', 'description', 'highlights', 'category', 'destinations',
                  'itinerary', 'pricing', 'inclusions', 'exclusions', 'images',
                  'videos', 'availability', 'duration', 'difficulty', 'tags',
                  'seoMeta', 'featured']:
        if field in data:
            update_data[field] = data[field]

    if 'title' in update_data:
        from slugify import slugify
        from datetime import datetime, timezone
        update_data['slug'] = slugify(update_data['title']) + '-' + str(int(datetime.now(timezone.utc).timestamp()))

    return update_package(package_id, update_data), None


def update_package_status(package_id, vendor_id, status):
    """Update package status. Returns (package, error)."""
    package = find_package_by_id(package_id)
    if not package:
        return None, 'Package not found.'
    if str(package.vendor_id) != str(vendor_id):
        return None, 'You can only edit your own packages.'
    if status not in ('draft', 'published', 'archived'):
        return None, 'Invalid status.'
    return update_package(package_id, {'status': status}), None


def delete_vendor_package(package_id, vendor_id):
    """Delete package. Returns error or None."""
    package = find_package_by_id(package_id)
    if not package:
        return 'Package not found.'
    if str(package.vendor_id) != str(vendor_id):
        return 'You can only delete your own packages.'
    delete_package(package_id)
    return None
