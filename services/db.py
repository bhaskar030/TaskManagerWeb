import os
import pyodbc
import bcrypt
import jwt
from datetime import datetime, timedelta
from flask import current_app

def get_db_connection():
    conn_str = os.getenv("CUSTOMCONNSTR")
    if not conn_str:
        raise ValueError("Database connection string not found.")
    return pyodbc.connect(conn_str)

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def generate_token(username):
    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=2)
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def decode_token(token):
    return jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
