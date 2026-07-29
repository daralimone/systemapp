import streamlit as st
import database as db  # Import ពី file database.py ដែលយើងទើបបង្កើត

st.set_page_config(page_title="ប្រព័ន្ធបុគ្គលិកផ្ទៃក្នុង", layout="centered")

# បង្កើត Database និងគណនី Admin ដំបូងប្រសិនបើគ្មាន
db.init_db()
db.register_user("admin", "123456", "Admin")  # បង្កើត admin / 123456 ស្វ័យប្រវត្តិ

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

def show_login_page():
    st.title("🔐 ប្រព័ន្ធចូលប្រើប្រាស់ផ្ទៃក្នុង")
    
    tab1, tab2 = st.tabs(["ចូលប្រព័ន្ធ (Login)", "បង្កើតគណនីថ្មី (Register)"])
    
    # ផ្ទាំង Login
    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login"):
            success, role = db.check_login_db(username, password)
            if success:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success(f"ចូលប្រព័ន្ធជោគជ័យ! តួនាទី៖ {role}")
                st.rerun()
            else:
                st.error("Username ឬ Password មិនត្រឹមត្រូវ!")

    # ផ្ទាំង Register បុគ្គលិកថ្មី
    with tab2:
        new_user = st.text_input("Username ថ្មី", key="reg_user")
        new_pass = st.text_input("Password ថ្មី", type="password", key="reg_pass")
        role = st.selectbox("តួនាទី", ["Staff", "Manager", "Admin"])
        
        if st.button("ចុះឈ្មោះ"):
            if new_user and new_pass:
                ok, msg = db.register_user(new_user, new_pass, role)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
            else:
                st.warning("សូមបំពេញព័ត៌មានឱ្យគ្រប់!")

if not st.session_state["logged_in"]:
    show_login_page()
    st.stop()

# --- ផ្ទាំង Dashboard ពេល Login រួច ---
st.sidebar.write(f"👤 គណនី៖ **{st.session_state['username']}**")
if st.sidebar.button("Logout"):
    st.session_state["logged_in"] = False
    st.rerun()

st.title("🏢 ប្រព័ន្ធគ្រប់គ្រងទិន្នន័យ និងឯកសារ")
st.success(f"ស្វាគមន៍ {st.session_state['username']}! ទិន្នន័យរបស់អ្នកត្រូវរក្សាទុកក្នុង SQLite Database ដោយសុវត្ថិភាព។")