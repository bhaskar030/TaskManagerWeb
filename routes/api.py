from flask import Blueprint, request, jsonify
from services.auth import token_required, get_user_access
from services.users import (
    authenticate_user, fetch_all_users,
    create_new_user, delete_existing_user,
    update_user_access, change_user_password
)

api = Blueprint('api', __name__)

@api.route('/login', methods=['POST'])
def login():
    data = request.json
    user, error = authenticate_user(data.get('username'), data.get('password'))
    if user:
        return jsonify(user)
    return jsonify({"message": error}), 401

@api.route('/users', methods=['GET'])
@token_required
def get_users(current_user):
    if get_user_access(current_user) != 'Admin':
        return jsonify({'message': 'Admin access required'}), 403
    return jsonify(fetch_all_users())

@api.route('/users', methods=['POST'])
@token_required
def create_user(current_user):
    if get_user_access(current_user) != 'Admin':
        return jsonify({'message': 'Admin access required'}), 403
    data = request.json
    success, message = create_new_user(data.get('username'), data.get('password'), data.get('access'))
    return (jsonify({'message': message}), 201) if success else (jsonify({'message': message}), 400)

@api.route('/users/<username>', methods=['DELETE'])
@token_required
def delete_user(current_user, username):
    if get_user_access(current_user) != 'Admin':
        return jsonify({'message': 'Admin access required'}), 403
    success, message = delete_existing_user(current_user, username)
    return (jsonify({'message': message}), 200) if success else (jsonify({'message': message}), 400)

@api.route('/users/<username>/access', methods=['PUT'])
@token_required
def change_access(current_user, username):
    if get_user_access(current_user) != 'Admin':
        return jsonify({'message': 'Admin access required'}), 403
    new_access = request.json.get('access')
    success, message = update_user_access(username, new_access)
    return (jsonify({'message': message}), 200) if success else (jsonify({'message': message}), 400)

@api.route('/users/<username>/password', methods=['PUT'])
@token_required
def change_password(current_user, username):
    data = request.json
    success, message = change_user_password(username, current_user, data.get('current_password'), data.get('new_password'))
    return (jsonify({'message': message}), 200) if success else (jsonify({'message': message}), 400)
