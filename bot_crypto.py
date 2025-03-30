import requests   #to send a request to binance API
import time

def get_crypto_price(symbol):
    """
    Fetches the current price of a cryptocurrency from Binance API.
    """
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
    response = requests.get(url)  #send an HTTP GET request to Binance to retrieve the price data.
    data = response.json()
    return float(data['price'])

def check_alerts(prices):
    """
    Checks if any cryptocurrency price has crossed the predefined high or low threshold.
    """
    alerts = {
        'BTC': {'high': 82613, 'low': 82609},
        'ETH': {'high': 4000, 'low': 1000},
        'SOL': {'high': 290, 'low': 100},
        'TAO': {'high': 500, 'low': 199},
    }
    
    for coin, price in prices.items():
        if price >= alerts[coin]['high']:
            print(f'🚀 ALERT: {coin} has exceeded {alerts[coin]["high"]} USDT! Current price: {price} USDT')
        elif price <= alerts[coin]['low']:
            print(f'📉 ALERT: {coin} has dropped below {alerts[coin]["low"]} USDT! Current price: {price} USDT')

if __name__ == "__main__":
    symbols = ['BTC', 'ETH', 'SOL', 'TAO']
    
    while True:
        # Fetch current prices for all specified cryptocurrencies
        prices = {symbol: get_crypto_price(symbol) for symbol in symbols}
        print(prices)  # Display real-time prices
        check_alerts(prices)  # Check if alerts need to be triggered
        time.sleep(5)  # Wait for 5 seconds before the next request
