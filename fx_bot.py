from tradersbot import TradersBot
import random

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
    if tck in dark_tickers: print(ms)

    if len(price_list[tck]) > 5:
        sma = np.mean(np.array(price_list[tck][-6:-1]))
        if abs(sma - last_price)/last_price > .015:
                if last_price > sma: order.addSell(tck,10,last_price+dx)
                else: order.addBuy(tck,10,last_price-dx)

                print('Trade')

    print(msg['market_state']['ticker'], msg['market_state']['last_price'])

    tick += 1

def trade(msg,order):
    print('traded')

def triangular_arbitrage():
    for


t.onMarketUpdate = on_update
t.onTrade = trade
t.run()
