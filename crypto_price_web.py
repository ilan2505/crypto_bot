from flask import Flask, jsonify, render_template
import requests
import time

app = Flask(__name__)

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/prices')
def prices():
    return jsonify(get_crypto_prices())

if __name__ == "__main__":
    app.run(debug=True, port=5001)

