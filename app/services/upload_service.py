# Upload service - Demo mode (no external storage)


def upload_image(file, folder='trip-planner'):
    """Demo: return placeholder image URL."""
    return {
        'url': 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800',
        'publicId': 'demo-image',
        'demo': True,
    }


def upload_images(files, folder='trip-planner'):
    """Demo: return placeholder URLs."""
    results = []
    for i, f in enumerate(files[:10]):
        results.append({
            'url': f'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&sig={i}',
            'publicId': f'demo-image-{i}',
        })
    return results


def delete_upload(public_id):
    """Demo: always succeed."""
    return True
