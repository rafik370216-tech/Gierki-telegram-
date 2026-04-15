import os

# Environment Variables and Game Settings

# Telegram Bot Token
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Binance API Configuration
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')

# Database Path
DATABASE_PATH = os.getenv('DATABASE_PATH')

# Bet Limits
MIN_BET_LIMIT = 10  # Minimum bet amount
MAX_BET_LIMIT = 1000  # Maximum bet amount

# Supported Cryptocurrencies
SUPPORTED_CRYPTOS = ['BTC', 'ETH', 'BNB', 'USDT']
