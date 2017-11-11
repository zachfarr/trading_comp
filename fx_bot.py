from tradersbot import TradersBot
import numpy as np
import random
from math import *

t = TradersBot(host='127.0.0.1', id='trader0', password='trader0')
tick = 0
dx = .01

tickers = ['USDCHF','USDJPY','EURUSD','USDCAD','CHFJPY','EURJPY','EURCHF','EURCAD' ]
public_ticker = {'USDCAD','EURUSD','USDCHF','USDJPY'}
dark_tickers = {'EURCAD','EURJPY','EURCHF','CHFJPY'}

price_list = {}
for tc in tickers:
    price_list[tc] = []


def on_update(msg,order):
    global tick
    ms = msg['market_state']
    tck = ms['ticker']
    last_price = msg['market_state']['last_price']
    price_list[tck].append(last_price)
    #if tck in dark_tickers: print(ms)

    if len(price_list[tck]) > 5:
        sma = np.mean(np.array(price_list[tck][-6:-1]))
        diff = abs(sma - last_price)/last_price
        diff *= (10/0.015)

        if diff >= 10:
                if last_price > sma: order.addSell(tck,ceil(diff),last_price+dx*last_price)
                else: order.addBuy(tck,floor(diff),last_price-dx*last_price)

                #print('Trade')
        arb = triangular_arbitrage(tck,last_price)
        if arb['trade'] == 'yes':
            for i in arb.keys():
                if i == 'trade':
                    continue
                if arb[i][0] == 'buy':
                    #print(i,arb[i][1])
                    order.addBuy(i,arb[i][1],price_list[i][-1])
                else:
                    order.addSell(i,arb[i][1],price_list[i][-1])

    #print(msg['market_state']['ticker'], msg['market_state']['last_price'])

    tick += 1

def trade(msg,order):
    #print('traded')
    pass

def get_info(msg,order):
    oo=msg['trader_state']['open_orders']
    #print(len(oo))
    if len(oo) > 50:
        count = 0
        for i in oo.keys():
            count+=1
            order.addCancel(oo[i]['ticker'],int(i))
            if count > 10:
                break

def triangular_arbitrage(ticker,price):
    if ticker == 'EURUSD':
        if len(price_list['EURJPY'])>0:
            val = 1/price_list['USDJPY'][-1]*price_list['EURJPY'][-1]
            if val<(1-5*dx)*price:
                return {'trade':'yes','EURUSD':('sell',amount(val,price)),'USDJPY':('sell',floor(amount(val,price))),'EURJPY':('buy',amount(val,price))}
            elif val>(1+5*dx)*price:
                return {'trade':'yes','EURUSD':('buy',amount(val,price)),'USDJPY':('buy',floor(amount(val,price))),'EURJPY':('sell',amount(val,price))}

        if len(price_list['EURCAD'])>0:
            val = 1/price_list['USDCAD'][-1]*price_list['EURCAD'][-1]
            if val<(1-5*dx)*price:
                return {'trade':'yes','EURUSD':('sell',amount(val,price)),'USDCAD':('sell',floor(amount(val,price)*price_list['EURCAD'][-1])),'EURCAD':('buy',amount(val,price))}
            elif val>(1+5*dx)*price:
                return {'trade':'yes','EURUSD':('buy',amount(val,price)),'USDCAD':('buy',floor(amount(val,price)*price_list['EURCAD'][-1])),'EURCAD':('sell',amount(val,price))}

        if len(price_list['EURCHF'])>0:    
            val = 1/price_list['USDCHF'][-1]*price_list['EURCHF'][-1]
            if val<(1-5*dx)*price:
                return {'trade':'yes','EURUSD':('sell',amount(val,price)),'USDCHF':('sell',floor(amount(val,price)*price_list['EURCHF'][-1])),'EURCHF':('buy',amount(val,price))}
            elif val>(1+5*dx)*price:
                return {'trade':'yes','EURUSD':('buy',amount(val,price)),'USDCHF':('buy',floor(amount(val,price)*price_list['EURCHF'][-1])),'EURCHF':('sell',amount(val,price))}
               
    elif ticker == 'USDCAD':
        if len(price_list['EURCAD'])>0:
            val = price_list['EURCAD'][-1]*1/price_list['EURUSD'][-1]
            if val<(1-5*dx)*price:
                return {'trade':'yes','USDCAD':('sell',amount(val,price)),'EURCAD':('buy',amount(val,price)),'EURUSD':('sell',amount(val,price))}
            elif val>(1+5*dx)*price:
                return {'trade':'yes','USDCAD':('buy',amount(val,price)),'EURCAD':('sell',amount(val,price)),'EURUSD':('buy',amount(val,price))}
        
    elif ticker == 'USDCHF':
        if len(price_list['EURCHF'])>0:
            val = 1/price_list['EURUSD'][-1]*price_list['EURCHF'][-1]
            if val<(1-5*dx)*price:
                return {'trade':'yes','USDCHF':('sell',amount(val,price)),'EURUSD':('sell',amount(val,price)),'EURCHF':('buy',amount(val,price))}
            elif val>(1+5*dx)*price:
                return {'trade':'yes','USDCHF':('buy',amount(val,price)),'EURUSD':('buy',amount(val,price)),'EURCHF':('sell',amount(val,price))}

        if len(price_list['CHFJPY'])>0:
            val = price_list['USDJPY'][-1]*1/price_list['CHFJPY'][-1]
            if val<(1-5*dx)*price:
                return {'trade':'yes','USDCHF':('sell',amount(val,price)),'USDJPY':('buy',amount(val,price)),'CHFJPY':('sell',amount(val,price))}
            elif val>(1+5*dx)*price:
                return {'trade':'yes','USDCHF':('buy',amount(val,price)),'USDJPY':('sell',amount(val,price)),'CHFJPY':('buy',amount(val,price))}

    elif ticker == 'USDJPY':
        if len(price_list['EURJPY'])>0:
            val = 1/price_list['EURUSD'][-1]*price_list['EURJPY'][-1]
            if val<(1-5*dx)*price:
                return {'trade':'yes','USDJPY':('sell',amount(val,price)),'EURUSD':('sell',amount(val,price)),'EURJPY':('buy',amount(val,price))}
            elif val>(1+5*dx)*price:
                return {'trade':'yes','USDJPY':('buy',amount(val,price)),'EURUSD':('buy',amount(val,price)),'EURJPY':('sell',amount(val,price))}

        if len(price_list['CHFJPY'])>0:
            val = price_list['USDCHF'][-1]*price_list['CHFJPY'][-1]
            if val<(1-5*dx)*price:
                return {'trade':'yes','USDJPY':('sell',amount(val,price)),'USDCHF':('buy',amount(val,price)),'CHFJPY':('buy',amount(val,price))}
            elif val>(1+5*dx)*price:
                return {'trade':'yes','USDJPY':('buy',amount(val,price)),'USDCHF':('sell',amount(val,price)),'CHFJPY':('sell',amount(val,price))}        
        
        
        
    return {'trade':'no'}

def amount(val, price):
    amt = abs(val-price)/price
    amt *= (20/(5*dx))
    return floor(amt)
        


t.onMarketUpdate = on_update
t.onTrade = trade
t.onTraderUpdate = get_info
t.run()
