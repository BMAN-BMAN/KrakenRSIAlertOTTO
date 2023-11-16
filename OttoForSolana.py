#Otto for Solana

import sys
import time
import requests
import pandas as pd
import numpy as np
import urllib.parse
import hashlib
import hmac
import base64

# Function to get Kraken API key and secret from a file
def get_kraken_api_credentials(file_path="KrakenAPI.txt"):
    with open(file_path, "r") as f:
        lines = f.read().splitlines()
        api_key = lines[0]
        api_sec = lines[1]
    return api_key, api_sec

# Function to generate Kraken signature
def get_kraken_signature(urlpath, data, secret):
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()
    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()

# Function to get hourly ticker data from Kraken
def get_kraken_hourly_ticker(pair, interval=1):
    url = f"https://api.kraken.com/0/public/OHLC"
    params = {
        "pair": pair,
        "interval": interval
    }
    response = requests.get(url, params=params)
    data = response.json()["result"][pair]
    df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "vwap", "volume", "count"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)
    df.set_index("timestamp", inplace=True)
    return df

# Function to calculate RSI
def calculate_rsi(data, period=14):
    close_prices = data["close"].astype(float)
    daily_returns = close_prices.diff(1)
    gains = np.where(daily_returns > 0, daily_returns, 0)
    losses = np.where(daily_returns < 0, -daily_returns, 0)
    
    avg_gain = pd.Series(gains).rolling(window=period, min_periods=1).mean()
    avg_loss = pd.Series(losses).rolling(window=period, min_periods=1).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

# Get Kraken API credentials
api_key, api_sec = get_kraken_api_credentials()

# System greeting and passcode
passCheck = False
questionCheck = input("Hello, Brooks. This is OTTO. Would you like to begin? ")
if questionCheck.lower() in ["yes", "yes.", "y"]:
    codeCheck = int(input("Please input the passcode to begin automated cryptocurrency market monitoring. "))
    if codeCheck == 2121:
        passCheck = True
        print("Very well. Let us begin monitoring for automatic buy-in opportunities for Solana.")
    else:
        sys.exit("Unauthorized code. Program killed.")
elif questionCheck.lower() in ["no", "no.", "nevermind", "nah", "never mind", "n"]:
    sys.exit("Please come back if ready to begin automated trading. Goodbye.")

# Continuously fetch and print RSI for Solana/USD
pair_solana = "SOLUSD"
interval_seconds = 60  # Adjust as needed
while passCheck:
    # Getting hourly ticker data for SOL/USD
    ticker_data_solana = get_kraken_hourly_ticker(pair_solana, interval=interval_seconds)

    # Calculate RSI based on hourly data for Solana/USD
    rsi_solana = calculate_rsi(ticker_data_solana, period=14)

    # Print the RSI values for Solana/USD
    print("RSI (14 periods) for Solana/USD:")
    print(rsi_solana)

    # Sleep for a while before fetching data again
    time.sleep(interval_seconds)
