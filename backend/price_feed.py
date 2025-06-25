import requests
import logging
import time
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache for price data
PRICE_CACHE = {}
CACHE_DURATION = 60  # seconds

def get_prices() -> Optional[Dict]:
    """
    Fetch cryptocurrency prices from CoinGecko API with caching and error handling
    """
    current_time = time.time()
    
    # Check cache first
    if ('data' in PRICE_CACHE and 
        'timestamp' in PRICE_CACHE and 
        current_time - PRICE_CACHE['timestamp'] < CACHE_DURATION):
        logger.info("Using cached price data")
        return PRICE_CACHE['data']
    
    logger.info("Fetching fresh crypto prices from CoinGecko...")
    
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin,ethereum,solana,binancecoin,cardano,polkadot",
        "vs_currencies": "usd",
        "include_24hr_change": "true",
        "include_market_cap": "true",
        "include_24hr_vol": "true"
    }
    
    try:
        # Add headers to avoid rate limiting
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Successfully fetched prices for {len(data)} cryptocurrencies")
            
            # Cache the successful response
            PRICE_CACHE['data'] = data
            PRICE_CACHE['timestamp'] = current_time
            
            return data
            
        elif response.status_code == 429:
            logger.warning("Rate limited by CoinGecko API, using fallback data")
            return get_fallback_prices()
            
        else:
            logger.error(f"Failed to fetch prices. Status code: {response.status_code}")
            return get_fallback_prices()
            
    except requests.exceptions.Timeout:
        logger.error("Timeout error when fetching prices")
        return get_fallback_prices()
        
    except requests.exceptions.ConnectionError:
        logger.error("Connection error when fetching prices")
        return get_fallback_prices()
        
    except Exception as e:
        logger.error(f"Unexpected error fetching prices: {str(e)}")
        return get_fallback_prices()

def get_fallback_prices() -> Dict:
    """
    Return fallback price data when API is unavailable
    """
    logger.info("Using fallback price data")
    return {
        "bitcoin": {
            "usd": 104906,
            "usd_24h_change": 2.4,
            "usd_market_cap": 2050000000000,
            "usd_24h_vol": 28000000000
        },
        "ethereum": {
            "usd": 2526.53,
            "usd_24h_change": -0.8,
            "usd_market_cap": 304000000000,
            "usd_24h_vol": 12000000000
        },
        "solana": {
            "usd": 145.74,
            "usd_24h_change": 1.2,
            "usd_market_cap": 69000000000,
            "usd_24h_vol": 2500000000
        },
        "binancecoin": {
            "usd": 692.45,
            "usd_24h_change": 0.5,
            "usd_market_cap": 100000000000,
            "usd_24h_vol": 1800000000
        },
        "cardano": {
            "usd": 1.23,
            "usd_24h_change": -1.5,
            "usd_market_cap": 43000000000,
            "usd_24h_vol": 850000000
        },
        "polkadot": {
            "usd": 7.89,
            "usd_24h_change": 3.2,
            "usd_market_cap": 11000000000,
            "usd_24h_vol": 420000000
        }
    }

def format_price_data(raw_data: Dict) -> Dict:
    """
    Format price data for display
    """
    formatted_data = {}
    
    for coin, data in raw_data.items():
        formatted_data[coin] = {
            'price': f"${data['usd']:,.2f}",
            'change_24h': f"{data.get('usd_24h_change', 0):+.2f}%",
            'market_cap': f"${data.get('usd_market_cap', 0):,.0f}",
            'volume_24h': f"${data.get('usd_24h_vol', 0):,.0f}"
        }
    
    return formatted_data

if __name__ == "__main__":
    # Test the price feed
    prices = get_prices()
    if prices:
        formatted = format_price_data(prices)
        for coin, data in formatted.items():
            print(f"{coin.upper()}: {data}")
    else:
        print("Failed to fetch prices")