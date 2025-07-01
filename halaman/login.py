import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
import urllib.parse
from utils.db_user import init_db, save_user, get_user

# ===== CONFIGURATIONS =====
GOOGLE_CLIENT_ID = st.secrets["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = st.secrets["GOOGLE_CLIENT_SECRET"]
REDIRECT_URI = "http://localhost:5000"  # Change this to your actual redirect URI

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

SCOPES = ["openid", "email", "profile"]
init_db()  # Initialize the database

# ===== STREAMLIT LOGIN & REGISTER =====
# Simulasi database user (disimpan sementara dalam session_state)
if 'users' not in st.session_state:
    st.session_state.users = {"admin": "admin123"}  # contoh user default

# Status login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None

if st.session_state.get("logged_in", False):
    st.success(f"You're logged in as {st.session_state.get('name') or st.session_state.get('username')} ✅")
    if st.button("Logout"):
        for key in ["logged_in", "username", "email", "name", "picture"]:
            st.session_state.pop(key, None)
        st.success("Logged out successfully.")
    st.stop()  # stop rendering sisa halaman

# Fungsi login
def login(username, password):
    if username in st.session_state.users:
        if st.session_state.users[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome, {username} 👋")
        else:
            st.error("Wrong password!")
    else:
        st.error("User not found!")

# Fungsi register
def register(username, password):
    if username in st.session_state.users:
        st.error("Username already exists!")
    else:
        st.session_state.users[username] = password
        st.success("Registration successful! You can now log in.")

# Logout
def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.success("Logged out.")

# UI utama
st.title("🔐 Streamlit Login & Register")

# Jika sudah login
if st.session_state.logged_in:
    st.success(f"You're logged in as **{st.session_state.username}**")
    if st.button("Logout"):
        logout()
else:
    tab1, tab2 = st.tabs(["🔓 Login", "📝 Register"])

    with tab1:
        st.subheader("Login to your account")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            login(username, password)

    with tab2:
        st.subheader("Create a new account")
        new_user = st.text_input("New username", key="reg_user")
        new_pass = st.text_input("New password", type="password", key="reg_pass")
        if st.button("Register"):
            register(new_user, new_pass)

# ===== HELPER FUNCTION =====
def get_login_url():
    oauth = OAuth2Session(
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPES
    )
    uri, _ = oauth.create_authorization_url(AUTHORIZE_URL)
    return uri

def get_user_info(code):
    oauth = OAuth2Session(
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        redirect_uri=REDIRECT_URI
    )
    token = oauth.fetch_token(TOKEN_URL, code=code)
    
    # Simpan token ke session sebelum melakukan request
    oauth.token = token
    
    # Sekarang aman untuk memanggil .get()
    resp = oauth.get(USERINFO_URL)
    return resp.json()

# ===== STREAMLIT APP =====
# st.title("🔐 Login with Google (OAuth 2.0)")

# Use st.query_params instead of deprecated function
code = st.query_params.get("code")

if code:
    # user_info = get_user_info(code)
    # st.success("✅ Logged in successfully!")
    # st.json(user_info)
    # st.write(f"👤 Hello, {user_info['name']} ({user_info['email']})")
    user_info = get_user_info(code)
    
    # Simpan user ke database jika belum ada
    save_user(user_info['email'], user_info['name'], user_info['picture'], "google")
    
    # Simpan ke session
    st.session_state.logged_in = True
    st.session_state.email = user_info['email']
    st.session_state.name = user_info['name']
    st.session_state.picture = user_info['picture']
    
    st.success(f"Welcome, {user_info['name']} 👋")
    st.image(user_info['picture'], width=100)
else:
    login_url = get_login_url()
    st.markdown(
        f"""
        <a href="{login_url}">
            <img src="https://developers.google.com/identity/images/btn_google_signin_dark_normal_web.png" 
                 alt="Sign in with Google" 
                 style="height:50px;">
        </a>
        """,
        unsafe_allow_html=True
    )
