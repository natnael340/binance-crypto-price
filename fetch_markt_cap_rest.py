import requests
import csv
from time import sleep


# Define the API endpoint
API_ENDPOINT = "https://api.binance.com/api/v3/ticker/24hr"

SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "DOTUSDT", "UNIUSDT", "LINKUSDT", "LTCUSDT"]
# Define the parameters for the API request
params = {
    'symbol': '',
}

# Define a function to fetch the price data and return it as JSON
def get_price_data():
    # Send the API request
    candlestick_data = {}
    for symbol in SYMBOLS:
        params['symbol'] = symbol
        response = requests.get(API_ENDPOINT, params=params)
        if response.status_code == 200:
            # Extract the price data from the response
            data = response.json()
           
            candlestick_data[symbol] = float(data['lastPrice']) * float(data['quoteVolume'])
            sleep(3)

    return candlestick_data

# Define a function to write the price data to a CSV file
def write_to_csv(data):
    with open('market_cap_data.csv', 'w+', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=SYMBOLS)
        if csvfile.tell() == 0:
            writer.writeheader()
            writer.writerow(data)

def fetch_mc_data():
    # Fetch the price data and write it to the CSV file

    data = get_price_data()
    if data:
        write_to_csv(data)

