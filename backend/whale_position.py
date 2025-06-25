import random
import datetime
import logging
from typing import List, Dict, Optional
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Symbols for simulation
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "BNBUSDT", "DOTUSDT", "MATICUSDT", "LINKUSDT"]

def get_simulated_open_positions(min_usd=10000, count=10) -> List[Dict]:
    """
    Generate simulated open positions for whale tracking
    """
    logger.info(f"Generating {count} simulated whale positions...")
    
    positions = []
    current_time = datetime.datetime.now()
    
    for i in range(count):
        # Generate random time within last 2 hours
        time_offset = random.randint(0, 7200)  # 0 to 2 hours in seconds
        position_time = current_time - datetime.timedelta(seconds=time_offset)
        
        # Generate position amount with realistic distribution
        if random.random() < 0.1:  # 10% chance of very large position
            amount = random.randint(min_usd * 10, min_usd * 50)
        elif random.random() < 0.3:  # 30% chance of large position
            amount = random.randint(min_usd * 3, min_usd * 10)
        else:  # 60% chance of regular position
            amount = random.randint(min_usd, min_usd * 3)
        
        # Select symbol with weighted probability (BTC and ETH more common)
        symbol_weights = {
            "BTCUSDT": 0.3,
            "ETHUSDT": 0.25,
            "SOLUSDT": 0.15,
            "ADAUSDT": 0.1,
            "BNBUSDT": 0.08,
            "DOTUSDT": 0.05,
            "MATICUSDT": 0.04,
            "LINKUSDT": 0.03
        }
        
        symbol = random.choices(
            list(symbol_weights.keys()),
            weights=list(symbol_weights.values())
        )[0]
        
        # Generate side with slight bias towards LONG
        side = random.choices(["LONG", "SHORT"], weights=[0.55, 0.45])[0]
        
        # Generate entry price (simulated)
        base_prices = {
            "BTCUSDT": 104000,
            "ETHUSDT": 2500,
            "SOLUSDT": 145,
            "ADAUSDT": 1.2,
            "BNBUSDT": 690,
            "DOTUSDT": 7.8,
            "MATICUSDT": 0.85,
            "LINKUSDT": 15.5
        }
        
        base_price = base_prices.get(symbol, 100)
        price_variation = random.uniform(-0.05, 0.05)  # ±5% variation
        entry_price = base_price * (1 + price_variation)
        
        # Calculate position size in coins
        position_size = amount / entry_price
        
        # Generate leverage (common values in futures)
        leverage = random.choice([1, 2, 3, 5, 10, 20, 25, 50])
        
        # Generate PnL (unrealized)
        pnl_percentage = random.uniform(-0.15, 0.25)  # -15% to +25%
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
            "time": position_time.strftime("%Y-%m-%d %H:%M:%S"),
            "symbol": symbol,
            "side": side,
            "amount_usd": amount,
            "position_size": round(position_size, 6),
            "entry_price": round(entry_price, 6),
            "current_price": round(current_price, 6),
            "leverage": f"{leverage}x",
            "margin_used": round(margin_used, 2),
            "unrealized_pnl": round(unrealized_pnl, 2),
            "pnl_percentage": round(pnl_percentage * 100, 2),
            "liquidation_price": round(liquidation_price, 6),
            "position_id": f"POS_{random.randint(100000, 999999)}",
            "exchange": random.choice(["Binance", "Bybit", "OKX", "Bitget"])
        })
    
    return positions

def get_simulated_recent_trades(min_usd=5000, count=20) -> List[Dict]:
    """
    Generate simulated recent whale trades (closed positions)
    """
    logger.info(f"Generating {count} simulated whale trades...")
    
    trades = []
    current_time = datetime.datetime.now()
    
    for i in range(count):
        # Generate random time within last 4 hours
        time_offset = random.randint(0, 14400)  # 0 to 4 hours in seconds
        trade_time = current_time - datetime.timedelta(seconds=time_offset)
        
        # Generate trade amount
        if random.random() < 0.15:  # 15% chance of very large trade
            amount = random.randint(min_usd * 20, min_usd * 100)
        else:
            amount = random.randint(min_usd, min_usd * 10)
        
        # Select symbol
        symbol_weights = {
            "BTCUSDT": 0.35,
            "ETHUSDT": 0.25,
            "SOLUSDT": 0.15,
            "ADAUSDT": 0.08,
            "BNBUSDT": 0.07,
            "DOTUSDT": 0.04,
            "MATICUSDT": 0.03,
            "LINKUSDT": 0.03
        }
        
        symbol = random.choices(
            list(symbol_weights.keys()),
            weights=list(symbol_weights.values())
        )[0]
        
        # Generate trade type
        trade_type = random.choice(["BUY", "SELL"])
        
        # Generate prices
        base_prices = {
            "BTCUSDT": 104000,
            "ETHUSDT": 2500,
            "SOLUSDT": 145,
            "ADAUSDT": 1.2,
            "BNBUSDT": 690,
            "DOTUSDT": 7.8,
            "MATICUSDT": 0.85,
            "LINKUSDT": 15.5
        }
        
        base_price = base_prices.get(symbol, 100)
        price_variation = random.uniform(-0.03, 0.03)  # ±3% variation
        trade_price = base_price * (1 + price_variation)
        
        # Calculate quantity
        quantity = amount / trade_price
        
        trades.append({
            "time": trade_time.strftime("%Y-%m-%d %H:%M:%S"),
            "symbol": symbol,
            "type": trade_type,
            "amount_usd": amount,
            "quantity": round(quantity, 6),
            "price": round(trade_price, 6),
            "trade_id": f"TRD_{random.randint(1000000, 9999999)}",
            "exchange": random.choice(["Binance", "Coinbase", "Kraken", "Bybit"]),
            "market_impact": round(random.uniform(0.1, 2.5), 2)  # % market impact
        })
    
    return trades

def analyze_whale_activity(positions: List[Dict], trades: List[Dict]) -> Dict:
    """
    Analyze whale activity patterns
    """
    logger.info("Analyzing whale activity patterns...")
    
    # Analyze positions
    total_position_value = sum(pos['amount_usd'] for pos in positions)
    long_positions = [pos for pos in positions if pos['side'] == 'LONG']
    short_positions = [pos for pos in positions if pos['side'] == 'SHORT']
    
    long_value = sum(pos['amount_usd'] for pos in long_positions)
    short_value = sum(pos['amount_usd'] for pos in short_positions)
    
    # Analyze trades
    total_trade_value = sum(trade['amount_usd'] for trade in trades)
    buy_trades = [trade for trade in trades if trade['type'] == 'BUY']
    sell_trades = [trade for trade in trades if trade['type'] == 'SELL']
    
    buy_value = sum(trade['amount_usd'] for trade in buy_trades)
    sell_value = sum(trade['amount_usd'] for trade in sell_trades)
    
    # Symbol analysis
    position_symbols = {}
    trade_symbols = {}
    
    for pos in positions:
        symbol = pos['symbol']
        if symbol not in position_symbols:
            position_symbols[symbol] = {'count': 0, 'value': 0}
        position_symbols[symbol]['count'] += 1
        position_symbols[symbol]['value'] += pos['amount_usd']
    
    for trade in trades:
        symbol = trade['symbol']
        if symbol not in trade_symbols:
            trade_symbols[symbol] = {'count': 0, 'value': 0}
        trade_symbols[symbol]['count'] += 1
        trade_symbols[symbol]['value'] += trade['amount_usd']
    
    return {
        "summary": {
            "total_open_positions": len(positions),
            "total_position_value_usd": total_position_value,
            "long_short_ratio": round(long_value / short_value, 2) if short_value > 0 else "∞",
            "total_recent_trades": len(trades),
            "total_trade_value_usd": total_trade_value,
            "buy_sell_ratio": round(buy_value / sell_value, 2) if sell_value > 0 else "∞"
        },
        "positions": {
            "long_positions": len(long_positions),
            "long_value_usd": long_value,
            "short_positions": len(short_positions),
            "short_value_usd": short_value
        },
        "trades": {
            "buy_trades": len(buy_trades),
            "buy_value_usd": buy_value,
            "sell_trades": len(sell_trades),
            "sell_value_usd": sell_value
        },
        "top_symbols_positions": sorted(position_symbols.items(), 
                                      key=lambda x: x[1]['value'], reverse=True)[:5],
        "top_symbols_trades": sorted(trade_symbols.items(), 
                                   key=lambda x: x[1]['value'], reverse=True)[:5]
    }

def display_whale_report(positions: List[Dict], trades: List[Dict], analysis: Dict):
    """
    Display formatted whale activity report
    """
    print("\n" + "="*80)
    print("🐋 WHALE ACTIVITY MONITORING REPORT")
    print("="*80)
    
    # Summary
    summary = analysis['summary']
    print(f"\n📊 MARKET OVERVIEW:")
    print(f"   Total Open Positions: {summary['total_open_positions']}")
    print(f"   Total Position Value: ${summary['total_position_value_usd']:,}")
    print(f"   Long/Short Ratio: {summary['long_short_ratio']}")
    print(f"   Recent Trades: {summary['total_recent_trades']}")
    print(f"   Total Trade Volume: ${summary['total_trade_value_usd']:,}")
    print(f"   Buy/Sell Ratio: {summary['buy_sell_ratio']}")
    
    # Top positions
    print(f"\n🎯 LARGEST OPEN POSITIONS:")
    sorted_positions = sorted(positions, key=lambda x: x['amount_usd'], reverse=True)[:5]
    for i, pos in enumerate(sorted_positions, 1):
        pnl_emoji = "🟢" if pos['unrealized_pnl'] > 0 else "🔴"
        print(f"   {i}. {pos['symbol']} {pos['side']} - ${pos['amount_usd']:,} "
              f"({pos['leverage']}) {pnl_emoji} {pos['pnl_percentage']}%")
    
    # Recent large trades
    print(f"\n💰 RECENT LARGE TRADES:")
    sorted_trades = sorted(trades, key=lambda x: x['amount_usd'], reverse=True)[:5]
    for i, trade in enumerate(sorted_trades, 1):
        emoji = "🟢" if trade['type'] == 'BUY' else "🔴"
        print(f"   {i}. {trade['symbol']} {trade['type']} - ${trade['amount_usd']:,} "
              f"@ ${trade['price']} {emoji} ({trade['time']})")
    
    # Symbol activity
    print(f"\n📈 TOP SYMBOLS BY ACTIVITY:")
    for i, (symbol, data) in enumerate(analysis['top_symbols_positions'][:3], 1):
        print(f"   {i}. {symbol}: {data['count']} positions, ${data['value']:,} value")

def main():
    """
    Main function to run whale tracking simulation
    """
    print("🐋 Starting Whale Activity Simulation...")
    
    # Generate simulated data
    positions = get_simulated_open_positions(min_usd=10000, count=15)
    trades = get_simulated_recent_trades(min_usd=5000, count=25)
    
    # Analyze data
    analysis = analyze_whale_activity(positions, trades)
    
    # Display report
    display_whale_report(positions, trades, analysis)
    
    # Optional: Save to JSON
    output_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "positions": positions,
        "trades": trades,
        "analysis": analysis
    }
    
    with open(f"whale_activity_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n💾 Data saved to whale_activity_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

if __name__ == "__main__":
    main()