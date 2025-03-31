import requests
import time

# Telegram bot credentials (replace with your values)
TELEGRAM_BOT_TOKEN = "7787717036:AAH3zANzCy2tbRGzcKb9xj7IyIioT3yh-A4"
TELEGRAM_CHAT_ID = "974690608"

def send_telegram_message(message):
    """
    Sends an alert message to a Telegram chat using a bot.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=payload)

def get_crypto_price(symbol):
    """
    Fetches the current price of a cryptocurrency from Binance API.
    """
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
    response = requests.get(url)
    data = response.json()
    return float(data['price'])

def check_alerts(prices, triggered_alerts):
    """
    Checks if any cryptocurrency price has crossed the predefined high or low threshold
    and ensures that the alert is triggered only once per crossing.
    """
    alerts = {
        'BTC': {'high': 82100, 'low': 82170},
        'ETH': {'high': 1803, 'low': 1799},
        'SOL': {'high': 290, 'low': 100},
        'TAO': {'high': 500, 'low': 199},
    }

    for coin, price in prices.items():
        if price >= alerts[coin]['high'] and not triggered_alerts[coin]['high']:
            message = f'🚀 ALERT: {coin} has exceeded {alerts[coin]["high"]} USDT! Current price: {price} USDT'
            print(message)
            send_telegram_message(message)  # Send Telegram alert
            triggered_alerts[coin]['high'] = True  # Mark alert as sent

        elif price <= alerts[coin]['low'] and not triggered_alerts[coin]['low']:
            message = f'📉 ALERT: {coin} has dropped below {alerts[coin]["low"]} USDT! Current price: {price} USDT'
            print(message)
            send_telegram_message(message)  # Send Telegram alert
            triggered_alerts[coin]['low'] = True  # Mark alert as sent

        # Reset the alert flag when the price moves back inside the range
        elif price < alerts[coin]['high'] and triggered_alerts[coin]['high']:
            triggered_alerts[coin]['high'] = False
        elif price > alerts[coin]['low'] and triggered_alerts[coin]['low']:
            triggered_alerts[coin]['low'] = False

if __name__ == "__main__":
    symbols = ['BTC', 'ETH', 'SOL', 'TAO']
    triggered_alerts = {
        'BTC': {'high': False, 'low': False},
        'ETH': {'high': False, 'low': False},
        'SOL': {'high': False, 'low': False},
        'TAO': {'high': False, 'low': False},
    }

    while True:
        # Fetch current prices for all specified cryptocurrencies
        prices = {symbol: get_crypto_price(symbol) for symbol in symbols}
        print(prices)  # Display real-time prices
        check_alerts(prices, triggered_alerts)  # Check if alerts need to be triggered
        time.sleep(5)  # Wait for 5 seconds before the next request
