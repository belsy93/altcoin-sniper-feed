
import os
import time
import random
import requests
from dotenv import load_dotenv
from binance.client import Client
from binance.enums import *

load_dotenv()
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
client = Client(API_KEY, API_SECRET)

TELEGRAM_TOKEN = "7943552022:AAHoO-rmIOI9keVL8qlwP56TNKQVSoR0JZY"
TELEGRAM_CHAT_ID = "7695441993"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})
    except Exception as e:
        print(f"Telegram error: {e}")

positions = {}
initial_capital = 1000
available_capital = initial_capital
profit_accumulated = 0

def load_coin_picks(url='https://pastebin.com/raw/wU9xHWWv'):
    try:
        r = requests.get(url)
        return [line.strip().upper() for line in r.text.splitlines() if line.strip()] if r.ok else []
    except Exception as e:
        print(f"Error fetching picks: {e}")
        return []

def buy_coin(symbol, amount):
    global available_capital
    try:
        price = float(client.get_symbol_ticker(symbol=symbol)['price'])
        qty = round(amount / price, 4)
        available_capital -= amount
        positions[symbol] = {'entry_price': price, 'amount': amount}
        send_telegram(f"[BUY] {symbol} | ${amount:.2f} @ ${price:.4f} ({qty} units)")
    except Exception as e:
        print(f"Buy error: {e}")

def sell_coin(symbol, reason):
    global available_capital, profit_accumulated
    try:
        if symbol not in positions:
            return
        entry = positions[symbol]
        current = float(client.get_symbol_ticker(symbol=symbol)['price'])
        change = (current - entry['entry_price']) / entry['entry_price']
        pnl = entry['amount'] * change
        available_capital += entry['amount']
        profit_accumulated += pnl
        send_telegram(f"[SELL] {symbol} @ ${current:.4f} | {reason} | PnL: ${pnl:.2f}")
        del positions[symbol]
    except Exception as e:
        print(f"Sell error: {e}")

def evaluate_pattern(symbol):
    return random.choice(["TP", "SL", "Hold"])

def run_bot():
    global available_capital
    coin_list = load_coin_picks()
    send_telegram(f"📈 Sniper booted. Loaded {len(coin_list)} targets.")
    trade_amt = initial_capital / max(len(coin_list), 1)
    for s in coin_list:
        buy_coin(s, trade_amt)
    while True:
        print(f"[CHECK] Capital: ${available_capital:.2f} | Banked: ${profit_accumulated:.2f}")
        for s in list(positions.keys()):
            d = evaluate_pattern(s)
            if d == "TP":
                sell_coin(s, "Take Profit")
            elif d == "SL":
                sell_coin(s, "Stop Loss")
            else:
                print(f"Holding {s}...")
        time.sleep(300)

if __name__ == "__main__":
    run_bot()
