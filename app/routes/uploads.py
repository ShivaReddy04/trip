from flask import Blueprint, request, jsonify
from app.utils.decorators import login_required

uploads_bp = Blueprint('uploads', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _validate_file(file):
    """Return an error string or None if valid."""
    if not file or not file.filename:
        return 'Empty file.'
    if not _allowed_file(file.filename):
        return f'File "{file.filename}" has an unsupported type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}.'
    # Check size by reading into memory (werkzeug doesn't expose content-length per part)
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > MAX_FILE_SIZE:
        return f'File "{file.filename}" exceeds the 5 MB size limit.'
    return None


@uploads_bp.route('/image', methods=['POST'])
@login_required
def upload_single():
    file = request.files.get('image')
    if not file:
        return jsonify({'error': 'No image provided'}), 400

    err = _validate_file(file)
    if err:
        return jsonify({'error': err}), 400

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
    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': 'No images provided'}), 400

    errors = []
    valid_files = []
    for f in files[:10]:
        err = _validate_file(f)
        if err:
            errors.append(err)
        else:
            valid_files.append(f)

    if not valid_files:
        return jsonify({'error': ' '.join(errors)}), 400

    # Demo mode: return placeholder URLs
    results = []
    for i, f in enumerate(valid_files):
        results.append({
            'url': f'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&sig={i}',
            'publicId': f'demo-image-{i}',
        })

    resp = {'images': results, 'demo': True}
    if errors:
        resp['warnings'] = errors

    return jsonify(resp), 201


@uploads_bp.route('/<public_id>', methods=['DELETE'])
@login_required
def delete(public_id):
    return jsonify({'message': 'Deleted successfully (demo mode)', 'demo': True})
