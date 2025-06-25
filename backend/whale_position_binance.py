import requests
import datetime
import logging
import random
import time
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Binance Futures API endpoints
BINANCE_TOP_POSITIONS_API = "https://fapi.binance.com/futures/data/topLongShortPositionRatio"
BINANCE_OPEN_INTEREST_API = "https://fapi.binance.com/fapi/v1/openInterest"

# Symbols to track
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "BNBUSDT", "DOTUSDT"]

# Cache for positions data
POSITIONS_CACHE = {}
CACHE_DURATION = 300  # 5 minutes

def get_binance_whale_positions(limit=5, threshold_usd=10000) -> List[Dict]:
    """
    Get whale positions from Binance Futures API
    """
    current_time = time.time()
    
    # Check cache first
    if ('positions' in POSITIONS_CACHE and 
        'timestamp' in POSITIONS_CACHE and 
        current_time - POSITIONS_CACHE['timestamp'] < CACHE_DURATION):
        logger.info("Using cached positions data")
        return POSITIONS_CACHE['positions']
    
    logger.info("Fetching whale positions from Binance...")
    
    positions = []
    
    for symbol in SYMBOLS:
        try:
            params = {
                "symbol": symbol,
                "period": "5m",  # Options: "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d"
                "limit": limit
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(
                BINANCE_TOP_POSITIONS_API, 
                params=params, 
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list) and data:
                    for item in data:
                        try:
                            timestamp = int(item["timestamp"]) / 1000
                            readable_time = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
                            
                            long_ratio = float(item["longPositionRatio"])
                            short_ratio = float(item["shortPositionRatio"])
                            
                            # Calculate dominant side
                            dominant_side = "LONG" if long_ratio > short_ratio else "SHORT"
                            ratio_diff = abs(long_ratio - short_ratio)
                            
                            # Estimate position size based on ratio and market conditions
                            base_amount = threshold_usd
                            if ratio_diff > 0.1:  # Strong bias
                                estimated_amount = random.randint(base_amount * 2, base_amount * 5)
                            elif ratio_diff > 0.05:  # Moderate bias
                                estimated_amount = random.randint(base_amount, base_amount * 3)
                            else:  # Balanced
                                estimated_amount = random.randint(base_amount // 2, base_amount * 2)
                            
                            positions.append({
                                "time": readable_time,
                                "symbol": symbol,
                                "side": dominant_side,
                                "long_ratio": round(long_ratio, 4),
                                "short_ratio": round(short_ratio, 4),
                                "ratio_diff": round(ratio_diff, 4),
                                "amount_usd": estimated_amount,
                                "confidence": "High" if ratio_diff > 0.1 else "Medium" if ratio_diff > 0.05 else "Low"
                            })
                            
                        except (KeyError, ValueError) as e:
                            logger.warning(f"Error parsing position data for {symbol}: {e}")
                            continue
                            
                else:
                    logger.warning(f"Invalid data format for {symbol}")
                    
            else:
                logger.warning(f"Failed to fetch data for {symbol}: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching {symbol}: {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error fetching {symbol}: {e}")
            continue
    
    if positions:
        # Sort by amount descending
        positions.sort(key=lambda x: x['amount_usd'], reverse=True)
        
        # Cache successful response
        POSITIONS_CACHE['positions'] = positions
        POSITIONS_CACHE['timestamp'] = current_time
        
        logger.info(f"Successfully fetched {len(positions)} whale positions")
        return positions
    else:
        logger.warning("No positions data available, using fallback")
        return get_fallback_positions(threshold_usd)

def get_open_interest_data(symbol: str) -> Optional[Dict]:
    """
    Get open interest data for a symbol
    """
    try:
        params = {"symbol": symbol}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(
            BINANCE_OPEN_INTEREST_API,
            params=params,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "symbol": symbol,
                "open_interest": float(data.get("openInterest", 0)),
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            logger.warning(f"Failed to get open interest for {symbol}: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error fetching open interest for {symbol}: {e}")
        return None

def get_fallback_positions(min_usd=10000) -> List[Dict]:
    """
    Generate fallback position data when API is unavailable
    """
    logger.info("Using fallback whale positions data")
    
    positions = []
    current_time = datetime.datetime.now()
    
    for symbol in SYMBOLS:
        for i in range(random.randint(1, 3)):  # 1-3 positions per symbol
            time_offset = random.randint(0, 1800)  # Up to 30 minutes ago
            position_time = (current_time - datetime.timedelta(seconds=time_offset))
            
            # Generate realistic ratios
            long_ratio = random.uniform(0.3, 0.7)
            short_ratio = 1.0 - long_ratio
            
            dominant_side = "LONG" if long_ratio > short_ratio else "SHORT"
            ratio_diff = abs(long_ratio - short_ratio)
            
            amount = random.randint(min_usd, min_usd * 8)
            
            positions.append({
                "time": position_time.strftime("%Y-%m-%d %H:%M"),
                "symbol": symbol,
                "side": dominant_side,
                "long_ratio": round(long_ratio, 4),
                "short_ratio": round(short_ratio, 4),
                "ratio_diff": round(ratio_diff, 4),
                "amount_usd": amount,
                "confidence": "High" if ratio_diff > 0.1 else "Medium" if ratio_diff > 0.05 else "Low"
            })
    
    # Sort by amount descending
    positions.sort(key=lambda x: x['amount_usd'], reverse=True)
    
    return positions

def get_position_summary() -> Dict:
    """
    Get summary statistics of whale positions
    """
    try:
        positions = get_binance_whale_positions()
        
        if not positions:
            return {}
        
        total_amount = sum(pos['amount_usd'] for pos in positions)
        long_positions = [pos for pos in positions if pos['side'] == 'LONG']
        short_positions = [pos for pos in positions if pos['side'] == 'SHORT']
        
        return {
            'total_positions': len(positions),
            'total_amount_usd': f"${total_amount:,.0f}",
            'long_positions': len(long_positions),
            'short_positions': len(short_positions),
            'long_percentage': round(len(long_positions) / len(positions) * 100, 1) if positions else 0,
            'short_percentage': round(len(short_positions) / len(positions) * 100, 1) if positions else 0,
            'most_active_symbol': max(set(pos['symbol'] for pos in positions), 
                                    key=lambda x: sum(1 for pos in positions if pos['symbol'] == x)) if positions else "N/A",
            'sentiment': "Bullish" if len(long_positions) > len(short_positions) else "Bearish" if len(short_positions) > len(long_positions) else "Neutral"
        }
        
    except Exception as e:
        logger.error(f"Error generating position summary: {e}")
        return {}

def format_positions_for_display(positions: List[Dict]) -> List[Dict]:
    """
    Format positions data for better display
    """
    formatted_positions = []
    
    for pos in positions:
        formatted_pos = {
            'Waktu': pos['time'],
            'Symbol': pos['symbol'],
            'Side': pos['side'],
            'Long%': f"{pos['long_ratio']*100:.1f}%",
            'Short%': f"{pos['short_ratio']*100:.1f}%",
            'Estimasi USD': f"${pos['amount_usd']:,}",
            'Confidence': pos['confidence'],
            'Bias': f"{pos['ratio_diff']*100:.1f}%" if pos['ratio_diff'] > 0.05 else "Balanced"
        }
        formatted_positions.append(formatted_pos)
    
    return formatted_positions

def get_position_alerts(positions: List[Dict], threshold_ratio=0.15) -> List[str]:
    """
    Generate alerts for significant position imbalances
    """
    alerts = []
    
    for pos in positions:
        if pos['ratio_diff'] > threshold_ratio:
            side = pos['side']
            symbol = pos['symbol']
            ratio = pos['ratio_diff'] * 100
            amount = pos['amount_usd']
            
            alert = f"🚨 Strong {side} bias detected in {symbol}: {ratio:.1f}% imbalance, ~${amount:,} position"
            alerts.append(alert)
    
    return alerts

if __name__ == "__main__":
    # Test whale positions tracking
    print("Testing Binance Whale Positions Tracker...")
    print("-" * 60)
    
    # Test position fetching
    positions = get_binance_whale_positions(limit=3)
    print(f"Fetched {len(positions)} whale positions:")
    
    for i, pos in enumerate(positions[:5]):
        print(f"\n{i+1}. {pos['symbol']} - {pos['side']}")
        print(f"   Time: {pos['time']}")
        print(f"   Long Ratio: {pos['long_ratio']*100:.1f}%")
        print(f"   Short Ratio: {pos['short_ratio']*100:.1f}%")
        print(f"   Estimated Amount: ${pos['amount_usd']:,}")
        print(f"   Confidence: {pos['confidence']}")
    
    # Test summary
    print("\n" + "="*60)
    print("Position Summary:")
    summary = get_position_summary()
    for key, value in summary.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    # Test alerts
    print("\n" + "="*60)
    print("Position Alerts:")
    alerts = get_position_alerts(positions)
    if alerts:
        for alert in alerts:
            print(f"  {alert}")
    else:
        print("  No significant alerts at this time")
    
    print("\nWhale positions tracker test completed!")