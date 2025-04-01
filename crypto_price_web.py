from flask import Flask, jsonify, render_template, request
import requests
import json

app = Flask(__name__)

# Store alerts (for demo purposes)
alerts_high = {
    'BTC': None,
    'ETH': None,
    'SOL': None,
    'TAO': None,
}

alerts_low = {
    'BTC': None,
    'ETH': None,
    'SOL': None,
    'TAO': None,
}

triggered_alerts = {
    'BTC': {'high': False, 'low': False},
    'ETH': {'high': False, 'low': False},
    'SOL': {'high': False, 'low': False},
    'TAO': {'high': False, 'low': False},
}

# Telegram bot parameters
TELEGRAM_TOKEN = "7787717036:AAH3zANzCy2tbRGzcKb9xj7IyIioT3yh-A4"
CHAT_ID = "974690608"

# Function to send Telegram notifications
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    response = requests.post(url, data=payload)
    return response

# Function to fetch crypto prices
def get_crypto_prices():
    symbols = ['BTC', 'ETH', 'SOL', 'TAO']
    prices = {}
    for symbol in symbols:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
        response = requests.get(url)
        data = response.json()
        prices[symbol] = float(data['price'])
    return prices

# Function to check alerts (high and low)
def check_alerts(prices):
    global triggered_alerts
    triggered_alerts_messages = []
    
    for symbol, price in prices.items():
        # Check high alert
        if alerts_high.get(symbol) and price >= alerts_high[symbol] and not triggered_alerts[symbol]['high']:
            triggered_alerts[symbol]['high'] = True
            message = f"🚀Alert: {symbol} price is above the high threshold! Price: {price} USDT"
            triggered_alerts_messages.append(message)
            send_telegram_message(message)  # Send message to Telegram
            print(message)  # Print the alert in the terminal
        
        # Check low alert
        if alerts_low.get(symbol) and price <= alerts_low[symbol] and not triggered_alerts[symbol]['low']:
            triggered_alerts[symbol]['low'] = True
            message = f"📉Alert: {symbol} price is below the low threshold! Price: {price} USDT"
            triggered_alerts_messages.append(message)
            send_telegram_message(message)  # Send message to Telegram
            print(message)  # Print the alert in the terminal
    
    return triggered_alerts_messages

# Function to handle the conversion of string with commas
def convert_price(price):
    if isinstance(price, str) and price.strip():  # Check if price is a non-empty string
        return float(price.replace(',', '.'))  # Replace commas with dots and convert to float
    return price  # If it's not a valid string, return it as is

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/prices')
def prices():
    prices = get_crypto_prices()
    triggered_alerts_messages = check_alerts(prices)
    return jsonify(prices)

@app.route('/set-alerts', methods=['POST'])
def set_alerts():
    global alerts_high, alerts_low, triggered_alerts
    user_alerts = request.get_json()

    # Convert and safely update the alerts
    alerts_high['BTC'] = convert_price(user_alerts.get('BTC_high', alerts_high['BTC']))
    alerts_high['ETH'] = convert_price(user_alerts.get('ETH_high', alerts_high['ETH']))
    alerts_high['SOL'] = convert_price(user_alerts.get('SOL_high', alerts_high['SOL']))
    alerts_high['TAO'] = convert_price(user_alerts.get('TAO_high', alerts_high['TAO']))

    alerts_low['BTC'] = convert_price(user_alerts.get('BTC_low', alerts_low['BTC']))
    alerts_low['ETH'] = convert_price(user_alerts.get('ETH_low', alerts_low['ETH']))
    alerts_low['SOL'] = convert_price(user_alerts.get('SOL_low', alerts_low['SOL']))
    alerts_low['TAO'] = convert_price(user_alerts.get('TAO_low', alerts_low['TAO']))

    # Reset triggered alerts when alerts are updated
    triggered_alerts = {symbol: {'high': False, 'low': False} for symbol in alerts_high}

    return jsonify({'status': 'success', 'alerts_high': alerts_high, 'alerts_low': alerts_low})

# New route to send custom messages to Telegram from terminal
@app.route('/send-message', methods=['POST'])
def send_message():
    user_message = request.get_json().get('message')
    if user_message:
        send_telegram_message(user_message)
        return jsonify({'status': 'success', 'message': user_message})
    return jsonify({'status': 'error', 'message': 'No message provided'}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5001)
