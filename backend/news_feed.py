import logging
import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict
import time
import re
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache for news data
NEWS_CACHE = {}
CACHE_DURATION = 300  # 5 minutes

def clean_text(text):
    """Clean text from HTML and extra whitespace"""
    # Remove HTML tags
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text

def fetch_news() -> List[Dict]:
    """
    Fetch cryptocurrency news from multiple sources with caching
    """
    current_time = time.time()
    
    # Check cache first
    if ('data' in NEWS_CACHE and 
        'timestamp' in NEWS_CACHE and 
        current_time - NEWS_CACHE['timestamp'] < CACHE_DURATION):
        logger.info("Using cached news data")
        return NEWS_CACHE['data']
    
    logger.info("Fetching fresh crypto news from multiple sources...")
    
    # Try to fetch from multiple sources
    news_sources = [
        fetch_from_coindesk,
        fetch_from_cointelegraph,
        fetch_from_cryptoslate,
        fetch_from_bitcoin_news,
        fetch_fallback_news
    ]
    
    all_news = []
    successful_sources = 0
    
    for source_func in news_sources:
        try:
            news = source_func()
            if news:
                all_news.extend(news)
                successful_sources += 1
                logger.info(f"Successfully fetched {len(news)} items from {source_func.__name__}")
        except Exception as e:
            logger.warning(f"Failed to fetch from {source_func.__name__}: {str(e)}")
            continue
    
    if all_news:
        # Shuffle and limit to avoid bias towards any source
        random.shuffle(all_news)
        final_news = all_news[:12]  # Show top 12 news items
        
        # Cache successful response
        NEWS_CACHE['data'] = final_news
        NEWS_CACHE['timestamp'] = current_time
        logger.info(f"Successfully aggregated {len(final_news)} news items from {successful_sources} sources")
        return final_news
    
    # If all sources fail, return fallback
    logger.error("All news sources failed, using fallback")
    fallback_news = fetch_fallback_news()
    NEWS_CACHE['data'] = fallback_news
    NEWS_CACHE['timestamp'] = current_time
    return fallback_news

def fetch_from_coindesk() -> List[Dict]:
    """
    Fetch news from CoinDesk RSS feed
    """
    try:
        logger.info("Fetching news from CoinDesk...")
        feed = feedparser.parse("https://www.coindesk.com/arc/outboundfeeds/rss/")
        
        news_items = []
        for entry in feed.entries[:4]:  # Get top 4 stories
            news_items.append({
                'title': clean_text(entry.title),
                'link': entry.link,
                'summary': clean_text(entry.get('summary', 'No summary available')),
                'published': entry.get('published', 'Unknown date'),
                'source': 'CoinDesk'
            })
        
        return news_items
        
    except Exception as e:
        logger.error(f"Error fetching CoinDesk news: {str(e)}")
        raise

def fetch_from_cointelegraph() -> List[Dict]:
    """
    Fetch news from CoinTelegraph RSS feed
    """
    try:
        logger.info("Fetching news from CoinTelegraph...")
        feed = feedparser.parse("https://cointelegraph.com/rss")
        
        news_items = []
        for entry in feed.entries[:4]:  # Get top 4 stories
            news_items.append({
                'title': clean_text(entry.title),
                'link': entry.link,
                'summary': clean_text(entry.get('summary', entry.get('description', 'No summary available'))),
                'published': entry.get('published', 'Unknown date'),
                'source': 'CoinTelegraph'
            })
        
        return news_items
        
    except Exception as e:
        logger.error(f"Error fetching CoinTelegraph news: {str(e)}")
        raise

def fetch_from_cryptoslate() -> List[Dict]:
    """
    Fetch news from CryptoSlate RSS feed
    """
    try:
        logger.info("Fetching news from CryptoSlate...")
        feed = feedparser.parse("https://cryptoslate.com/feed/")
        
        news_items = []
        for entry in feed.entries[:4]:  # Get top 4 stories
            news_items.append({
                'title': clean_text(entry.title),
                'link': entry.link,
                'summary': clean_text(entry.get('summary', entry.get('description', 'No summary available'))),
                'published': entry.get('published', 'Unknown date'),
                'source': 'CryptoSlate'
            })
        
        return news_items
        
    except Exception as e:
        logger.error(f"Error fetching CryptoSlate news: {str(e)}")
        raise

def fetch_from_bitcoin_news() -> List[Dict]:
    """
    Fetch news from Bitcoin.com News RSS feed
    """
    try:
        logger.info("Fetching news from Bitcoin.com...")
        feed = feedparser.parse("https://news.bitcoin.com/feed/")
        
        news_items = []
        for entry in feed.entries[:4]:  # Get top 4 stories
            news_items.append({
                'title': clean_text(entry.title),
                'link': entry.link,
                'summary': clean_text(entry.get('summary', entry.get('description', 'No summary available'))),
                'published': entry.get('published', 'Unknown date'),
                'source': 'Bitcoin.com'
            })
        
        return news_items
        
    except Exception as e:
        logger.error(f"Error fetching Bitcoin.com news: {str(e)}")
        raise

def fetch_fallback_news() -> List[Dict]:
    """
    Return fallback news when RSS feeds are unavailable
    """
    logger.info("Using fallback news data")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    return [
        {
            "title": clean_text("Bitcoin Mencapai Rekor Tertinggi Baru di Tahun 2025"),
            "link": "https://example.com/news1",
            "summary": clean_text("Bitcoin mencapai harga tertinggi sepanjang masa hari ini karena adopsi institusional terus meningkat. Para analis memperkirakan tren bullish akan berlanjut hingga akhir tahun."),
            "published": current_time,
            "source": "Crypto News"
        },
        {
            "title": clean_text("Ethereum 2.0 Siap Diluncurkan dengan Upgrade Besar"),
            "link": "https://example.com/news2",
            "summary": clean_text("Jaringan Ethereum bersiap untuk upgrade paling signifikan dalam sejarahnya. Upgrade ini diharapkan meningkatkan skalabilitas dan mengurangi biaya transaksi secara drastis."),
            "published": current_time,
            "source": "Crypto News"
        },
        {
            "title": clean_text("Regulasi Crypto Baru Diusulkan oleh Pemerintah"),
            "link": "https://example.com/news3",
            "summary": clean_text("Pejabat pemerintah mengusulkan regulasi cryptocurrency baru hari ini yang bertujuan untuk melindungi investor retail sambil mendorong inovasi teknologi blockchain."),
            "published": current_time,
            "source": "Crypto News"
        },
        {
            "title": clean_text("Solana Mengalami Lonjakan Volume Trading Harian"),
            "link": "https://example.com/news4",
            "summary": clean_text("Volume trading Solana meningkat 150% dalam 24 jam terakhir seiring dengan meningkatnya minat terhadap ekosistem DeFi di platform ini."),
            "published": current_time,
            "source": "Crypto News"
        },
        {
            "title": clean_text("Perusahaan Teknologi Besar Mulai Adopsi Blockchain"),
            "link": "https://example.com/news5",
            "summary": clean_text("Beberapa perusahaan teknologi Fortune 500 mengumumkan rencana integrasi teknologi blockchain dalam operasi bisnis mereka, menandai milestone penting untuk adopsi enterprise."),
            "published": current_time,
            "source": "Crypto News"
        },
        {
            "title": clean_text("NFT Gaming Memasuki Era Baru dengan Teknologi AI"),
            "link": "https://example.com/news6",
            "summary": clean_text("Industri gaming NFT mengalami revolusi dengan integrasi kecerdasan buatan, membuka peluang baru untuk gameplay yang lebih immersive dan ekonomi virtual yang berkelanjutan."),
            "published": current_time,
            "source": "Crypto News"
        },
        {
            "title": clean_text("DeFi Protocol Baru Menawarkan Yield Farming Inovatif"),
            "link": "https://example.com/news7",
            "summary": clean_text("Protokol DeFi terbaru memperkenalkan mekanisme yield farming yang revolusioner dengan tingkat keamanan tinggi dan APY yang kompetitif untuk para investor."),
            "published": current_time,
            "source": "Crypto News"
        },
        {
            "title": clean_text("Analisis: Tren Bullish Crypto Akan Berlanjut hingga Q4"),
            "link": "https://example.com/news8",
            "summary": clean_text("Para analis teknikal memproyeksikan tren bullish pasar cryptocurrency akan terus berlanjut hingga kuartal keempat, didorong oleh sentimen positif dan adopsi institusional."),
            "published": current_time,
            "source": "Crypto News"
        }
    ]

def clean_html_tags(text: str) -> str:
    """
    Remove HTML tags from text
    """
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def format_news_for_display(news_items: List[Dict]) -> List[Dict]:
    """
    Format news items for better display
    """
    formatted_news = []
    
    for item in news_items:
        formatted_item = {
            'title': clean_html_tags(item['title']),
            'link': item['link'],
            'summary': clean_html_tags(item['summary'])[:300] + '...' if len(item['summary']) > 300 else clean_html_tags(item['summary']),
            'published': item.get('published', 'Unknown date'),
            'source': item.get('source', 'Unknown source')
        }
        formatted_news.append(formatted_item)
    
    return formatted_news

def get_news_sources_status() -> Dict:
    """
    Get status of all news sources
    """
    sources = {
        'CoinDesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
        'CoinTelegraph': 'https://cointelegraph.com/rss',
        'CryptoSlate': 'https://cryptoslate.com/feed/',
        'Bitcoin.com': 'https://news.bitcoin.com/feed/'
    }
    
    status = {}
    for source_name, url in sources.items():
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                status[source_name] = '✅ Active'
            else:
                status[source_name] = '⚠️ No Data'
        except Exception:
            status[source_name] = '❌ Error'
    
    return status

if __name__ == "__main__":
    # Test the news feed
    print("Testing Multi-Source News Feed...")
    print("-" * 50)
    
    # Test sources status
    print("News Sources Status:")
    sources_status = get_news_sources_status()
    for source, status in sources_status.items():
        print(f"  {source}: {status}")
    print()
    
    # Test news fetching
    news = fetch_news()
    print(f"Total news items fetched: {len(news)}")
    print()
    
    # Show sample news by source
    sources_count = {}
    for item in news:
        source = item['source']
        sources_count[source] = sources_count.get(source, 0) + 1
    
    print("News count by source:")
    for source, count in sources_count.items():
        print(f"  {source}: {count} items")
    print()
    
    # Show first 3 items
    print("Sample news items:")
    for i, item in enumerate(news[:3]):
        print(f"{i+1}. [{item['source']}] {item['title']}")
        print(f"   Summary: {item['summary'][:100]}...")
        print("-" * 50)