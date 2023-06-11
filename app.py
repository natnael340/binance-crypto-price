from flask import Flask, render_template, request, session, make_response
from flask_socketio import SocketIO, socketio
import csv
from apscheduler.schedulers.background import BackgroundScheduler
from binance_api_rest import fetch_data, SYMBOLS
from fetch_markt_cap_rest import SYMBOLS as MCSYMBOLS
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app, manage_session=False)


STOPPED = 'STOPPED'
STARTED = 'STARTED'

symbol = 'BTCUSDT'
symbol_updated = False


def get_csv_data():
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
    global symbol
    return render_template('index.html', symbol=symbol, symbols=SYMBOLS, mc_symbols= MCSYMBOLS)

@app.route('/change_symbol')
def change_symbol():
    global symbol
    global symbol_updated 
    print(request.args.get('symbol'))
    symbol = request.args.get('symbol')
    symbol_updated = True
    response = make_response('')

    return response

@socketio.on('mc_data')
def handle_market_cap_data(event):
    global server_status
    while not event.is_set():
        if server_status == STOPPED:
            continue
        socketio.emit('mc_data', get_market_cap_data())
        socketio.sleep(30)


@socketio.on('get_data', namespace='/')
def handle_get_data(event):
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
    socketio.emit("initial_data", get_csv_data())

scheduler = BackgroundScheduler()
scheduler.add_job(func=fetch_data, trigger='interval', seconds=3600)
scheduler.start()

if __name__ == '__main__':
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
        
