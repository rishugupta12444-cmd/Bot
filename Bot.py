# Ye tumhara final Render 24/7 On-Demand Signal Bot code hai
import requests
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BOT_TOKEN = "8361123291:AAE382eKTm5Nr8DzJM2_DkY5pkmUgcShYPg"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

SYMBOL = "BTCUSDT"
INTERVAL = "1m"

last_update_id = None

def send_message(chat_id, text):
    try:
        requests.post(f"{BASE_URL}/sendMessage", data={"chat_id": chat_id, "text": text}, timeout=10)
    except:
        print("Telegram send failed")

def get_prices():
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={SYMBOL}&interval={INTERVAL}&limit=100"
        r = requests.get(url, timeout=10, verify=False).json()
        return [float(c[4]) for c in r]
    except:
        print("Price fetch failed")
        return None

def calc_rsi(prices, period=14):
    gains, losses = [], []
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i-1]
        gains.append(diff if diff > 0 else 0)
        losses.append(-diff if diff < 0 else 0)
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calc_ema(prices, period=20):
    ema = prices[0]
    k = 2 / (period + 1)
    for price in prices[1:]:
        ema = price * k + ema * (1 - k)
    return ema

def generate_signal():
    prices = get_prices()
    if not prices:
        return "⚠️ Market data error"

    rsi = round(calc_rsi(prices), 2)
    ema = round(calc_ema(prices), 2)
    last_price = prices[-1]

    if rsi < 45 and last_price > ema:
        return f"📈 BUY SIGNAL ({SYMBOL} 1M)\nRSI: {rsi}"
    elif rsi > 55 and last_price < ema:
        return f"📉 SELL SIGNAL ({SYMBOL} 1M)\nRSI: {rsi}"
    else:
        return f"⏳ NO CLEAR SIGNAL\nRSI: {rsi}"

def check_updates():
    global last_update_id
    try:
        params = {"timeout": 30, "offset": last_update_id}
        response = requests.get(f"{BASE_URL}/getUpdates", params=params, timeout=35).json()

        for update in response.get("result", []):
            last_update_id = update["update_id"] + 1

            if "message" in update and "text" in update["message"]:
                chat_id = update["message"]["chat"]["id"]
                text = update["message"]["text"]

                if text == "/start":
                    signal = generate_signal()
                    send_message(chat_id, signal)

    except:
        print("Update fetch error")

print("🤖 Stable On-Demand Signal Bot Running...")

while True:
    check_updates()
    time.sleep(3)  # Slow polling prevents Telegram block
