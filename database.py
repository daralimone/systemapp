from asyncio import open_connection

import psycopg2
import hashlib
import os
import random
import requests

# 🤖 ដាក់ព័ត៌មាន Bot របស់អ្នកនៅទីនេះ
TELEGRAM_BOT_TOKEN = "8837515158:AAG3XTYNKQhd9G9_AKpam8wUE-Axj3BsOoA"      # Bot Token ចេញពី @BotFather
TELEGRAM_BOT_USERNAME = "resetpasswordsys_bot" # Username Bot (ឧ. EVBike_Shop_bot) គ្មានសញ្ញា @

# 1. បន្ថែម Column telegram_chat_id ទៅក្នុង Table Users
def init_db():
    conn = open_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role VARCHAR(20) DEFAULT 'Staff',
            telegram_chat_id VARCHAR(50)
        );
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# 2. មុខងារទាញយក Chat ID ពី Telegram ដោយស្វ័យប្រវត្តិ ពេល User ចុច /start
def sync_telegram_connections():
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
        res = requests.get(url).json()
        if res.get("ok"):
            conn = open_connection()
            cursor = conn.cursor()
            for result in res.get("result", []):
                msg = result.get("message", {})
                text = msg.get("text", "")
                chat_id = msg.get("chat", {}).get("id")
                
                # បើ User ចុច Start តាម Link (ឧ. /start username)
                if text.startswith("/start ") and chat_id:
                    target_username = text.split("/start ")[1].strip()
                    cursor.execute("UPDATE users SET telegram_chat_id = %s WHERE username = %s;", (str(chat_id), target_username))
                    conn.commit()
                    
                    # ផ្ញើសារប្រាប់ User វិញថាភ្ជាប់ជោគជ័យ
                    send_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                    requests.post(send_url, json={
                        "chat_id": chat_id,
                        "text": f"✅ ភ្ជាប់ Telegram ជាមួយគណនី '{target_username}' ជោគជ័យហើយ!"
                    })
            cursor.close()
            conn.close()
    except Exception as e:
        print("Telegram Sync Error:", e)

# 3. មុខងារផ្ញើ OTP ទៅកាន់ Telegram ផ្ទាល់ខ្លួនរបស់ User
def send_otp_to_user(username, otp_code):
    sync_telegram_connections() # ធ្វើបច្ចុប្បន្នភាព Data ជាមុន
    conn = open_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT telegram_chat_id FROM users WHERE username = %s;", (username,))
    res = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not res or not res[0]:
        return False, "គណនីនេះមិនទាន់បានភ្ជាប់ Telegram ទេ! សូមភ្ជាប់ Telegram ជាមុនសិន។"
        
    chat_id = res[0]
    try:
        message = f"🔑 [លេខកូដ Reset Password]\nលេខកូដ OTP របស់អ្នកគឺ៖ {otp_code}\n(សូមកុំចែករំលែកលេខនេះទៅអ្នកដទៃ)"
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        resp = requests.post(url, json=payload)
        if resp.status_code == 200:
            return True, "លេខកូដ OTP ត្រូវបានផ្ញើទៅ Telegram របស់អ្នករួចហើយ!"
        else:
            return False, "ផ្ញើ OTP បរាជ័យ! សូមពិនិត្យមើល Telegram របស់អ្នក។"
    except Exception as e:
        return False, f"កំហុស៖ {e}"

def hash_password(password):
    raise NotImplementedError

# 4. មុខងារអាប់ដេត Password ថ្មី
def reset_password_db(username, new_password):
    try:
        conn = open_connection()
        cursor = conn.cursor()
        hashed_pw = hash_password(new_password)
        cursor.execute("UPDATE users SET password = %s WHERE username = %s;", (hashed_pw, username))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "កំណត់ពាក្យសម្ងាត់ថ្មីជោគជ័យ!"
    except Exception as e:
        return False, f"កំហុស៖ {e}"