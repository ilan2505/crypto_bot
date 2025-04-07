from flask import jsonify
import requests
import time

# Default list of supported cryptocurrencies
cryptos = ['BTC', 'ETH', 'SOL', 'TAO']

# Simulation of wallet holdings (to be adapted according to your actual data)
wallet_holdings = {
    'BTC': 0.5,
    'ETH': 5,
    'SOL': 30,
    'TAO': 10
}

# History for the chart (timestamps in seconds and total value)
wallet_history = {
    'times': [],
    'values': []
}

def get_crypto_prices():
    """
    Fetches the current prices of each cryptocurrency via the Binance API.
    """
    prices = {}
    for symbol in cryptos:
        try:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
            response = requests.get(url)
            data = response.json()
            prices[symbol] = float(data['price'])
        except Exception as e:
            prices[symbol] = 0.0
    return prices

def register_wallet_routes(app):
    """
    Registers the /wallet-data route on the passed Flask app object.
    """
    @app.route('/wallet-data')
    def wallet_data():
        prices = get_crypto_prices()
        total_value = 0
        crypto_values = {}
        for symbol in cryptos:
            # Value for each crypto = quantity held * current price
            value = wallet_holdings.get(symbol, 0) * prices.get(symbol, 0)
            crypto_values[symbol] = value
            total_value += value

        # Calculate the percentage breakdown for each crypto
        breakdown = {}
        for symbol, value in crypto_values.items():
            breakdown[symbol] = (value / total_value) * 100 if total_value > 0 else 0

        # Update the history
        current_time = time.time()
        wallet_history['times'].append(current_time)
        wallet_history['values'].append(total_value)

        data = {
            'total_wallet_value': total_value,
            'breakdown': breakdown,
            'history': wallet_history
        }
        return jsonify(data)
