import websocket
import json
import threading
import time
import requests
import csv

# Set the Binance API WebSocket endpoint
socket_endpoint = "wss://stream.binance.com:9443/ws"

# Define the symbols to retrieve market cap data for
symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "DOTUSDT", "UNIUSDT", "LINKUSDT", "LTCUSDT"]

# Define the message to send to the WebSocket
subscribe_message = {
    "method": "SUBSCRIBE",
    "params": [f"{symbol.lower()}@ticker" for symbol in symbols],
    "id": 1
}

# Define the callback function for handling the WebSocket messages
def on_message(ws, message):
    data = json.loads(message)
    if not data.get('result', True):
        return
    
    symbol = data['s']
    market_cap = float(data['c']) * float(data['Q'])
    

    # Write market cap data to CSV file
    with open('market_cap_data.csv', 'a+', newline='') as csvfile:
        fieldnames = ['symbol', 'market_cap']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()
        writer.writerow({'symbol': symbol, 'market_cap': market_cap})

        
        

# Define the callback function for handling errors
def on_error(ws, error):
    print("error", error)

# Define the callback function for handling the WebSocket connection
def on_open(ws):
    # Send the subscription message
    ws.send(json.dumps(subscribe_message))

# Define a function to keep the WebSocket connection alive
def keep_alive(ws, event):
    import pdb
    pdb.set_trace()
    while not event.is_set():
        time.sleep(100)
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
#threading.Thread(target=keep_alive, args=(ws,)).start()

# Start the WebSocket connection
#ws.run_forever()