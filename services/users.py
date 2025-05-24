from services.db import get_db_connection, hash_password, verify_password, generate_token

def authenticate_user(username, password):
    if not username or not password:
        return None, "Username and password required"
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash, access FROM users WHERE username = ?", username)
        row = cursor.fetchone()

    if row and verify_password(password, row[0]):
        token = generate_token(username)
        return {"token": token, "access": row[1]}, None
    return None, "Invalid credentials"

def fetch_all_users():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, access FROM users")
        return [{"id": row[0], "username": row[1], "access": row[2]} for row in cursor.fetchall()]

def create_new_user(username, password, access):
    if not username or not password or access not in ['User', 'Admin']:
        return False, "Username, password, and valid access required"
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", username)
        if cursor.fetchone()[0] > 0:
            return False, "User already exists"
        password_hash = hash_password(password)
        cursor.execute("INSERT INTO users (username, password_hash, access) VALUES (?, ?, ?)",
                       username, password_hash, access)
        conn.commit()
    return True, f"User {username} created"

def delete_existing_user(requesting_user, target_user):
    if requesting_user == target_user:
        return False, "You cannot delete yourself"
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", target_user)
        if cursor.fetchone()[0] == 0:
            return False, "User not found"
        cursor.execute("DELETE FROM users WHERE username = ?", target_user)
        conn.commit()
    return True, f"User {target_user} deleted"

def update_user_access(username, new_access):
    if new_access not in ['User', 'Admin']:
        return False, "Access must be 'User' or 'Admin'"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET access = ? WHERE username = ?", new_access, username)
        conn.commit()
    return True, f"{username} is now {new_access}"

def change_user_password(username, current_user, old_pw, new_pw):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username = ?", username)
        row = cursor.fetchone()
        if not row:
            return False, "User not found"
        if current_user == username and not verify_password(old_pw, row[0]):
            return False, "Old password incorrect"
        new_hash = hash_password(new_pw)
        cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", new_hash, username)
        conn.commit()
    return True, "Password updated"
