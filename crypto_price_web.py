from flask import Flask, jsonify, render_template, request
import requests
import time

app = Flask(__name__)

# Default list of cryptocurrencies
cryptos = ['BTC', 'ETH', 'SOL', 'TAO']

# Data for alerts and price history
alerts_high = {symbol: None for symbol in cryptos}
alerts_low = {symbol: None for symbol in cryptos}
triggered_alerts = {symbol: {'high': False, 'low': False} for symbol in cryptos}
historical_prices = {symbol: [] for symbol in cryptos}

# Import wallet information from wallet.py
from wallet import wallet_holdings, wallet_history, register_wallet_routes

# Telegram configuration (optional)
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
            message = f"🚀 Alert: {symbol} price is above the high threshold! Price: {price} USDT"
            triggered_alerts_messages.append(message)
            send_telegram_message(message)
            print(message)
        if alerts_low.get(symbol) and price <= alerts_low[symbol] and not triggered_alerts[symbol]['low']:
            triggered_alerts[symbol]['low'] = True
            message = f"📉 Alert: {symbol} price is below the low threshold! Price: {price} USDT"
            triggered_alerts_messages.append(message)
            send_telegram_message(message)
            print(message)
    return triggered_alerts_messages

def convert_price(price):
    if isinstance(price, str) and price.strip():
        return float(price.replace(',', '.'))
    return price

# -------------------
# Main routes
# -------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/wallet')
def wallet_page():
    return render_template('wallet.html')

@app.route('/market')
def market_page():
    return render_template("market.html")

@app.route('/market/<symbol>')
def crypto_detail(symbol):
    symbol = symbol.upper()
    # Accept any symbol without strict validation
    return render_template("crypto_detail.html", symbol=symbol)

@app.route('/cryptos')
def get_cryptos():
    return jsonify(cryptos)

@app.route('/prices')
def prices_route():
    prices_dict = get_crypto_prices()
    check_alerts(prices_dict)
    return jsonify(prices_dict)

@app.route('/set-alerts', methods=['POST'])
def set_alerts_route():
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

# -------------------
# Endpoints for the wallet
# -------------------

@app.route('/wallet-holdings')
def wallet_holdings_route():
    return jsonify(wallet_holdings)

@app.route('/update-wallet', methods=['POST'])
def update_wallet_route():
    new_holdings = request.get_json()
    for symbol, value in new_holdings.items():
        try:
            wallet_holdings[symbol.upper()] = float(value)
        except Exception as e:
            pass
    return jsonify({'status': 'success', 'wallet_holdings': wallet_holdings})

# -------------------
# Endpoints for alerts
# -------------------

@app.route('/get-alerts')
def get_alerts_route():
    return jsonify({'alerts_high': alerts_high, 'alerts_low': alerts_low})

@app.route('/clear-alerts', methods=['POST'])
def clear_alerts_route():
    data = request.get_json()
    symbol = data.get('symbol')
    if symbol in alerts_high:
        alerts_high[symbol] = None
        alerts_low[symbol] = None
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Symbol not found'}), 404

# -------------------
# Endpoint to get the price of a cryptocurrency
# -------------------

@app.route('/price/<symbol>')
def price_for_symbol(symbol):
    symbol = symbol.upper()
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({'error': 'Price not available'}), 404
    data = response.json()
    return jsonify({symbol: float(data['price'])})

# -------------------
# Endpoint for Fear & Greed data (simulated data)
# -------------------
@app.route('/fear-greed')
def fear_greed():
    url = "https://api.alternative.me/fng/"
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch Fear & Greed data'}), 500
    data = response.json()
    try:
        # The API returns a list in data["data"]; take the first element
        index_value = int(data["data"][0]["value"])
    except Exception as e:
        index_value = 0
    return jsonify({'fear_greed': index_value})

NEWS_API_KEY = 'YOUR_NEWSAPI_KEY'  # Replace with your NewsAPI key

@app.route('/news')
def news():
    url = 'https://newsapi.org/v2/top-headlines'
    params = {
        'apiKey': NEWS_API_KEY,
        'country': 'fr',  # or 'us', etc.
        'category': 'technology'
    }
    response = requests.get(url, params=params)
    data = response.json()
    articles = [{'title': article['title'], 'url': article['url']} for article in data.get('articles', [])]
    
    # Fallback: if no articles are found, return examples
    if not articles:
        articles = [
            {"title": "Why BTC is going down ?", "url": "https://www.cnbc.com/2025/04/06/bitcoin-drops-sunday-evening-as-cryptocurrencies-join-global-market-rout.html"},
            {"title": "Cryptocurrencies see prices fall amid global market turmoil", "url": "https://apnews.com/article/trump-bitcoin-crypto-tariffs-ether-4b59eeac841cb1dd1b71d7fec14be94e"},
            {"title": "BTC news on X", "url": "https://x.com/bitcoinnewscom?lang=en"}
        ]
    return jsonify({'articles': articles})

# -------------------
# Register additional routes from wallet.py
# -------------------
from wallet import register_wallet_routes
register_wallet_routes(app)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
