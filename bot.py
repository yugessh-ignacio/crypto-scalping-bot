# File: bot.py
import os
import time
from binance.client import Client
from telegram import Bot
from google.oauth2.service_account import Credentials
import gspread

# ================ CONFIG ===================
API_KEY = os.environ['BINANCE_API_KEY']
API_SECRET = os.environ['BINANCE_API_SECRET']
TELEGRAM_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
MASTER_USERNAME = os.environ['MASTER_USERNAME']
FRIEND_USERNAME = os.environ['FRIEND_USERNAME']
GOOGLE_EMAIL = os.environ['GOOGLE_EMAIL']

TRADE_SYMBOL = "BTCUSDT"   # You can rotate
TRADE_QUANTITY = 10        # In USDT
MAX_TRADES = 10

# ================ INIT =====================
client = Client(API_KEY, API_SECRET)
tg_bot = Bot(token=TELEGRAM_TOKEN)

# ========== GOOGLE SHEETS ===============
# You should upload 'credentials.json' to root of repo
creds = Credentials.from_service_account_file("credentials.json", scopes=["https://www.googleapis.com/auth/spreadsheets"])
gc = gspread.authorize(creds)
sh = gc.open("CryptoBot_Trades").sheet1

# ========== MAIN FUNCTION ===============
def simple_strategy():
    ticker = client.get_ticker(symbol=TRADE_SYMBOL)
    price = float(ticker['lastPrice'])
    if price % 2 == 0:
        return "BUY"
    else:
        return "SELL"

def execute_trade():
    side = simple_strategy()
    try:
        order = client.create_test_order(
            symbol=TRADE_SYMBOL,
            side=side,
            type="MARKET",
            quantity=TRADE_QUANTITY
        )
        return side, True
    except Exception as e:
        return str(e), False

def send_report(msg):
    tg_bot.send_message(chat_id=MASTER_USERNAME, text=msg)
    tg_bot.send_message(chat_id=FRIEND_USERNAME, text=msg)

def log_to_sheet(index, side):
    sh.append_row([index, TRADE_SYMBOL, side, time.strftime("%Y-%m-%d %H:%M:%S")])

# ========== LOOP =======================
trade_count = 0
while trade_count < MAX_TRADES:
    decision, status = execute_trade()
    if status:
        trade_count += 1
        msg = f"✅ Trade {trade_count}: {decision} executed on {TRADE_SYMBOL}"
        send_report(msg)
        log_to_sheet(trade_count, decision)
    else:
        send_report(f"❌ Trade Failed: {decision}")
    time.sleep(60)

send_report("🎯 Daily Trade Limit Reached")
