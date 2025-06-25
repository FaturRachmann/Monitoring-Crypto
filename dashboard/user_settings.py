import streamlit as st
from auth import auth_manager, get_current_user, logout_user

def show_user_menu():
    """Tampilkan menu user di sidebar kanan"""
    user_data = get_current_user()
    if not user_data:
        return
    
    # User info di sidebar
    with st.sidebar:
        st.markdown("---")
        
        # User profile section
        col1, col2 = st.columns([1, 2])
        with col1:
            # Avatar placeholder
            st.markdown("""
            <div style='
                width: 40px; 
                height: 40px; 
                background: linear-gradient(45deg, #667eea, #764ba2);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: 18px;
            '>
                {initial}
            </div>
            """.format(initial=user_data.get('name', 'U')[0].upper()), unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"**{user_data.get('name', 'User')}**")
            st.caption(f"@{st.session_state['username']}")
        
        # Menu buttons
        if st.button("⚙️ Pengaturan", use_container_width=True):
            st.session_state["show_settings"] = True
        
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            logout_user()

def show_settings_modal():
    """Tampilkan modal pengaturan"""
    if not st.session_state.get("show_settings", False):
        return
    
    user_data = get_current_user()
    if not user_data:
        return
    
    # Settings modal
    with st.expander("⚙️ Pengaturan Akun & Dashboard", expanded=True):
        tab1, tab2, tab3 = st.tabs(["👤 Profil", "🎛️ Dashboard", "🔑 API Keys"])
        
        with tab1:
            show_profile_settings(user_data)
        
        with tab2:
            show_dashboard_settings(user_data)
        
        with tab3:
            show_api_settings(user_data)
        
        # Close button
        if st.button("❌ Tutup Pengaturan"):
            st.session_state["show_settings"] = False
            st.rerun()

def show_profile_settings(user_data):
    """Pengaturan profil pengguna"""
    st.markdown("### 👤 Pengaturan Profil")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Nama Lengkap", value=user_data.get('name', ''))
            email = st.text_input("Email", value=user_data.get('email', ''))
        
        with col2:
            # Password change
            new_password = st.text_input("Password Baru (kosongkan jika tidak ingin mengubah)", type="password")
            confirm_password = st.text_input("Konfirmasi Password Baru", type="password")
        
        # Theme selection
        current_theme = user_data.get('settings', {}).get('theme', 'dark')
        theme = st.selectbox("Tema", options=['dark', 'light'], index=0 if current_theme == 'dark' else 1)
        
        submit_profile = st.form_submit_button("💾 Simpan Profil", use_container_width=True)
    
    if submit_profile:
        errors = []
        
        if not name:
            errors.append("Nama tidak boleh kosong")
        
        if not email or "@" not in email:
            errors.append("Email tidak valid")
        
        if new_password and len(new_password) < 6:
            errors.append("Password baru minimal 6 karakter")
        
        if new_password and new_password != confirm_password:
            errors.append("Konfirmasi password tidak cocok")
        
        if errors:
            for error in errors:
                st.error(f"❌ {error}")
        else:
            # Update profile
            profile_data = {
                'name': name,
                'email': email,
                'settings': user_data.get('settings', {})
            }
            profile_data['settings']['theme'] = theme
            
            if new_password:
                profile_data['password'] = auth_manager.hash_password(new_password)
            
            success = auth_manager.update_user_profile(st.session_state['username'], profile_data)
            
            if success:
                st.success("✅ Profil berhasil diperbarui!")
                # Update session data
                st.session_state["user_data"] = auth_manager.get_user(st.session_state['username'])
                st.rerun()
            else:
                st.error("❌ Gagal memperbarui profil")

def show_dashboard_settings(user_data):
    """Pengaturan dashboard"""
    st.markdown("### 🎛️ Pengaturan Dashboard")
    
    settings = user_data.get('settings', {})
    
    with st.form("dashboard_form"):
        # Language selection
        current_lang = settings.get('language', 'id')
        language = st.selectbox(
            "Bahasa",
            options=['id', 'en'],
            index=0 if current_lang == 'id' else 1,
            format_func=lambda x: "🇮🇩 Bahasa Indonesia" if x == 'id' else "🇺🇸 English"
        )
        
        # Module selection
        st.markdown("**Modul yang Ditampilkan:**")
        
        all_modules = {
            'prices': '💰 Harga Cryptocurrency',
            'news': '📰 Berita Crypto',
            'whale_tx': '🐋 Transaksi Whale',
            'whale_positions': '💼 Posisi Whale'
        }
        
        current_modules = settings.get('modules', list(all_modules.keys()))
        selected_modules = []
        
        for module_key, module_name in all_modules.items():
            if st.checkbox(module_name, value=module_key in current_modules, key=f"module_{module_key}"):
                selected_modules.append(module_key)
        
        # Auto-refresh settings
        current_refresh = settings.get('auto_refresh_interval', 10)
        refresh_interval = st.slider(
            "Interval Auto-Refresh (detik)",
            min_value=5,
            max_value=60,
            value=current_refresh,
            step=5
        )
        
        # Display settings
        st.markdown("**Pengaturan Tampilan:**")
        col1, col2 = st.columns(2)
        
        with col1:
            show_animations = st.checkbox(
                "Animasi UI",
                value=settings.get('show_animations', True)
            )
            compact_mode = st.checkbox(
                "Mode Kompak",
                value=settings.get('compact_mode', False)
            )
        
        with col2:
            show_alerts = st.checkbox(
                "Notifikasi Alert",
                value=settings.get('show_alerts', True)
            )
            dark_charts = st.checkbox(
                "Chart Mode Gelap",
                value=settings.get('dark_charts', True)
            )
        
        submit_dashboard = st.form_submit_button("💾 Simpan Pengaturan Dashboard", use_container_width=True)
    
    if submit_dashboard:
        if not selected_modules:
            st.error("❌ Pilih minimal satu modul untuk ditampilkan")
        else:
            new_settings = {
                'language': language,
                'modules': selected_modules,
                'auto_refresh_interval': refresh_interval,
                'show_animations': show_animations,
                'compact_mode': compact_mode,
                'show_alerts': show_alerts,
                'dark_charts': dark_charts
            }
            
            success = auth_manager.update_user_settings(st.session_state['username'], new_settings)
            
            if success:
                st.success("✅ Pengaturan dashboard berhasil disimpan!")
                # Update session data
                st.session_state["user_data"] = auth_manager.get_user(st.session_state['username'])
                st.rerun()
            else:
                st.error("❌ Gagal menyimpan pengaturan")

def show_api_settings(user_data):
    """Pengaturan API Keys"""
    st.markdown("### 🔑 Pengaturan API Keys")
    
    settings = user_data.get('settings', {})
    api_keys = settings.get('api_keys', {})
    
    st.info("💡 Tambahkan API keys untuk mengakses data real-time dari berbagai sumber")
    
    with st.form("api_form"):
        # CoinGecko API
        st.markdown("**CoinGecko API**")
        coingecko_key = st.text_input(
            "CoinGecko API Key (opsional)",
            value=api_keys.get('coingecko', ''),
            help="Untuk limit rate yang lebih tinggi"
        )
        
        # News API
        st.markdown("**News API**")
        news_key = st.text_input(
            "News API Key",
            value=api_keys.get('news_api', ''),
            help="Dari newsapi.org untuk berita crypto"
        )
        
        # Binance API (untuk whale tracking)
        st.markdown("**Binance API (Read-Only)**")
        col1, col2 = st.columns(2)
        with col1:
            binance_key = st.text_input(
                "Binance API Key",
                value=api_keys.get('binance_key', ''),
                help="Read-only untuk data market"
            )
        with col2:
            binance_secret = st.text_input(
                "Binance Secret",
                value=api_keys.get('binance_secret', ''),
                type="password",
                help="Secret key (akan dienkripsi)"
            )
        
        # Custom APIs
        st.markdown("**Custom API Endpoints**")
        custom_apis = st.text_area(
            "Custom API URLs (satu per baris)",
            value='\n'.join(api_keys.get('custom_apis', [])),
            help="Format: name=url"
        )
        
        submit_api = st.form_submit_button("💾 Simpan API Keys", use_container_width=True)
    
    if submit_api:
        new_api_keys = {
            'coingecko': coingecko_key.strip(),
            'news_api': news_key.strip(),
            'binance_key': binance_key.strip(),
            'binance_secret': binance_secret.strip(),
            'custom_apis': [line.strip() for line in custom_apis.split('\n') if line.strip()]
        }
        
        # Remove empty keys
        new_api_keys = {k: v for k, v in new_api_keys.items() if v}
        
        success = auth_manager.update_user_settings(
            st.session_state['username'], 
            {'api_keys': new_api_keys}
        )
        
        if success:
            st.success("✅ API Keys berhasil disimpan!")
            # Update session data
            st.session_state["user_data"] = auth_manager.get_user(st.session_state['username'])
            st.rerun()
        else:
            st.error("❌ Gagal menyimpan API Keys")
    
    # Test API section
    if api_keys:
        st.markdown("---")
        st.markdown("**🧪 Test API Connections**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Test CoinGecko", disabled=not api_keys.get('coingecko')):
                test_coingecko_api(api_keys.get('coingecko'))
        
        with col2:
            if st.button("Test News API", disabled=not api_keys.get('news_api')):
                test_news_api(api_keys.get('news_api'))
        
        with col3:
            if st.button("Test Binance", disabled=not (api_keys.get('binance_key') and api_keys.get('binance_secret'))):
                test_binance_api(api_keys.get('binance_key'), api_keys.get('binance_secret'))

def test_coingecko_api(api_key):
    """Test CoinGecko API connection"""
    # Placeholder for API testing
    st.info("🔄 Testing CoinGecko API...")
    # Add actual API test logic here

def test_news_api(api_key):
    """Test News API connection"""
    # Placeholder for API testing
    st.info("🔄 Testing News API...")
    # Add actual API test logic here

def test_binance_api(api_key, secret):
    """Test Binance API connection"""
    # Placeholder for API testing
    st.info("🔄 Testing Binance API...")
    # Add actual API test logic here