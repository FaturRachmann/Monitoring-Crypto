import random
from datetime import datetime, timedelta
import secrets
import logging
from typing import Dict, Optional, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Whale transaction templates for more realistic data
WHALE_TEMPLATES = [
    {
        'tokens': ['BTC', 'ETH', 'SOL', 'BNB', 'ADA', 'DOT'],
        'exchanges': ['Binance', 'Coinbase', 'Kraken', 'OKX', 'Bybit', 'Huobi'],
        'types': ['Buy', 'Sell', 'Transfer'],
        'min_amount': 100,
        'max_amount': 10000
    }
]

def generate_realistic_whale_address(token: str) -> str:
    """Generate realistic-looking wallet addresses for different tokens"""
    if token in ['BTC']:
        # Bitcoin address format
        return f"bc1{secrets.token_hex(15)}...{secrets.token_hex(4)}"
    elif token in ['ETH', 'BNB']:
        # Ethereum-style address
        return f"0x{secrets.token_hex(4)}...{secrets.token_hex(4)}"
    elif token == 'SOL':
        # Solana address format
        return f"{secrets.token_hex(6)}...{secrets.token_hex(4)}"
    else:
        # Generic format
        return f"0x{secrets.token_hex(4)}...{secrets.token_hex(4)}"

def calculate_transaction_value(token: str, amount: int) -> str:
    """Calculate approximate USD value based on current market prices"""
    # Approximate prices (in production, get from price_feed)
    token_prices = {
        'BTC': 104906,
        'ETH': 2526,
        'SOL': 145,
        'BNB': 692,
        'ADA': 1.23,
        'DOT': 7.89
    }
    
    price = token_prices.get(token, 100)
    total_value = amount * price
    
    if total_value >= 1_000_000:
        return f"${total_value/1_000_000:.1f}M"
    elif total_value >= 1_000:
        return f"${total_value/1_000:.1f}K"
    else:
        return f"${total_value:.2f}"

def get_transaction_impact(token: str, transaction_type: str, amount: int) -> str:
    """Determine market impact level"""
    if amount > 5000:
        return "🔴 High Impact"
    elif amount > 1000:
        return "🟡 Medium Impact"
    else:
        return "🟢 Low Impact"

def get_fake_whale_tx() -> Optional[Dict]:
    """Generate realistic whale transaction data"""
    logger.info("Generating whale transaction...")
    
    try:
        template = WHALE_TEMPLATES[0]
        
        # Select random parameters
        token = random.choice(template['tokens'])
        tx_type = random.choice(template['types'])
        exchange = random.choice(template['exchanges'])
        
        # Generate amount based on token (different ranges for different tokens)
        if token == 'BTC':
            amount = random.randint(50, 2000)
        elif token == 'ETH':
            amount = random.randint(200, 5000)
        elif token in ['SOL', 'BNB']:
            amount = random.randint(500, 10000)
        else:
            amount = random.randint(1000, 50000)
        
        # Generate transaction details
        wallet_address = generate_realistic_whale_address(token)
        tx_value = calculate_transaction_value(token, amount)
        impact = get_transaction_impact(token, tx_type, amount)
        
        # Add some randomness to timing
        time_offset = random.randint(0, 300)  # Up to 5 minutes ago
        tx_time = (datetime.now() - timedelta(seconds=time_offset)).strftime('%H:%M:%S')
        
        transaction = {
            'Waktu': tx_time,
            'Tipe': tx_type,
            'Token': token,
            'Jumlah': f"{amount:,}",
            'Nilai USD': tx_value,
            'Impact': impact,
            'Exchange': exchange,
            'Wallet': wallet_address,
            'Hash': f"0x{secrets.token_hex(8)}...{secrets.token_hex(4)}"
        }
        
        logger.info(f"Generated whale transaction: {token} {tx_type} for {tx_value}")
        return transaction
        
    except Exception as e:
        logger.error(f"Error generating whale transaction: {str(e)}")
        return None

def get_whale_statistics() -> Dict:
    """Get whale transaction statistics for the dashboard"""
    try:
        return {
            'total_transactions_24h': random.randint(150, 300),
            'total_volume_24h': f"${random.randint(500, 1200)}M",
            'largest_transaction': f"${random.randint(50, 200)}M BTC",
            'most_active_token': random.choice(['BTC', 'ETH', 'SOL']),
            'whale_sentiment': random.choice(['Bullish', 'Bearish', 'Neutral'])
        }
    except Exception as e:
        logger.error(f"Error getting whale statistics: {str(e)}")
        return {}

def generate_whale_alert(transaction: Dict) -> str:
    """Generate whale alert message"""
    try:
        token = transaction['Token']
        tx_type = transaction['Tipe']
        amount = transaction['Jumlah']
        value = transaction['Nilai USD']
        exchange = transaction['Exchange']
        
        alerts = [
            f"🚨 WHALE ALERT: Large {tx_type.lower()} detected! {amount} {token} ({value}) on {exchange}",
            f"🐋 Big Move: {amount} {token} worth {value} just {tx_type.lower()}ed on {exchange}",
            f"📈 Whale Activity: {value} {token} {tx_type.lower()} transaction spotted on {exchange}",
        ]
        
        return random.choice(alerts)
        
    except Exception as e:
        logger.error(f"Error generating whale alert: {str(e)}")
        return "🚨 Whale transaction detected!"

def get_historical_whale_data(hours: int = 24) -> List[Dict]:
    """Generate historical whale transaction data for analysis"""
    logger.info(f"Generating {hours}h of historical whale data...")
    
    try:
        historical_data = []
        transactions_per_hour = random.randint(5, 15)
        
        for hour in range(hours):
            for _ in range(random.randint(1, transactions_per_hour)):
                # Generate timestamp for this hour
                time_ago = datetime.now() - timedelta(hours=hour, 
                                                    minutes=random.randint(0, 59))
                
                tx = get_fake_whale_tx()
                if tx:
                    tx['Waktu'] = time_ago.strftime('%Y-%m-%d %H:%M:%S')
                    historical_data.append(tx)
        
        logger.info(f"Generated {len(historical_data)} historical transactions")
        return historical_data
        
    except Exception as e:
        logger.error(f"Error generating historical data: {str(e)}")
        return []

if __name__ == "__main__":
    # Test whale transaction generation
    print("Testing Whale Transaction Generator...")
    print("-" * 50)
    
    # Generate 5 sample transactions
    for i in range(5):
        tx = get_fake_whale_tx()
        if tx:
            print(f"Transaction {i+1}:")
            for key, value in tx.items():
                print(f"  {key}: {value}")
            print()
    
    # Test statistics
    stats = get_whale_statistics()
    print("Whale Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\nWhale tracker test completed successfully!")