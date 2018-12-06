import requests, json
import matplotlib.pyplot as plt
import pandas as pd
import time
import os
import numpy as np

existe = os.path.isfile('tickers.csv')


janela = 900
desvio = 2

historico_bid = []
historico_ask = [] 
historico_lower_band = []
historico_upper_band = []
historico_compras = []
historico_vendas = []
historico_sinal = []
index_compras = []
index_vendas = []  
if existe:
    pass
else:
    grava = open("tickers.csv","w")
    grava.write("bid,ask\n") 
    grava.close()


fig = plt.figure(figsize=(10,10))

ax = fig.gca()




def Bollinger_Bands(bid, ask, janela, desvio):

    if len(bid) > janela:
        media = bid.rolling(window= janela).mean()
        rolling_std  = bid.rolling(window= janela).std()
        upper_band = media + (rolling_std * desvio)
        lower_band = media - (rolling_std * desvio)

        porcentagem = spread(bid[-1:],ask[-1:])
        diferenca = ask[-1:] - bid[-1:] 
        ax.text(len(ask) + (len(ask)/10), bid[-1:] + (diferenca/2), "Spread " + str(np.around(float(porcentagem),3)) + "%")



        ax.plot(media, '--', color = 'gray', alpha = 0.3)
        ax.plot(upper_band, '--', color = 'blue', alpha = 0.5)
        ax.plot(lower_band, '--', color = 'blue', alpha = 0.2)


        ax.scatter(len(ask),media[-1:], color = 'gray', alpha = 0.1)
        ax.scatter(len(ask),upper_band[-1:], color = 'blue', alpha = 0.1)
        ax.scatter(len(ask),lower_band[-1:], color = 'blue', alpha = 0.1)
        return lower_band, upper_band



    else:
        print("Sem dados suficientes para criar faixas de Bollinger")




 

    
def detect_cross(bid, ask, lower_band, upper_band, index):

    historico_bid.append(bid)
    historico_ask.append(ask)
    historico_lower_band.append(lower_band)
    historico_upper_band.append(upper_band)


    del historico_bid[:-10]
    del historico_ask[:-10]
    del historico_lower_band[:-10]
    del historico_upper_band[:-10]



    if len(historico_sinal) > 1:

        if historico_bid[-1:] > historico_lower_band[-1:] and historico_bid[-2:-1] <= historico_lower_band[-2:-1]:
            historico_compras.append(float(ask))
            index_compras.append(index)
            sinal = "Buy"
            sinal_action = 1

        elif historico_bid[-1:] < historico_upper_band[-1:] and historico_bid[-2:-1] >= historico_upper_band[-2:-1]:
            historico_vendas.append(float(bid))
            index_vendas.append(index)
            sinal = "Sell"
            sinal_action =2
        else:
            sinal = "Hold"
            sinal_action = 0
    else:
        sinal = "Hold"
        sinal_action = 0
    historico_sinal.append(sinal_action) 

    return 0



def plota_negociatas(bid,ask, lower_band, upper_band):
    reset_memoria()

    for i in range(len(bid)-(janela*2), len(bid)):            
        _ = detect_cross(float(bid[i]), float(ask[i]), float(lower_band[i]), float(upper_band[i]), i)

    if len(historico_compras) > 0:
        ax.scatter(index_compras, historico_compras, marker = 'v', color = "red", label = "Compra")
        for c in range(len(index_compras)): 
            ax.text(index_compras[c], historico_compras[c], '- compra', color = "black", alpha = 0.8)

    if len(historico_vendas) > 0:
        ax.scatter(index_vendas, historico_vendas, marker = '^', color = "green", label = "Venda")
        for v in range(len(index_vendas)): 
            ax.text(index_vendas[v], historico_vendas[v], '- venda', color = "black", alpha = 0.8)


def reset_memoria():
    global historico_compras, historico_vendas, index_compras, index_vendas

    historico_compras = []
    historico_vendas = []
    index_compras = []
    index_vendas = []

def spread(bid,ask):
    porcento = ask / 100
    diferenca = ask - bid 
    porcentagem = diferenca / porcento

    return porcentagem


def get_tickers():
    bitfinex_ltc = "https://api.bitfinex.com/v1/pubticker/ltcbtc"
    data_bitfinex = requests.get(url=bitfinex_ltc)
    binary_bitfinex = data_bitfinex.content
    output_bitfinex = json.loads(binary_bitfinex)
    grava = open("tickers.csv","a")
    grava.write(str(output_bitfinex['bid'])+","+str(output_bitfinex['ask'])+'\n')
    grava.close()



def plot():
    df = pd.read_csv("tickers.csv")

    if len(df) > 1:
        ax.clear()
        bid = df['bid']
        ask = df['ask']


        diferenca = ask[-1:] - bid[-1:]


        plt.title("Litecoin/BTC")

        if len(bid) < janela*2:
            ax.set_xlim(0, len(bid)+(len(bid)/4)+5)

        else:
            ax.set_xlim(len(bid)-janela*2, len(bid)+100)
            bid_min = np.array(bid[-janela*2:]).min()
            ask_max = np.array(ask[-janela*2:]).max()
            ax.set_ylim(bid_min-(bid_min * .001),ask_max+(ask_max * .001))




        ax.plot(bid, label = "Bid - Venda LTC "+ str(np.around(float(bid[-1:]),8)), color = 'green', alpha = 0.5)
        ax.plot(ask, label = "Ask - Compra LTC "+ str(np.around(float(ask[-1:]),8)), color = 'red', alpha = 0.5)

        
        plt.legend()

        ax.scatter(len(ask)-1,ask[-1:], color = 'red', alpha = 1)
        ax.scatter(len(bid)-1,bid[-1:], color = 'green', alpha = 1)
        if len(bid) > janela * 2:
            lower_band, upper_band = Bollinger_Bands(bid, ask, janela, desvio)
            plota_negociatas(bid,ask, lower_band, upper_band)

        plt.pause(2)



while True:

    try:
        get_tickers()
    except:
        print("Erro no servidor")
        time.sleep(5)
    try:
        plot()
    except:
        print("-- Encerrando o Programa --")
        exit()
            
   
