from functools import wraps
from flask import request, jsonify
from services.db import decode_token, get_db_connection

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            parts = request.headers['Authorization'].split()
            if len(parts) == 2 and parts[0] == 'Bearer':
                token = parts[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = decode_token(token)
            current_user = data['username']
        except Exception:
            return jsonify({'message': 'Invalid or expired token!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

def get_user_access(username):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT access FROM users WHERE username = ?", username)
        row = cursor.fetchone()
    return row[0] if row else None
