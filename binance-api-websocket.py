import websocket
import json
import threading
import time
import requests
import csv
import json

# Set the Binance API WebSocket endpoint
socket_endpoint = "wss://stream.binance.com:9443/ws"

# Define the message to send to the WebSocket
subscribe_message = {
    "method": "SUBSCRIBE",
    "params": [
        "btcusdt@kline_1h",
        "ethusdt@kline_1h"
    ],
    "id": 1
}

# Define the callback function for handling the WebSocket messages
def on_message(ws, message):
    data = json.loads(message)
    candlestick_data = data['k']
    # Write candlestick data to CSV file
    with open('candlestick_data.csv', 'a', newline='') as csvfile:
        fieldnames = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()
        writer.writerow({
            'open_time': candlestick_data['t'],
            'open': candlestick_data['o'],
            'high': candlestick_data['h'],
            'low': candlestick_data['l'],
            'close': candlestick_data['c'],
            'volume': candlestick_data['v'],
            'close_time': candlestick_data['T'],
            'quote_asset_volume': candlestick_data['q'],
            'number_of_trades': candlestick_data['n'],
            'taker_buy_base_asset_volume': candlestick_data['V'],
            'taker_buy_quote_asset_volume': candlestick_data['Q'],
            'ignore': candlestick_data['B']
        })

# Define the callback function for handling errors
def on_error(ws, error):
    print(error)

# Define the callback function for handling the WebSocket connection
def on_open(ws):
    # Send the subscription message
    ws.send(json.dumps(subscribe_message))

# Define a function to keep the WebSocket connection alive
# Define a function to keep the WebSocket connection alive
def keep_alive(ws):
    while True:
        time.sleep(30)
        if ws.sock is not None and ws.sock.connected:
            try:
                ws.send(json.dumps({"method": "PING", "id": 123}))
            except websocket._exceptions.WebSocketConnectionClosedException:
                print("WebSocket connection closed unexpectedly. Reconnecting...")
                ws.run_forever()
        else:
            print("WebSocket connection is not established. Reconnecting...")
            ws.run_forever()

# Create a WebSocket connection
ws = websocket.WebSocketApp(socket_endpoint, on_message=on_message, on_error=on_error, on_open=on_open)

# Start a thread to keep the WebSocket connection alive
threading.Thread(target=keep_alive, args=(ws,)).start()

# Start the WebSocket connection
ws.run_forever()