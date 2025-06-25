#!/usr/bin/env python3
"""
Bloomberg Crypto Lokal - Main Runner Script
Memudahkan untuk menjalankan aplikasi dengan berbagai konfigurasi
"""

import os
import sys
import subprocess
import argparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'streamlit',
        'pandas', 
        'requests',
        'streamlit-autorefresh',
        'feedparser'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {', '.join(missing_packages)}")
        logger.info("Please install them using: pip install -r requirements.txt")
        return False
    
    logger.info("All dependencies are installed ✓")
    return True

def create_directories():
    """Create required directories if they don't exist"""
    directories = ['backend', 'ai', 'logs']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")
        
        # Create __init__.py files for Python packages
        if directory in ['backend', 'ai']:
            init_file = os.path.join(directory, '__init__.py')
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    f.write(f'"""{directory.title()} package for Bloomberg Crypto Lokal"""\n')
                logger.info(f"Created {init_file}")

def run_streamlit_app(host='localhost', port=8501, debug=False):
    """Run the Streamlit application"""
    logger.info(f"Starting Bloomberg Crypto Lokal on {host}:{port}")
    
    # Prepare streamlit command
    cmd = [
        'streamlit', 'run', 'app.py',
        '--server.address', host,
        '--server.port', str(port),
        '--server.headless', 'true' if not debug else 'false',
        '--browser.gatherUsageStats', 'false'
    ]
    
    if debug:
        cmd.extend(['--logger.level', 'debug'])
    
    try:
        # Run the command
        process = subprocess.run(cmd, check=True)
        return process.returncode == 0
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start Streamlit: {e}")
        return False
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
        return True

def test_components():
    """Test individual components before running the full app"""
    logger.info("Testing application components...")
    
    try:
        # Test price feed
        logger.info("Testing price feed...")
        from backend.price_feed import get_prices
        prices = get_prices()
        if prices:
            logger.info(f"Price feed working ✓ - Got {len(prices)} cryptocurrencies")
        else:
            logger.warning("Price feed returned no data - will use fallback")
        
        # Test news feed
        logger.info("Testing news feed...")
        from backend.news_feed import fetch_news
        news = fetch_news()
        if news:
            logger.info(f"News feed working ✓ - Got {len(news)} news items")
        else:
            logger.warning("News feed returned no data - will use fallback")
        
        # Test whale tracker
        logger.info("Testing whale tracker...")
        from backend.whale_tracker import get_fake_whale_tx
        whale_tx = get_fake_whale_tx()
        if whale_tx:
            logger.info("Whale tracker working ✓")
        else:
            logger.warning("Whale tracker returned no data")
        
        # Test AI summarizer
        logger.info("Testing AI summarizer...")
        from ai.summarize import summarize
        test_text = "This is a test text for summarization functionality."
        summary = summarize(test_text)
        if summary:
            logger.info("AI summarizer working ✓")
        else:
            logger.warning("AI summarizer returned no data")
        
        logger.info("All component tests completed ✓")
        return True
        
    except ImportError as e:
        logger.error(f"Import error during testing: {e}")
        return False
    except Exception as e:
        logger.error(f"Error during component testing: {e}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Bloomberg Crypto Lokal Runner')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8501, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--test', action='store_true', help='Test components only')
    parser.add_argument('--setup', action='store_true', help='Setup directories and dependencies')
    
    args = parser.parse_args()
    
    logger.info("🚀 Bloomberg Crypto Lokal - Starting up...")
    
    # Setup phase
    if args.setup or not os.path.exists('backend') or not os.path.exists('ai'):
        logger.info("Setting up project structure...")
        create_directories()
    
    # Dependency check
    if not check_dependencies():
        logger.error("❌ Dependency check failed. Please install requirements.")
        sys.exit(1)
    
    # Test components if requested
    if args.test:
        if test_components():
            logger.info("✅ All tests passed!")
            sys.exit(0)
        else:
            logger.error("❌ Some tests failed!")
            sys.exit(1)
    
    # Run the application
    try:
        logger.info("🎯 Starting Streamlit application...")
        success = run_streamlit_app(args.host, args.port, args.debug)
        
        if success:
            logger.info("✅ Application finished successfully")
        else:
            logger.error("❌ Application failed to start")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()