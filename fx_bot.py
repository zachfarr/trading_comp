from tradersbot import TradersBot
import random

t = TradersBot(host='127.0.0.1', id='trader0', password='trader0')
tick = 0

tickers = ['USDCAD','USDJPY','EURUSD','USDCAD','CHFJPY','EURJPY','EURCHF','EURCAD' ]
public_ticker = {'USDCAD','EURUSD','USDCHF','USDJPY'}
dark_tickers = {'EURCAD','EURJPY','EURCHF','CHFJPY'}

def on_update(msg,order):
    global tick
    ms = msg['market_state']
    tck = ms['ticker']

    curr = 'EURCAD'
    order.addBuy(curr,10,2.0)
    # order.addBuy(curr,10,1.0)

    tick += 1

def trade(msg,order):
    print('traded')

t.onMarketUpdate = on_update
t.onTrade = trade
t.run()
