# config.py
# إعدادات أداة Osama Honeypot

HOST = '0.0.0.0'
PORT = 2222

LOG_DIR = "logs"
DATA_DIR = "data"

SERVER_KEY_FILE = "osama_honeypot_key"
GEOIP_DB = "data/GeoLite2-City.mmdb"

# إعدادات التلجرام (خليها False دلوقتي)
TELEGRAM_ENABLED = False
TELEGRAM_BOT_TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID = "PUT_YOUR_CHAT_ID_HERE"
