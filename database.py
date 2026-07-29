import sqlite3
import hashlib
import os

# ==========================================
# ១. Function សម្រាប់ Hashing & Verify Password
# ==========================================

def hash_password(password: str) -> str:
    """បំប្លែង Password ដើមទៅជា Hash សម្ងាត់ (ជាមួយ Salt)"""
    salt = os.urandom(16)  # បង្កើត Salt ចែកដាច់ដោយឡែក
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + ':' + hashed.hex()

def verify_password(stored_password: str, provided_password: str) -> bool:
    """ផ្ទៀងផ្ទាត់ Password ដែលអ្នកប្រើប្រាស់វាយ បញ្ចូលជាមួយ Hash ក្នុង Database"""
    try:
        salt_hex, hashed_hex = stored_password.split(':')
        salt = bytes.fromhex(salt_hex)
        hashed = bytes.fromhex(hashed_hex)
        
        new_hashed = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
        return new_hashed == hashed
    except Exception:
        return False


# ==========================================
# ២. Function សម្រាប់គ្រប់គ្រង SQLite Database
# ==========================================

DB_NAME = "users.db"

def init_db():
    """បង្កើត Table ឈ្មោះ 'users' ប្រសិនបើមិនទាន់មាន"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'Staff'
        )
    ''')
    conn.commit()
    conn.close()

def register_user(username, password, role="Staff"):
    """បន្ថែមបុគ្គលិកថ្មីចូល Database (មាន Hash Password)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    hashed_pw = hash_password(password)
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                       (username, hashed_pw, role))
        conn.commit()
        return True, "ចុះឈ្មោះជោគជ័យ!"
    except sqlite3.IntegrityError:
        return False, "Username នេះមានគេប្រើរួចហើយ!"
    finally:
        conn.close()

def check_login_db(username, password):
    """ពិនិត្យមើលការ Login ពី Database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT password, role FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        stored_hash, role = user[0], user[1]
        if verify_password(stored_hash, password):
            return True, role
    return False, None

# បង្កើត Database ស្វ័យប្រវត្តិពេល run file នេះ
init_db()