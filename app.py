from flask import Flask, render_template, request, session, make_response
from flask_socketio import SocketIO, socketio
import csv
from apscheduler.schedulers.background import BackgroundScheduler
from binance_api_rest import fetch_data, SYMBOLS
from fetch_markt_cap_rest import SYMBOLS as MCSYMBOLS, fetch_mc_data
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app, manage_session=False)


STOPPED = 'STOPPED'
STARTED = 'STARTED'


symbol = 'BTCUSDT' # default symbol
symbol_updated = False # symbol status


def get_csv_data():
    """
    Read the candelstick csv data from candlestick_data.csv for a specific symbol
    and return an array of candelstick data
    """
    global symbol
    try:
        with open('candlestick_data.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            data = []
            for row in reader:
                if row.get('symbol') == symbol:
                    data.append(row)
            return data
    except FileNotFoundError:
        return []
    
def get_market_cap_data():
    """
    Get the market cap data from market_cap_data.csv file and return
    the market cap data for selected symbols.
    """
    try:
        with open('market_cap_data.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            data = {}
            for row in reader:
                data = row
            return data
    except FileNotFoundError:
        return {}
    
def check_for_new_data():
    """
    Check if the candelstic data is updated based on last number of rows.
    """
    global last_row_count
    csv_data = get_csv_data()
    if len(csv_data) > last_row_count:
        data_to_return = csv_data[last_row_count:]
        last_row_count = len(csv_data)
        return data_to_return
    else:
        return None

last_row_count = 0

@app.route('/')
def index():
    """
    Main entry point
    """
    global symbol
    return render_template('index.html', symbol=symbol, symbols=SYMBOLS, mc_symbols= MCSYMBOLS)

@app.route('/change_symbol')
def change_symbol():
    """
    An endpoint to change the symbol and retrive another symbol candelstick data.
    """
    global symbol
    global symbol_updated 
    print(request.args.get('symbol'))
    symbol = request.args.get('symbol')
    symbol_updated = True
    response = make_response('')

    return response

@socketio.on('mc_data')
def handle_market_cap_data(event):
    """
    Market cap socket endpoint
    it get the csv data and send it to the client only when the server is running.
    """
    global server_status
    while not event.is_set():
        if server_status == STOPPED:
            continue
        socketio.emit('mc_data', get_market_cap_data())
        socketio.sleep(30)


@socketio.on('get_data', namespace='/')
def handle_get_data(event):
    """
    a Scoket enpoint which is used to listed for get_data events.
    while the server is running it emt if there exists new data or 
    the symbol is changed and the data haven't been updated yet.
    """
    global symbol_updated
    while not event.is_set():
        if symbol_updated:
            socketio.emit("initial_data", get_csv_data())
            symbol_updated = False
            continue
        new_data = check_for_new_data()
        if new_data:
            socketio.emit('new_data', new_data)
            socketio.sleep(10)

# Define the WebSocket route to stream live candlestick data
@socketio.on('connect')
def handle_connect():
    "initate intial websocket connection"
    socketio.emit("initial_data", get_csv_data())

"""
Background task that run every 1 hour 
"""
scheduler = BackgroundScheduler()
# Add the task that fetch the candelick data from binance to run every 1 hour
scheduler.add_job(func=fetch_data, trigger='interval', seconds=3600)
# Add the task that fetch the marketcap data from binance to run every 1 hour
scheduler.add_job(func=fetch_mc_data, trigger='interval', seconds=3600)
scheduler.start()

if __name__ == '__main__':
    """
    This contains 2 threads one is for checking if new candelstick data is present and send 
    data to the client, and the other thread sends the marketcap data to the client
    """
    global server_status
    server_status = STOPPED
    event = threading.Event()
    thread = threading.Thread(target=handle_get_data, args=(event,))
    thread.start()
    mcthread = threading.Thread(target=handle_market_cap_data, args=(event,))
    mcthread.start()
    
   

    try:
        server_status = STARTED
        print('Flask server is running at http://localhost:5000')
        socketio.run(app)
    except KeyboardInterrupt:
        pass
    finally:
        # Set the stop event to stop the background thread
        event.set()
        thread.join()
        mcthread.join()
        
