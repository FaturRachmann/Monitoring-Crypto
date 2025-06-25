import streamlit as st
from auth import auth_manager, login_user

def show_login_page():
    """Tampilkan halaman login dan registrasi"""
    
    # Custom CSS untuk styling
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }
    
    .login-title {
        text-align: center;
        color: white;
        font-size: 2.5rem;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .login-subtitle {
        text-align: center;
        color: rgba(255,255,255,0.8);
        margin-bottom: 2rem;
    }
    
    .stTextInput > div > div > input {
        background-color: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 8px;
        color: white;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(255,255,255,0.6);
    }
    
    .login-button {
        width: 100%;
        background: linear-gradient(45deg, #ff6b6b, #ee5a24);
        border: none;
        border-radius: 8px;
        padding: 12px;
        color: white;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .login-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .register-button {
        width: 100%;
        background: linear-gradient(45deg, #4ecdc4, #44a08d);
        border: none;
        border-radius: 8px;
        padding: 12px;
        color: white;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .register-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="login-title">
        📈 Dashboard Crypto - FBucket
    </div>
    <div class="login-subtitle">
        Dashboard Monitoring Cryptocurrency
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs untuk Login dan Register
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Registrasi"])
    
    with tab1:
        show_login_form()
    
    with tab2:
        show_register_form()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        <p>🔒 Akses terbatas untuk pengguna terdaftar</p>
        <p>Default Admin: username: <code>admin</code>, password: <code>admin123</code></p>
    </div>
    """, unsafe_allow_html=True)

def show_login_form():
    """Form login"""
    with st.container():
        st.markdown("### 🔑 Masuk ke Akun")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Masukkan username")
            password = st.text_input("Password", type="password", placeholder="Masukkan password")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                login_btn = st.form_submit_button("🚀 Login", use_container_width=True)
            with col2:
                remember_me = st.checkbox("Ingat saya")
        
        if login_btn:
            if not username or not password:
                st.error("❌ Username dan password harus diisi!")
            else:
                success, message = auth_manager.authenticate(username, password)
                
                if success:
                    login_user(username)
                    st.success(f"✅ {message}")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ {message}")

def show_register_form():
    """Form registrasi"""
    with st.container():
        st.markdown("### 📝 Buat Akun Baru")
        
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("Username", placeholder="Pilih username")
                email = st.text_input("Email", placeholder="email@example.com")
            
            with col2:
                name = st.text_input("Nama Lengkap", placeholder="Nama lengkap")
                password = st.text_input("Password", type="password", placeholder="Minimal 6 karakter")
            
            confirm_password = st.text_input("Konfirmasi Password", type="password", placeholder="Ulangi password")
            
            agree_terms = st.checkbox("Saya setuju dengan syarat dan ketentuan")
            
            register_btn = st.form_submit_button("🎯 Daftar Sekarang", use_container_width=True)
        
        if register_btn:
            # Validasi form
            errors = []
            
            if not username or len(username) < 3:
                errors.append("Username minimal 3 karakter")
            
            if not email or "@" not in email:
                errors.append("Email tidak valid")
            
            if not name or len(name) < 2:
                errors.append("Nama lengkap harus diisi")
            
            if not password or len(password) < 6:
                errors.append("Password minimal 6 karakter")
            
            if password != confirm_password:
                errors.append("Konfirmasi password tidak cocok")
            
            if not agree_terms:
                errors.append("Anda harus menyetujui syarat dan ketentuan")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                success, message = auth_manager.register_user(username, password, email, name)
                
                if success:
                    st.success(f"✅ {message}")
                    st.success("🎉 Akun berhasil dibuat! Silakan login.")
                    st.balloons()
                else:
                    st.error(f"❌ {message}")

def show_welcome_message():
    """Pesan selamat datang untuk user baru"""
    if "show_welcome" not in st.session_state:
        st.session_state["show_welcome"] = True
    
    if st.session_state["show_welcome"]:
        user_data = st.session_state.get("user_data", {})
        name = user_data.get("name", "User")
        
        st.success(f"🎉 Selamat datang, {name}!")
        
        # Auto-hide welcome message after showing
        st.session_state["show_welcome"] = False
