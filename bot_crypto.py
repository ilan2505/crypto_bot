import time
import requests    #to send a request to binance API in order to have the btc price

def get_crypto_price(symbol="BTCUSDT"): #can write ETHUSDT, BNBUSDT...
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url)   #send an HTTP GET request to Binance to retrieve the price data.
    data = response.json()    #->json format
    return float(data["price"])

if __name__ == "__main__":
    while True:
        price = get_crypto_price("BTCUSDT")
        print(f"Prix du Bitcoin : {price} USDT")
        time.sleep(5)  # updates every 5s
