import matplotlib.pyplot as plt
from coinmarketcap import Market
import pandas as pd
import time 


def recebe_btc(lista_btc):
    market = Market()
    ticker = market.ticker(convert="BRL")
    data = ticker['data']['1']['quotes']['BRL']['price']
    btc = data
    lista_btc.append(btc)
    return lista_btc

def recebe_xrp(lista_xrp):
    market = Market()
    ticker = market.ticker(convert="BRL")
    data = ticker['data']['1']['quotes']['BRL']['price']
    btc = data
    lista_xrp.append(btc)
    return lista_xrp


lista_btc = []
lista_xrp = []

fig = plt.figure(figsize=(10,10))
fig2 = plt.figure(figsize=(10,10))
 
ax = fig.gca()
ax2 = fig2.gca()

while True:
    ax.clear()
    ax2.clear()
    ax.plot(recebe_btc(lista_btc))
    ax2.plot(recebe_xrp(lista_xrp))
    plt.pause(1)

