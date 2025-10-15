from flask import Blueprint, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/health')
def health_check():
    """Health check endpoint to confirm the service is running."""
    return jsonify({
        "status": "ok",
        "service": "{{ project_name }}",
        "version": "{{ version }}"
    })
