import hashlib
import json
import os
from datetime import datetime, timedelta
import streamlit as st

class AuthManager:
    def __init__(self, users_file="users.json"):
        self.users_file = users_file
        self.ensure_users_file()
    
    def ensure_users_file(self):
        """Pastikan file users.json ada"""
        if not os.path.exists(self.users_file):
            # Buat akun admin default
            default_users = {
                "admin": {
                    "password": self.hash_password("admin123"),
                    "email": "admin@example.com",
                    "name": "Administrator",
                    "role": "admin",
                    "created_at": datetime.now().isoformat(),
                    "settings": {
                        "language": "id",
                        "modules": ["prices", "news", "whale_tx", "whale_positions"],
                        "api_keys": {},
                        "theme": "dark"
                    }
                }
            }
            self.save_users(default_users)
    
    def hash_password(self, password):
        """Hash password menggunakan SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def load_users(self):
        """Load users dari file JSON"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_users(self, users):
        """Simpan users ke file JSON"""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2, default=str)
    
    def register_user(self, username, password, email, name):
        """Registrasi user baru"""
        users = self.load_users()
        
        if username in users:
            return False, "Username sudah digunakan"
        
        users[username] = {
            "password": self.hash_password(password),
            "email": email,
            "name": name,
            "role": "user",
            "created_at": datetime.now().isoformat(),
            "settings": {
                "language": "id",
                "modules": ["prices", "news", "whale_tx", "whale_positions"],
                "api_keys": {},
                "theme": "dark"
            }
        }
        
        self.save_users(users)
        return True, "Registrasi berhasil"
    
    def authenticate(self, username, password):
        """Autentikasi user"""
        users = self.load_users()
        
        if username not in users:
            return False, "Username tidak ditemukan"
        
        if users[username]["password"] != self.hash_password(password):
            return False, "Password salah"
        
        return True, "Login berhasil"
    
    def get_user(self, username):
        """Ambil data user"""
        users = self.load_users()
        return users.get(username)
    
    def update_user_settings(self, username, settings):
        """Update pengaturan user"""
        users = self.load_users()
        if username in users:
            users[username]["settings"].update(settings)
            self.save_users(users)
            return True
        return False
    
    def update_user_profile(self, username, profile_data):
        """Update profil user"""
        users = self.load_users()
        if username in users:
            users[username].update(profile_data)
            self.save_users(users)
            return True
        return False

# Instance global
auth_manager = AuthManager()

def check_authentication():
    """Cek apakah user sudah login"""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    
    if "username" not in st.session_state:
        st.session_state["username"] = None
    
    return st.session_state["authenticated"]

def login_user(username):
    """Set status login user"""
    st.session_state["authenticated"] = True
    st.session_state["username"] = username
    st.session_state["user_data"] = auth_manager.get_user(username)

def logout_user():
    """Logout user"""
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["user_data"] = None
    st.rerun()

def get_current_user():
    """Ambil data user yang sedang login"""
    if check_authentication():
        return st.session_state.get("user_data")
    return None