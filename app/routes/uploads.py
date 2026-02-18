from flask import Blueprint, request, jsonify
from app.utils.decorators import login_required

uploads_bp = Blueprint('uploads', __name__)


@uploads_bp.route('/image', methods=['POST'])
@login_required
def upload_single():
    file = request.files.get('image')
    if not file:
        return jsonify({'error': 'No image provided'}), 400

    # Demo mode: return a placeholder image URL
    return jsonify({
        'url': 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800',
        'publicId': 'demo-image',
        'demo': True,
        'message': 'Image upload is a demo feature.',
    }), 201


@uploads_bp.route('/images', methods=['POST'])
@login_required
def upload_multiple():
    files = request.files.getlist('images')
    if not files:
        return jsonify({'error': 'No images provided'}), 400

    # Demo mode: return placeholder URLs
    results = []
    for i, f in enumerate(files[:10]):
        results.append({
            'url': f'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&sig={i}',
            'publicId': f'demo-image-{i}',
        })

    return jsonify({'images': results, 'demo': True}), 201


@uploads_bp.route('/<public_id>', methods=['DELETE'])
@login_required
def delete(public_id):
    return jsonify({'message': 'Deleted successfully (demo mode)', 'demo': True})
