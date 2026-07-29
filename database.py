import psycopg2
import hashlib
import os

# 🔗 ដាក់ Connection String របស់ Supabase ត្រង់នេះ
DB_URL = "postgresql://postgres:[YOUR-PASSWORD]@db.pzpqxgkwtfzgquwwlvdj.supabase.co:5432/postgres"

def get_connection():
    return psycopg2.connect(DB_URL)

# --- Function Hashing Password ---
def hash_password(password: str) -> str:
    salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + ':' + hashed.hex()

def verify_password(stored_password: str, provided_password: str) -> bool:
    try:
        salt_hex, hashed_hex = stored_password.split(':')
        salt = bytes.fromhex(salt_hex)
        hashed = bytes.fromhex(hashed_hex)
        new_hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return new_hashed == hashed
    except Exception:
        return False

# --- បង្កើត Table ក្នុង PostgreSQL ---
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role VARCHAR(20) DEFAULT 'Staff'
        );
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# --- ចុះឈ្មោះបុគ្គលិក ---
def register_user(username, password, role="Staff"):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        hashed_pw = hash_password(password)
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s);", 
                       (username, hashed_pw, role))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "ចុះឈ្មោះជោគជ័យ!"
    except Exception as e:
        return False, f"កំហុស៖ {e}"

# --- ផ្ទៀងផ្ទាត់ Login ---
def check_login_db(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password, role FROM users WHERE username = %s;", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        stored_hash, role = user[0], user[1]
        if verify_password(stored_hash, password):
            return True, role
    return False, None