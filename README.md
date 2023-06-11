# Crypto Price & Marketcap

## Selected Currency for live candelstick

- BTCUSDT
- ETHUSDT
- ADAUSDT

## Selected Currency for Marketcap

- BTCUSDT
- ETHUSDT
- BNBUSDT
- XRPUSDT
- ADAUSDT
- DOGEUSDT
- DOTUSDT
- UNIUSDT
- LINKUSDT
- LTCUSDT

## Installation

### First make sure you have python installed

For windows

```
python --version
```

For linux or mac

```
python3 --version
```

### Install virtual environment

For windows

```
python -m venv binance-env
```

For linux or mac

```
python3 -m venv binance-env
```

### Activate environment

For windows

```
./binance-env/Scripts/Activate
```

For linux or mac

```
source bin/activate
```

### Install required libraries

```
pip install -r requirements.txt
```

## Running

For windows

```
python app.py
```

For linux or mac

```
python3 app.py
```

## Suggestions

- Using postgresql instead of storing the data is preferable due to:

  - Scalability
  - Performance
  - Data integrity
  - Data management:

- Using websocket and decreasing the fetching time would make a live data update on the candelstick
- The script can be deployed as a cron job but to have a real-time data using websocket with background task scheduler and also using multithreading we can display real-time data update
