import streamlit as st
import database as db
import random

# ១. កំណត់មុខមាត់ទំព័រ Web
st.set_page_config(page_title="EV Bike Shop System", layout="wide")

st.title("🚲 ប្រព័ន្ធគ្រប់គ្រងហាងកង់អគ្គិសនី")

# ២. បង្កើត Tabs ទាំង ៣ ជាមុនសិន (ត្រង់នេះហើយដែលបង្កើត tab1, tab2, tab3)
tab1, tab2, tab3 = st.tabs(["📦 គ្រប់គ្រងស្តុក", "🛒 ការលក់", "📲 Telegram & Security"])

# ---------------------------------------------------------
# Tab 1: គ្រប់គ្រងស្តុក
# ---------------------------------------------------------
with tab1:
    st.subheader("📦 បញ្ជីស្តុកកង់អគ្គិសនី")
    # (ដាក់កូដគ្រប់គ្រងស្តុករបស់អ្នកនៅទីនេះ)

# ---------------------------------------------------------
# Tab 2: ការលក់
# ---------------------------------------------------------
with tab2:
    st.subheader("🛒 ប្រព័ន្ធកត់ត្រាការលក់")
    # (ដាក់កូដការលក់របស់អ្នកនៅទីនេះ)

# ---------------------------------------------------------
# Tab 3: Telegram & Reset Password
# ---------------------------------------------------------
with tab3:
    st.subheader("📲 សេវាកម្ម Telegram & Reset Password")
    
    # 1️⃣ ការភ្ជាប់ Telegram
    st.markdown("### 1️⃣ ភ្ជាប់គណនីជាមួយ Telegram")
    link_user = st.text_input("បញ្ចូល Username របស់អ្នកដើម្បីភ្ជាប់៖", key="link_user")
    
    if link_user:
        telegram_url = f"https://t.me/{db.TELEGRAM_BOT_USERNAME}?start={link_user}"
        st.markdown(f'👉 [ចុចទីនេះដើម្បីបើក Telegram រួចចុច START]({telegram_url})')
        
        if st.button("🔄 ផ្ទៀងផ្ទាត់ការភ្ជាប់ Telegram"):
            db.sync_telegram_connections()
            st.success("បានធ្វើបច្ចុប្បន្នភាព! ប្រសិនបើអ្នកបានចុច START ក្នុង Telegram រួចរាល់ ការភ្ជាប់ត្រូវបានបញ្ចប់។")

    st.divider()

    # 2️⃣ Reset Password តាម OTP
    st.markdown("### 2️⃣ Reset Password តាម OTP")
    reset_user = st.text_input("ឈ្មោះគណនីដែលភ្លេច Password (Username):", key="rst_user")
    
    if st.button("📩 ផ្ញើលេខកូដ OTP ទៅ Telegram របស់ខ្ញុំ"):
        if reset_user:
            otp_code = str(random.randint(100000, 999999))
            ok, msg = db.send_otp_to_user(reset_user, otp_code)
            if ok:
                st.session_state['sent_otp'] = otp_code
                st.session_state['target_user'] = reset_user
                st.success(msg)
            else:
                st.error(msg)
        else:
            st.warning("សូមបញ្ចូល Username ជាមុនសិន!")

    input_otp = st.text_input("លេខកូដ OTP ៦ ខ្ទង់ (ទទួលបានក្នុង Telegram)", key="input_otp")
    new_pass = st.text_input("ពាក្យសម្ងាត់ថ្មី", type="password", key="new_pass_otp")
    
    if st.button("ដូរពាក្យសម្ងាត់"):
        if 'sent_otp' in st.session_state and st.session_state['sent_otp']:
            if input_otp == st.session_state['sent_otp']:
                if reset_user == st.session_state['target_user']:
                    ok, msg = db.reset_password_db(reset_user, new_pass)
                    if ok:
                        st.success(msg)
                        st.session_state['sent_otp'] = None
                    else:
                        st.error(msg)
                else:
                    st.error("Username មិនត្រូវគ្នា!")
            else:
                st.error("លេខកូដ OTP មិនត្រឹមត្រូវទេ!")
        else:
            st.warning("សូមចុចប៊ូតុង 'ផ្ញើលេខកូដ OTP' ជាមុនសិន!")