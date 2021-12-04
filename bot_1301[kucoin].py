# kucoin(pip install kucoin-python) -- bolt1304

api_key = ''
api_secret = ''
api_passphrase = ''
eth_acc = ''
kcs_acc = ''
btc3l_acc = ''

asset = 'BTC'
fiat = 'USDT'

import time
import numpy as np
import pandas as pd
import datetime as DT

print('----TIME-------------PRICE--RSI---STRATEGY')

while True:
    try:
        from kucoin.client import Market
        client = Market(api_key, api_secret, api_passphrase,
                        url='https://api.kucoin.com')
        price = client.get_ticker(asset+'-'+fiat)
        price = price['price']
        orders = client.get_aggregated_orderv3(asset+'-'+fiat)
        klines = client.get_kline(asset+'-'+fiat, '1min')
        server_time = time.strftime('%m/%d/%Y %H:%M:%S',
                                        time.gmtime(client.get_server_timestamp()/1000.))


        from kucoin.client import User
        client = User(api_key, api_secret, api_passphrase)
        fiat_balance = client.get_account('612a5bd4fdacf4000769936e')
        fiat_balance = fiat_balance['available']
        coin_balance = client.get_account(kcs_acc)
        coin_balance = coin_balance['available']

        
        from kucoin.client import Trade
        client = Trade(api_key, api_secret, api_passphrase, is_sandbox=False)
        last_price = pd.DataFrame(client.get_order_list())
        last_price = last_price.loc[0]['items']['price']


        orderBids = np.array(list(orders.values()), dtype=object)[2]
        orderAsks = np.array(list(orders.values()), dtype=object)[3]
        orderBidAmount = pd.DataFrame([float(entry[1]) for entry in orderBids])
        orderAskAmount = pd.DataFrame([float(entry[1]) for entry in orderAsks])
        
        buyOrders = float(orderBidAmount.iloc[0:500].sum())
        sellOrders = float(orderAskAmount.iloc[0:500].sum())
        orderRate = int(buyOrders/(buyOrders + sellOrders)*100)
        

        if float(price) > float(last_price) and orderRate < 40:
            signal = 'SELL'
        elif orderRate > 85:
            signal = 'BUY'
        elif float(price) < float(last_price)*0.75:
            signal = 'limit_loss'
        else:
            signal = 'wait'


        if signal == 'BUY':
            if float(fiat_balance) > float(coin_balance)*float(price):
                from kucoin.client import Trade
                client = Trade(api_key, api_secret, api_passphrase, is_sandbox=False)
                client.create_limit_order(asset+'-'+fiat, 'buy',
                                          format(int((float(fiat_balance)/float(price))-0.005),'.2f'),
                                          price)
                signal = 'BUY ordered @ ' + price
        elif signal == 'SELL':
            if float(coin_balance)*float(price) > float(fiat_balance):
                from kucoin.client import Trade
                client = Trade(api_key, api_secret, api_passphrase, is_sandbox=False)
                client.create_limit_order(asset+'-'+fiat, 'sell',
                                          format(float(coin_balance)-0.005,'.3f'), price)
                signal = 'SELL ordered @ ' + price
        elif signal == 'limit_loss':
            if float(coin_balance)*float(price) > float(fiat_balance):
                from kucoin.client import Trade
                client = Trade(api_key, api_secret, api_passphrase, is_sandbox=False)
                client.create_market_order(asset+'-'+fiat, 'sell', size=coin_balance)

    except:
        signal = signal

    
    print(server_time + ' ' + price + ' ' + str(orderRate) + ' ' + signal)
    time.sleep(60)
