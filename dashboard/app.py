import sys
import os
import random
import logging
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# Import authentication modules
from auth import check_authentication, get_current_user
from login_page import show_login_page, show_welcome_message
from user_settings import show_user_menu, show_settings_modal

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import backend modules (pastikan file-file ini tersedia)
try:
    from backend.price_feed import get_prices
    from backend.news_feed import fetch_news
    from backend.whale_tracker import get_fake_whale_tx
    from ai.summarize import summarize
except ImportError as e:
    logging.warning(f"Backend modules not found: {e}")
    # Fallback functions jika backend tidak tersedia
    def get_prices():
        return {
            'bitcoin': {'usd': 104500},
            'ethereum': {'usd': 2580}
        }
    
    def fetch_news():
        return [
            {
                'title': 'Bitcoin Mencapai ATH Baru',
                'summary': 'Bitcoin berhasil menembus level $105,000 untuk pertama kalinya...',
                'link': 'https://example.com'
            }
        ]
    
    def get_fake_whale_tx():
        symbols = ["BTC", "ETH", "SOL", "ADA"]
        return {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'symbol': random.choice(symbols),
            'type': random.choice(['BUY', 'SELL']),
            'amount': f"${random.randint(100000, 5000000):,}",
            'exchange': random.choice(['Binance', 'Bybit', 'OKX'])
        }

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Whale Position Functions (sama seperti kode asli)
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "BNBUSDT", "DOTUSDT", "MATICUSDT", "LINKUSDT"]

def get_simulated_open_positions(min_usd=10000, count=5):
    """Generate simulated open positions for whale tracking"""
    positions = []
    current_time = datetime.now()
    
    for i in range(count):
        # Generate random time within last 2 hours
        time_offset = random.randint(0, 7200)
        position_time = current_time - timedelta(seconds=time_offset)
        
        # Generate position amount with realistic distribution
        if random.random() < 0.1:
            amount = random.randint(min_usd * 10, min_usd * 50)
        elif random.random() < 0.3:
            amount = random.randint(min_usd * 3, min_usd * 10)
        else:
            amount = random.randint(min_usd, min_usd * 3)
        
        # Select symbol with weighted probability
        symbol_weights = {
            "BTCUSDT": 0.3, "ETHUSDT": 0.25, "SOLUSDT": 0.15, "ADAUSDT": 0.1,
            "BNBUSDT": 0.08, "DOTUSDT": 0.05, "MATICUSDT": 0.04, "LINKUSDT": 0.03
        }
        
        symbol = random.choices(
            list(symbol_weights.keys()),
            weights=list(symbol_weights.values())
        )[0]
        
        # Generate side with slight bias towards LONG
        side = random.choices(["LONG", "SHORT"], weights=[0.55, 0.45])[0]
        
        # Generate entry price
        base_prices = {
            "BTCUSDT": 104000, "ETHUSDT": 2500, "SOLUSDT": 145, "ADAUSDT": 1.2,
            "BNBUSDT": 690, "DOTUSDT": 7.8, "MATICUSDT": 0.85, "LINKUSDT": 15.5
        }
        
        base_price = base_prices.get(symbol, 100)
        price_variation = random.uniform(-0.05, 0.05)
        entry_price = base_price * (1 + price_variation)
        
        # Calculate position size
        position_size = amount / entry_price
        
        # Generate leverage
        leverage = random.choice([1, 2, 3, 5, 10, 20, 25, 50])
        
        # Generate PnL
        pnl_percentage = random.uniform(-0.15, 0.25)
        unrealized_pnl = amount * pnl_percentage
        
        # Generate margin used
        margin_used = amount / leverage
        
        # Generate current price based on PnL
        if side == "LONG":
            current_price = entry_price * (1 + (unrealized_pnl / amount))
        else:
            current_price = entry_price * (1 - (unrealized_pnl / amount))
        
        # Generate liquidation price
        if side == "LONG":
            liquidation_price = entry_price * (1 - (0.8 / leverage))
        else:
            liquidation_price = entry_price * (1 + (0.8 / leverage))
        
        positions.append({
            "Time": position_time.strftime("%H:%M:%S"),
            "Symbol": symbol.replace("USDT", ""),
            "Side": side,
            "Amount (USD)": f"${amount:,}",
            "Size": f"{position_size:.4f}",
            "Entry Price": f"${entry_price:,.2f}",
            "Current Price": f"${current_price:,.2f}",
            "Leverage": f"{leverage}x",
            "Margin": f"${margin_used:,.0f}",
            "PnL": f"${unrealized_pnl:,.0f}",
            "PnL %": f"{pnl_percentage * 100:+.1f}%",
            "Liq. Price": f"${liquidation_price:,.2f}",
            "Exchange": random.choice(["Binance", "Bybit", "OKX", "Bitget"])
        })
    
    return positions

def update_position_pnl(position):
    """Update a single position's PnL and current price"""
    try:
        # Extract current values
        current_pnl_str = position['PnL'].replace('$', '').replace(',', '')
        current_pnl = float(current_pnl_str)
        amount_str = position['Amount (USD)'].replace('$', '').replace(',', '')
        amount = float(amount_str)
        
        # Small price movement (-2% to +3%)
        price_change = random.uniform(-0.02, 0.03)
        new_pnl = current_pnl + (amount * price_change)
        new_pnl_pct = (new_pnl / amount) * 100
        
        # Update PnL fields
        position['PnL'] = f"${new_pnl:,.0f}"
        position['PnL %'] = f"{new_pnl_pct:+.1f}%"
        
        # Update current price based on entry price and PnL
        entry_price = float(position['Entry Price'].replace('$', '').replace(',', ''))
        if position['Side'] == 'LONG':
            new_current_price = entry_price * (1 + (new_pnl / amount))
        else:
            new_current_price = entry_price * (1 - (new_pnl / amount))
        position['Current Price'] = f"${new_current_price:,.2f}"
        
        return position
    except Exception as e:
        logger.error(f"Error updating position PnL: {e}")
        return position

def format_currency(value):
    """Format currency with proper thousand separators"""
    try:
        if isinstance(value, (int, float)):
            return f"${value:,.2f}"
        return value
    except Exception as e:
        logger.error(f"Error formatting currency: {e}")
        return value

def get_market_data():
    """Get comprehensive market data"""
    try:
        return {
            'total_market_cap': '$2.45T',
            'volume_24h': '$98.2B',
            'btc_dominance': '52.3%',
            'fear_greed_index': 65
        }
    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        return {}

def clean_html(html_text):
    """Remove HTML tags from text"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', html_text)

def get_user_language():
    """Get user's preferred language"""
    user_data = get_current_user()
    if user_data:
        return user_data.get('settings', {}).get('language', 'id')
    return 'id'

def get_enabled_modules():
    """Get user's enabled modules"""
    user_data = get_current_user()
    if user_data:
        return user_data.get('settings', {}).get('modules', ['prices', 'news', 'whale_tx', 'whale_positions'])
    return ['prices', 'news', 'whale_tx', 'whale_positions']

def get_auto_refresh_interval():
    """Get user's preferred auto-refresh interval"""
    user_data = get_current_user()
    if user_data:
        return user_data.get('settings', {}).get('auto_refresh_interval', 10) * 1000  # Convert to milliseconds
    return 10000

def show_protected_dashboard():
    """Dashboard yang dilindungi autentikasi"""
    try:
        # Show welcome message for new users
        show_welcome_message()
        
        # Show user menu in sidebar
        show_user_menu()
        
        # Show settings modal if requested
        show_settings_modal()
        
        # Get user preferences
        language = get_user_language()
        enabled_modules = get_enabled_modules()
        refresh_interval = get_auto_refresh_interval()
        
        # Auto-refresh with user's preferred interval
        st_autorefresh(interval=refresh_interval, key="datarefresh")

        # Title and description with real-time indicator
        title = "📈 Dashboard Crypto - FBucket" if language == 'id' else "📈 Dashboard Crypto - FBucket"
        subtitle = "Pantauan pasar crypto dan transaksi besar secara real-time" if language == 'id' else "Real-time crypto market and whale transaction monitoring"
        
        st.title(title)
        col_title, col_status = st.columns([3, 1])
        
        with col_title:
            st.markdown(subtitle)
        
        with col_status:
            # Real-time status indicator
            current_time = datetime.now()
            status_text = "LIVE" if language == 'id' else "LIVE"
            st.markdown(f"""
                <div style='text-align: right; padding: 10px;'>
                    <span style='color: #00ff88; font-size: 12px;'>
                        🟢 {status_text} • {current_time.strftime('%H:%M:%S')}
                    </span>
                </div>
            """, unsafe_allow_html=True)

        # Market metrics (if enabled)
        if 'prices' in enabled_modules:
            col1, col2, col3, col4 = st.columns(4)
            
            prices = get_prices()
            market_data = get_market_data()

            with col1:
                btc_price = prices.get('bitcoin', {}).get('usd', 0)
                st.metric("Bitcoin (BTC)", format_currency(btc_price), "+2.4%")

            with col2:
                eth_price = prices.get('ethereum', {}).get('usd', 0)
                st.metric("Ethereum (ETH)", format_currency(eth_price), "-0.8%")

            with col3:
                cap_label = "Total Market Cap" if language == 'en' else "Total Market Cap"
                st.metric(cap_label, market_data.get('total_market_cap', 'N/A'))

            with col4:
                vol_label = "24h Volume" if language == 'en' else "Volume 24j"
                st.metric(vol_label, market_data.get('volume_24h', 'N/A'))

        # Whale Transactions (if enabled)
        if 'whale_tx' in enabled_modules:
            whale_title = "🐋 Whale Transactions" if language == 'en' else "🐋 Transaksi Whale"
            st.subheader(whale_title)
            
            # Initialize whale transactions if not exists
            if "whale_tx" not in st.session_state:
                st.session_state["whale_tx"] = []
            
            # Initialize last update time
            if "last_tx_update" not in st.session_state:
                st.session_state["last_tx_update"] = datetime.now()
            
            # Auto-generate new transactions every 15-45 seconds
            current_time = datetime.now()
            time_since_last_tx = (current_time - st.session_state["last_tx_update"]).total_seconds()
            
            # Generate new transaction with probability based on time elapsed
            should_generate_tx = (
                time_since_last_tx > 15 and random.random() < 0.3
            ) or time_since_last_tx > 45
            
            if should_generate_tx:
                tx = get_fake_whale_tx()
                if tx:
                    st.session_state["whale_tx"].append(tx)
                    st.session_state["last_tx_update"] = current_time
                    # Keep only last 15 transactions for better visibility
                    if len(st.session_state["whale_tx"]) > 15:
                        st.session_state["whale_tx"] = st.session_state["whale_tx"][-15:]
            
            # Display transactions with real-time updates
            if st.session_state["whale_tx"]:
                tx_df = pd.DataFrame(st.session_state["whale_tx"])
                # Sort by timestamp to show newest first
                if 'timestamp' in tx_df.columns:
                    tx_df = tx_df.sort_values('timestamp', ascending=False)
                st.dataframe(tx_df, use_container_width=True)
                
                # Show transaction stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    total_label = "Total Transactions" if language == 'en' else "Total Transaksi"
                    st.metric(total_label, len(st.session_state["whale_tx"]))
                with col2:
                    if len(st.session_state["whale_tx"]) > 0:
                        latest_time = st.session_state["last_tx_update"]
                        time_ago = (current_time - latest_time).total_seconds()
                        last_label = "Last Transaction" if language == 'en' else "Transaksi Terakhir"
                        st.metric(last_label, f"{int(time_ago)}s ago")
                with col3:
                    next_tx_time = 45 - time_since_last_tx
                    if next_tx_time > 0:
                        next_label = "Next TX in" if language == 'en' else "TX Berikutnya"
                        st.metric(next_label, f"~{int(next_tx_time)}s")
                    else:
                        next_label = "Next TX" if language == 'en' else "TX Berikutnya"
                        any_moment = "Any moment..." if language == 'en' else "Sebentar lagi..."
                        st.metric(next_label, any_moment)
            else:
                waiting_msg = "🔄 Waiting for new whale transactions..." if language == 'en' else "🔄 Menunggu transaksi whale baru..."
                st.info(waiting_msg)

        # Whale Positions (if enabled)
        if 'whale_positions' in enabled_modules:
            positions_title = "💼 Whale Open Positions" if language == 'en' else "💼 Posisi Terbuka Whale"
            st.subheader(positions_title)
            
            # Initialize whale positions and timing
            if "whale_positions" not in st.session_state:
                st.session_state["whale_positions"] = []
            
            if "last_position_update" not in st.session_state:
                st.session_state["last_position_update"] = datetime.now()
            
            # Auto-update positions every 20-60 seconds
            current_time = datetime.now()
            time_since_last_update = (current_time - st.session_state["last_position_update"]).total_seconds()
            
            # Generate new positions or update existing ones
            should_update_positions = (
                len(st.session_state["whale_positions"]) == 0 or 
                (time_since_last_update > 20 and random.random() < 0.4) or
                time_since_last_update > 60
            )
            
            if should_update_positions:
                # Mix of updating existing and adding new positions
                if len(st.session_state["whale_positions"]) > 0 and random.random() < 0.7:
                    # Update some existing positions (simulate PnL changes)
                    updated_positions = []
                    for pos in st.session_state["whale_positions"]:
                        # Randomly update some positions
                        if random.random() < 0.6:
                            pos = update_position_pnl(pos)
                        updated_positions.append(pos)
                    
                    # Occasionally add a new position or remove an old one
                    if random.random() < 0.3:
                        new_positions = get_simulated_open_positions(min_usd=50000, count=1)
                        updated_positions.extend(new_positions)
                    elif len(updated_positions) > 8 and random.random() < 0.2:
                        # Remove oldest position occasionally
                        updated_positions = updated_positions[1:]
                    
                    st.session_state["whale_positions"] = updated_positions
                else:
                    # Generate completely new set of positions
                    new_positions = get_simulated_open_positions(min_usd=50000, count=8)
                    st.session_state["whale_positions"] = new_positions
                
                st.session_state["last_position_update"] = current_time
            
            # Display whale positions
            if st.session_state["whale_positions"]:
                positions_df = pd.DataFrame(st.session_state["whale_positions"])
                
                # Create columns with better proportions
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    # Display the main dataframe with fixed height
                    st.dataframe(
                        positions_df,
                        use_container_width=True,
                        height=350
                    )
                
                with col2:
                    # Create a container with consistent spacing
                    with st.container():
                        summary_title = "📊 Position Summary" if language == 'en' else "📊 Ringkasan Posisi"
                        st.markdown(f"### {summary_title}")
                        
                        # Calculate summary stats
                        total_positions = len(positions_df)
                        long_positions = len(positions_df[positions_df['Side'] == 'LONG'])
                        short_positions = len(positions_df[positions_df['Side'] == 'SHORT'])
                        
                        # Extract numeric values for calculations
                        amounts = []
                        pnl_values = []
                        for _, row in positions_df.iterrows():
                            # Clean amount string
                            amount_str = row['Amount (USD)'].replace('$', '').replace(',', '')
                            amounts.append(float(amount_str))
                            
                            # Clean PnL string
                            pnl_str = row['PnL'].replace('$', '').replace(',', '')
                            pnl_values.append(float(pnl_str))
                        
                        total_value = sum(amounts)
                        total_pnl = sum(pnl_values)
                        
                        # Display metrics with consistent spacing
                        total_pos_label = "Total Positions" if language == 'en' else "Total Posisi"
                        st.metric(total_pos_label, total_positions)
                        st.metric("Long/Short", f"{long_positions}/{short_positions}")
                        
                        total_val_label = "Total Value" if language == 'en' else "Total Nilai"
                        st.metric(total_val_label, f"${total_value:,.0f}")
                        
                        # PnL metric with color indication
                        pnl_delta = f"{(total_pnl/total_value)*100:+.1f}%" if total_value > 0 else "0%"
                        st.metric(
                            "Total PnL", 
                            f"${total_pnl:,.0f}",
                            pnl_delta
                        )
                        
                        # Add some spacing
                        st.markdown("---")
                        
                        # Show last update time
                        if "last_position_update" in st.session_state:
                            last_update = st.session_state["last_position_update"]
                            update_label = "Last updated" if language == 'en' else "Terakhir diperbarui"
                            st.caption(f"🕒 {update_label}: {last_update.strftime('%H:%M:%S')}")
                        
                        # Manual refresh button (optional)
                        refresh_label = "🔄 Force Refresh" if language == 'en' else "🔄 Refresh Paksa"
                        refresh_help = "Force immediate update of positions" if language == 'en' else "Paksa pembaruan posisi segera"
                        if st.button(refresh_label, 
                                    key="refresh_positions", 
                                    use_container_width=True,
                                    help=refresh_help):
                            st.session_state["whale_positions"] = get_simulated_open_positions(min_usd=50000, count=8)
                            st.session_state["last_position_update"] = datetime.now()
                            st.rerun()
            else:
                loading_msg = "🔄 Loading whale positions..." if language == 'en' else "🔄 Memuat posisi whale..."
                st.info(loading_msg)

        # News Section (if enabled)
        if 'news' in enabled_modules:
            news_title = "📰 Latest Crypto News" if language == 'en' else "📰 Berita Crypto Terbaru"
            st.subheader(news_title)
            news = fetch_news()
            
            for item in news:
                with st.expander(item['title']):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        # Clean and display the summary
                        clean_summary = clean_html(item['summary'])
                        st.markdown(clean_summary)
                        
                    with col2:
                        # Add a nice looking "Read More" button
                        read_more_text = "🔗 Read More" if language == 'en' else "🔗 Baca Selengkapnya"
                        st.markdown(
                            f"""
                            <div style='text-align: right; padding: 10px;'>
                            <a href='{item["link"]}' target='_blank'>
                                <button style='
                                    background-color: #4CAF50;
                                    border: none;
                                    color: white;
                                    padding: 10px 20px;
                                    text-align: center;
                                    text-decoration: none;
                                    display: inline-block;
                                    font-size: 14px;
                                    margin: 4px 2px;
                                    cursor: pointer;
                                    border-radius: 4px;
                                '>
                                {read_more_text}
                                </button>
                            </a>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    
                    # Add separator between news items
                    st.markdown("---")

    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        error_msg = "An error occurred while loading the dashboard" if get_user_language() == 'en' else "Terjadi kesalahan saat memuat dashboard"
        st.error(error_msg)

def main():
    """Fungsi utama aplikasi"""
    # Configure page
    st.set_page_config(
        page_title="Dashboard Crypto - FBucket",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Check authentication
    if not check_authentication():
        # Show login page
        show_login_page()
    else:
        # Show protected dashboard
        show_protected_dashboard()

if __name__ == "__main__":
    main()
