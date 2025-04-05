from flask import Flask, jsonify, render_template, request
import requests
import json
import time

app = Flask(__name__)

# List of supported cryptos
cryptos = ['BTC', 'ETH', 'SOL', 'TAO']

# Store alerts
alerts_high = {symbol: None for symbol in cryptos}
alerts_low = {symbol: None for symbol in cryptos}
triggered_alerts = {symbol: {'high': False, 'low': False} for symbol in cryptos}
historical_prices = {symbol: [] for symbol in cryptos}

# Telegram bot configuration
TELEGRAM_TOKEN = "7787717036:AAH3zANzCy2tbRGzcKb9xj7IyIioT3yh-A4"
CHAT_ID = "974690608"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message}
    response = requests.post(url, data=payload)
    return response

def get_crypto_prices():
    prices = {}
    for symbol in cryptos:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
        response = requests.get(url)
        data = response.json()
        prices[symbol] = float(data['price'])
        historical_prices[symbol].append({'time': time.time(), 'price': prices[symbol]})
    return prices

def check_alerts(prices):
    global triggered_alerts
    triggered_alerts_messages = []
    for symbol, price in prices.items():
        if alerts_high.get(symbol) and price >= alerts_high[symbol] and not triggered_alerts[symbol]['high']:
            triggered_alerts[symbol]['high'] = True
            message = f"🚀Alert: {symbol} price is above the high threshold! Price: {price} USDT"
            triggered_alerts_messages.append(message)
            send_telegram_message(message)
            print(message)
        if alerts_low.get(symbol) and price <= alerts_low[symbol] and not triggered_alerts[symbol]['low']:
            triggered_alerts[symbol]['low'] = True
            message = f"📉Alert: {symbol} price is below the low threshold! Price: {price} USDT"
            triggered_alerts_messages.append(message)
            send_telegram_message(message)
            print(message)
    return triggered_alerts_messages

def convert_price(price):
    if isinstance(price, str) and price.strip():
        return float(price.replace(',', '.'))
    return price

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cryptos')
def get_cryptos():
    return jsonify(cryptos)

@app.route('/prices')
def prices():
    prices = get_crypto_prices()
    triggered_alerts_messages = check_alerts(prices)
    return jsonify(prices)

@app.route('/set-alerts', methods=['POST'])
def set_alerts():
    global alerts_high, alerts_low, triggered_alerts
    user_alerts = request.get_json()
    for symbol in cryptos:
        alerts_high[symbol] = convert_price(user_alerts.get(f'{symbol}_high', alerts_high[symbol]))
        alerts_low[symbol] = convert_price(user_alerts.get(f'{symbol}_low', alerts_low[symbol]))
    triggered_alerts = {symbol: {'high': False, 'low': False} for symbol in cryptos}
    return jsonify({'status': 'success', 'alerts_high': alerts_high, 'alerts_low': alerts_low})

@app.route('/send-message', methods=['POST'])
def send_message():
    user_message = request.get_json().get('message')
    if user_message:
        send_telegram_message(user_message)
        return jsonify({'status': 'success', 'message': user_message})
    return jsonify({'status': 'error', 'message': 'No message provided'}), 400

@app.route('/chart-data/<symbol>/<interval>')
def get_chart_data(symbol, interval):
    symbol = symbol.upper()
    if symbol not in cryptos:
        return jsonify({'error': 'Invalid crypto symbol'}), 400

    interval_map = {
        "1m": "1m",
        "30m": "30m",
        "1h": "1h",
        "4h": "4h",
        "1d": "1d",
        "1w": "1w",
        "1M": "1M"
    }
    binance_interval = interval_map.get(interval, "1m")
    limit = 100
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}USDT&interval={binance_interval}&limit={limit}"
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch candlestick data'}), 500

    klines = response.json()
    data = {
        'times': [k[0] for k in klines],
        'opens': [float(k[1]) for k in klines],
        'highs': [float(k[2]) for k in klines],
        'lows': [float(k[3]) for k in klines],
        'closes': [float(k[4]) for k in klines]
    }
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
