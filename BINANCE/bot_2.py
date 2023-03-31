## Binance Python Bot :]
# This bot calculates the RSI indicator and buys/sells if 
# RSI is in range and the price is higher than buy price

import time
# pip install python-binance
from binance.client import Client
from binance.enums import *
# pip install pandas
import pandas as pd
# pip install numpy
import numpy as np


# Functions
def computeRSI (data, time_window):
    diff = np.diff(data)
    up_chg = 0 * diff
    down_chg = 0 * diff
    
    # up change is equal to the positive difference, otherwise equal to zero
    up_chg[diff > 0] = diff[ diff>0 ]
    
    # down change is equal to negative deifference, otherwise equal to zero
    down_chg[diff < 0] = diff[ diff < 0 ]

    up_chg = pd.DataFrame(up_chg)
    down_chg = pd.DataFrame(down_chg)
    
    up_chg_avg   = up_chg.ewm(com=time_window-1 , min_periods=time_window).mean()
    down_chg_avg = down_chg.ewm(com=time_window-1 , min_periods=time_window).mean()
    
    rs = abs(up_chg_avg/down_chg_avg)
    rsi = 100 - 100/(1+rs)
    rsi = int(rsi[0].iloc[-1])
    return rsi

##################################################

# Authenticate to Binance
api_key = ''
api_secret = ''

##################################################

trdPair1 = 'BNB'
trdPair2 = 'BUSD'
winRate = 1.017
client = Client(api_key, api_secret)

# Console header
print('___DATE______TIME_____BALANCE___RSI____PRICE____STRATEGY___TARGET-PRICE__')

##################################################

# Main loop
while True:
    try:
        # Initial values
        tradePair = trdPair1 + trdPair2
        price = client.get_ticker(symbol=tradePair)
        btcCount = client.get_asset_balance(asset = trdPair1)
        btcCount = float(btcCount['free'])*float(price['askPrice'])
        busdCount = client.get_asset_balance(asset = trdPair2)
        busdCount = float(busdCount['free'])

        # Find last trade
        if btcCount > busdCount:
            lastrade = trdPair1
        elif btcCount < busdCount:
            lastrade = trdPair2

        # Find last price
        trades = client.get_my_trades(symbol=tradePair)
        trades = trades[len(trades)-1]
        lasprice = float(trades['price'])
        
        klines = client.get_klines(symbol=tradePair, interval='5m', limit='500')
        klines2 = client.get_historical_klines(tradePair, Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
        close = [float(entry[4]) for entry in klines]
        close_array = np.asarray(close)
        close_finished = close_array[:-1]
        rsi = computeRSI (close_finished, 14)
        
        # Price & Server Time
        price = client.get_ticker(symbol=tradePair)
        coitime = client.get_server_time()
        coitime = time.strftime('%m/%d/%Y %H:%M:%S',
                                time.gmtime(coitime['serverTime']/1000.))
        
        # SELL 
        if lastrade == trdPair1:
            balance = client.get_asset_balance(asset = trdPair1)
            coiNumber = format(float(balance['free'])- 0.0005,'.4f') 
            coiprice = format(float(price['askPrice']), '.2f')
            if float(coiprice) > float(lasprice) * winRate or (rsi > 70):
                stat = 'sell'
                ## order the sell comand            
                order = client.order_limit_sell(
                    symbol=tradePair,
                    quantity= float(coiNumber),
                    price= coiprice)
                
                lastrade = trdPair2
                lasprice = coiprice
            else:
                stat = 'hold' + trdPair1 + '  ' + str(lasprice*winRate)

        # BUY    
        elif lastrade == trdPair2:
            balance = client.get_asset_balance(asset = trdPair2)
            coiNumber = format(float(balance['free'])-0.0005,'.4f')
            coiprice = format(float(price['askPrice']), '.2f')
            test = float(coiNumber)/float(coiprice)
            if float(coiprice) * winRate < float(lasprice) or (rsi < 25):
                stat = 'buy'
                
                order = client.order_limit_buy(
                    symbol=tradePair,
                    quantity=format(test, '.4f'),
                    price= coiprice)
                
                lastrade = trdPair1
                lasprice = coiprice
            else:
                stat = 'hold' + trdPair2 + '  ' + str(lasprice/winRate)

        # Print the values
        print(coitime + ' ' + balance['free'] + '  ' + str(rsi) + '  ' +
              price['askPrice'] + ' ' + stat)
    except:
        print(coitime + ' ' + 'an error occured & retrying now')
    # Repeat the code every 1.5 minute
    time.sleep(60)



    
