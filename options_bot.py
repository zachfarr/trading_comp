from tradersbot import TradersBot
import numpy as np
from scipy import stats
from py_vollib import black_scholes
from py_vollib.black_scholes import implied_volatility
from py_vollib.black_scholes.greeks import analytical
import time

t = TradersBot(host='127.0.0.1', id='trader0', password='trader0')
tick = 0
r = 0
dx = .02

calls = set()
puts = set()
fut = 'TMXFUT'

tickers = {'TMXFUT': {'price': []}}

for i in range(80,121):
    curr_call = str('T' + str(i) + 'C')
    curr_put = str('T' + str(i) + 'P')
    calls.add(curr_call)
    puts.add(curr_put)
    tickers[curr_call] = {'price': [], 'delta': [], 'gamma': [], 'vega': [], 'vol': []}
    tickers[curr_put] = {'price': [], 'delta': [], 'gamma': [], 'vega': [], 'vol': []}


def on_update(msg,order):
    now = time.time()
    global tick
    ms = msg['market_state']
    tck = ms['ticker']
    last_price = msg['market_state']['last_price']
    tickers[tck]['price'].append(last_price)

    tick += 1

    if tck == fut:
        return

    S = tickers[fut]['price'][-1] if len(tickers[fut]['price']) > 0 else None
    K = int(tck[1:4]) if len(tck) == 5 else int(tck[1:3])
    t = (450 - tick)/450 *1/12
    flag = 'c' if tck[-1] == 'C' else 'p'


    if S is not None:
        try:
            iv = implied_volatility.implied_volatility(last_price,S,K,t,r,flag)
            theo_p = black_scholes.black_scholes(flag,S,K,t,r,iv)
            delta = analytical.delta(flag,S,K,t,r,iv)
            gamma = analytical.gamma(flag,S,K,t,r,iv)
            # vega = analytical.vega(flag,S,K,t,r,iv)
            tickers[tck]['vol'].append(vol)
            tickers[tck]['delta'].append(delta)
            tickers[tck]['gamma'].append(gamma)
            # tickers[tck]['vega'].append(vega)

            if len(tickers[tck]['vol']) > 5:
                vol_sma = np.mean(np.array(ticker[tck]['vol'][-6:-1]))
                if abs(iv - vol_sma)/vol_sma > .015:
                    if iv > vol_sma: order.addSell(tck,10,last_price+dx)
                    else: order.addBuy(tck,10,last_price-dx)

        except:
            print(S, K, last_price, flag)


def curr_pos(msg,order):
    ts = msg['trader_state']
    cash = ts['cash']
    pos = ts['positions']


def trade(msg,order):
    print('traded')


def black_scholes_call(S,K,t,T,r,sigma):
    d1 = np.log(S/K) + (r + .5*sigma**2)*(T-t)
    d1 = d1/(sigma*np.sqrt(T-t))
    d2 = d1 - sigma*np.sqrt(T-t)
    return stats.norm.cdf(d1)*S - stats.norm.cdf(d2)*K*np.exp(-1*r*(T-t))

def black_scholes_put(S,K,t,T,r,sigma):
    return black_scholes_call(S,K,t,T,r,sigma) + K*np.exp(-1*r*(T-t)) - S

# S = 100
# K = 100
# sigma = .2
# r = .01
# flag = 'p'
# t = .5

# print(black_scholes_put(S,K,t,1,r,sigma))
# p = black_scholes.black_scholes(flag,S,K,t,r,sigma)
# print(p)



t.onMarketUpdate = on_update
t.onTrade = trade
t.onTraderUpdate = curr_pos
t.run()
