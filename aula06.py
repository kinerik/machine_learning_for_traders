import requests, json
import matplotlib.pyplot as plt
import pandas as pd
import time
import os
import numpy as np

existe = os.path.isfile('tickers.csv')


janela = 600
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




def Bollinger_Bands(tickers, janela, desvio):

    if len(tickers) > janela:
        media = tickers.rolling(window= janela).mean()
        rolling_std  = tickers.rolling(window= janela).std()
        upper_band = media + (rolling_std * desvio)
        lower_band = media - (rolling_std * desvio)

        return True, media, upper_band, lower_band

    else:
        return False, 0, 0, 0

 

    
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

        if historico_ask[-1:] > historico_lower_band[-1:] and historico_ask[-2:-1] <= historico_lower_band[-2:-1] and len(historico_compras) >= len(historico_vendas):
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
    if len(historico_compras)> 0:
        ax.scatter(index_compras, historico_compras, marker = '^', color = "red", label = "Compra")
    if len(historico_vendas)>0:
        ax.scatter(index_vendas, historico_vendas, marker = 'v', color = "green", label = "Venda")

    return sinal, sinal_action





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
        status, media, upper_band, lower_band = Bollinger_Bands(bid, janela, desvio)

        if len(bid) < janela:
            ax.set_xlim(0, len(bid)+(len(bid)/4)+5)
        else:
            ax.set_xlim(len(bid)-janela, len(bid)+(len(bid)/4)+5)
            bid_min = np.array(bid[-janela:]).min()
            ask_max = np.array(ask[-janela:]).max()


            #ax.set_ylim(bid_min, ask_max)

            ax.set_ylim(bid_min,ask_max)
        ax.plot(bid, label = "Bid - Venda LTC "+ str(np.around(float(bid[-1:]),8)), color = 'green', alpha = 0.5)
        ax.plot(ask, label = "Ask - Compra LTC "+ str(np.around(float(ask[-1:]),8)), color = 'red', alpha = 0.5)




        sinal, sinal_action = detect_cross(float(bid[-1:]), float(ask[-1:]), float(lower_band[-1:]), float(upper_band[-1:]), len(df))
        
        print(sinal, sinal_action) 

        plt.legend()


        porcentagem = spread(bid[-1:],ask[-1:])
        ax.text(len(ask) + (len(ask)/10), bid[-1:] + (diferenca/2), "Spread " + str(np.around(float(porcentagem),3)) + "%")

        ax.scatter(len(ask)-1,ask[-1:], color = 'red', alpha = 1)
        ax.scatter(len(bid)-1,bid[-1:], color = 'green', alpha = 1)
        if status:
            ax.plot(media, '--', color = 'gray', alpha = 0.3)
            ax.plot(upper_band, '--', color = 'blue', alpha = 0.5)
            ax.plot(lower_band, '--', color = 'blue', alpha = 0.2)


            ax.scatter(len(ask),media[-1:], color = 'gray', alpha = 0.1)
            ax.scatter(len(ask),upper_band[-1:], color = 'blue', alpha = 0.1)
            ax.scatter(len(ask),lower_band[-1:], color = 'blue', alpha = 0.1)

        else:
            print("Sem dados suficientes para criar faixas de Bollinger")
        plt.pause(2)
        print(str(len(df)),"BID - ", str(float(bid[-1:])), " | ASK - ", str(float(ask[-1:])))


while True:

    try:
        get_tickers()
    except:
        print("Erro no servidor")
        time.sleep(5)
    plot()
    '''
    try:
        plot()

    except:
        print("- - Programa Encerrado -- ")
        exit()
    '''
