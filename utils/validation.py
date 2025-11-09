"""
Utility functions for simple request JSON validation.
"""

from flask import request, jsonify

def require_json_fields(*fields):
    """
    Decorator to ensure that the incoming request JSON contains the specified fields.
    Returns a 400 response if validation fails.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return jsonify({"success": False, "error": "Invalid JSON"}), 400
            data = request.get_json()
            missing = [f for f in fields if f not in data or data[f] in (None, "", [])]
            if missing:
                return jsonify({"success": False, "error": f"Missing required fields: {', '.join(missing)}"}), 400
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator