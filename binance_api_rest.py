import requests
import csv
from time import sleep


# Define the API endpoint
API_ENDPOINT = "https://api.binance.com/api/v3/klines"

SYMBOLS = ["BTCUSDT", "ETHUSDT", "ADAUSDT"]
# Define the parameters for the API request
params = {
    'symbol': '',
    'interval': '1h',
    'limit': 1
}

# Define a function to fetch the price data and return it as JSON
def get_price_data():
    # Send the API request
    candlestick_array = []
    for symbol in SYMBOLS:
        params['symbol'] = symbol
        response = requests.get(API_ENDPOINT, params=params)
        if response.status_code == 200:
            # Extract the price data from the response
            data = response.json()[0]
            candlestick_data = {
                'open_time': data[0],
                'open': data[1],
                'high': data[2],
                'low': data[3],
                'close': data[4],
                'volume': data[5],
                'close_time': data[6],
                'quote_asset_volume': data[7],
                'number_of_trades': data[8],
                'taker_buy_base_asset_volume': data[9],
                'taker_buy_quote_asset_volume': data[10],
                'ignore': data[11],
                'symbol': symbol,
            }
            candlestick_array.append(candlestick_data)
            sleep(3)

    return candlestick_array

# Define a function to write the price data to a CSV file
def write_to_csv(data_array):
    with open('candlestick_data.csv', 'a+', newline='') as csvfile:
        fieldnames = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore', 'symbol',]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if csvfile.tell() == 0:
            writer.writeheader()
        for data in data_array:
            writer.writerow(data)

def fetch_data():
    # Fetch the price data and write it to the CSV file

    data = get_price_data()
    
    if data:
        write_to_csv(data)


fetch_data()