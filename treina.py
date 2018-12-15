import requests, json
import matplotlib.pyplot as plt
import pandas as pd
import time
import os
import numpy as np
from sklearn.svm import SVC
from sklearn.externals import joblib

existe = os.path.isfile('tickers.csv')
svm = SVC(kernel='rbf', random_state=0, gamma=.01, C=3)

## CONFIGURAÇÃO DOS PARÂMETROS

janela = 360            # Dimensão da janela para cálculo de indicadores
desvio = 2              # Dimensão do desvio da janela dos indicadores
batch_size = 360        # Dimensão do Lote de memória para treinar o modelo ( features - X )  
intervalo = 10           # Intervalo entre as consultas de tickers no servidor
historico_tamanho = 360  # Dimensão da janela para visualização dos sinais dos indicadores 

## ---------------------------------


X = []
Y = [] 

historico_bid = []
historico_ask = [] 

historico_lower_band = []
historico_upper_band = []

historico_compras = []
historico_vendas = []
historico_sinal = []

index_compras = []
index_vendas = []

historico = ["","","","","",""]

X_temp = [0,0,0,0,0,0]
epoch = 0
lucro_total=0

batch = []
compras = [0,0,0,0,0,0]
vendas = [0,0,0,0,0,0]

sinal_action = ['','','','','','']

if existe:
    pass
else:
    grava = open("tickers.csv","w")
    grava.write("bid,ask\n") 
    grava.close()


fig = plt.figure(figsize=(10,10))

ax = fig.gca()

def reset_memoria():
    global historico_compras, historico_vendas, index_compras, index_vendas

    historico_compras = []
    historico_vendas = []
    index_compras = []
    index_vendas = []


def Bollinger_Bands(bid, ask, janela, desvio):

    if len(bid) > janela:
        media = bid.rolling(window= janela).mean()
        rolling_std  = bid.rolling(window= janela).std()
        upper_band = media + (rolling_std * desvio)
        lower_band = media - (rolling_std * desvio)




        #ax.plot(media, '--', color = 'gray', alpha = 0.3)
        ax.plot(upper_band, '--', color = 'green', alpha = 0.5)
        ax.plot(lower_band, '--', color = 'red', alpha = 0.2)


        #ax.scatter(len(ask),media[-1:], color = 'gray', alpha = 0.1)
        ax.scatter(len(ask),upper_band[-1:], color = 'green', alpha = 0.1)
        ax.scatter(len(ask),lower_band[-1:], color = 'red', alpha = 0.1)
        return lower_band, upper_band



    else:
        print("Sem dados suficientes para criar faixas de Bollinger")

 

    
def detect_cross(bid, ask, lower_band, upper_band, index):

    historico_bid.append(bid)
    historico_ask.append(ask)
    historico_lower_band.append(lower_band)
    historico_upper_band.append(upper_band)


    del historico_bid[:-historico_tamanho]
    del historico_ask[:-historico_tamanho]
    del historico_lower_band[:-historico_tamanho]
    del historico_upper_band[:-historico_tamanho]



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

    return sinal_action



def plota_negociatas(bid,ask, lower_band, upper_band):
    reset_memoria()

    for i in range(len(bid)-(janela), len(bid)):            
        sinal_action = detect_cross(float(bid[i]), float(ask[i]), float(lower_band[i]), float(upper_band[i]), i)

    if len(historico_compras) > 0:
        ax.scatter(index_compras, historico_compras, marker = 'v', color = "red", label = "Compra")
        for c in range(len(index_compras)): 
            ax.text(index_compras[c], historico_compras[c], '- compra', color = "black", alpha = 0.8)

    if len(historico_vendas) > 0:
        ax.scatter(index_vendas, historico_vendas, marker = '^', color = "green", label = "Venda")
        for v in range(len(index_vendas)): 
            ax.text(index_vendas[v], historico_vendas[v], '- venda', color = "black", alpha = 0.8)

    return sinal_action

def spread(bid,ask):
    porcento = ask / 100
    diferenca = ask - bid 
    porcentagem = diferenca / porcento

    return porcentagem


def get_tickers():
    bitfinex_ltc = "https://api.bitfinex.com/v1/pubticker/btcusd"
    data_bitfinex = requests.get(url=bitfinex_ltc)
    binary_bitfinex = data_bitfinex.content
    output_bitfinex = json.loads(binary_bitfinex)
    grava = open("tickers.csv","a")
    grava.write(str(output_bitfinex['bid'])+","+str(output_bitfinex['ask'])+'\n')
    grava.close()



def main():
    global epoch, historico, lucro_total
    print("Lucro Total: ", lucro_total) 
    df = pd.read_csv("tickers.csv")

    if len(df) > 1:
        ax.clear()
        bid = df['bid']
        ask = df['ask']
        j = janela * 3



        diferenca = ask[-1:] - bid[-1:] 
        porcentagem = spread(bid[-1:],ask[-1:])

        ax.text(len(ask) + 10, bid[-1:] + (diferenca/2), "Spread " + str(np.around(float(porcentagem),3)) + "%")


        plt.title("BTC / USD")

        if len(bid) < janela:
            ax.set_xlim(0, len(bid)+(len(bid)/4)+5)

        else:
            ax.set_xlim(len(bid)-janela, len(bid)+100)
            bid_min = np.array(bid[-janela:]).min()
            ask_max = np.array(ask[-janela:]).max()
            ax.set_ylim(bid_min-(bid_min * .001),ask_max+(ask_max * .001))




        ax.plot(bid, label = "Bid - Venda BTC "+ str(np.around(float(bid[-1:]),8)), color = 'black', alpha = 0.5)
        ax.plot(ask, label = "Ask - Compra BTC "+ str(np.around(float(ask[-1:]),8)), color = 'gray', alpha = 0.5)

        
        plt.legend()

        ax.scatter(len(ask)-1,ask[-1:], color = 'black', alpha = 1)
        ax.scatter(len(bid)-1,bid[-1:], color = 'gray', alpha = 1)
        if len(bid) > janela * 3:
            bid_mean = float(bid[-1:] / bid[0])
            ask_mean = float(ask[-1:] / ask[0])
            volta = 0.5
            for ind in range(0,6):

                 lower_band, upper_band = Bollinger_Bands(bid, ask, int(janela*volta), desvio)
                 sinal_action[ind] = plota_negociatas(bid,ask, lower_band, upper_band)
                 volta += .5

            del batch[:-batch_size - 10]
            batch.append([[sinal_action[0]], [sinal_action[1]],[sinal_action[2]],[sinal_action[3]], [sinal_action[4]], [sinal_action[5]], [bid_mean], [ask_mean]])



            if len(batch) >= batch_size: 
                for ind in range(0,6):       
 
                    if sinal_action[ind] == 1:
                        if historico[ind] != "COMPRA":
                            compras[ind] = float(ask[-1:])
                            X_temp[ind] = batch[-batch_size:]
                            print("--**--** COMPRA - ", str(float( compras[ind])))
                        if historico[ind] == "COMPRA":
                            compras[ind] = float(ask[-1:])
                            X.append(X_temp[ind])
                            Y.append(0)
                            X_temp[ind] = batch[-batch_size:]
                            compras[ind] = float(ask[-1:])
                            epoch += 1

                        historico[ind] = "COMPRA" 


                    if sinal_action[ind] == 2 and historico[ind]!= "":
                        vendas[ind] = float(bid[-1:])
                        epoch += 1
                        lucro = float(float(vendas[ind]) - float(compras[ind]))

                        lucro_total += lucro
                        print("--**--** VENDA ", str(float( vendas[ind]))," - Lucro = US$ ", str(lucro))
                        if lucro > 0:
                            try:
                                X.append(X_temp[ind])
                                Y.append(np.array(1))
                                X.append(batch[-batch_size:])
                                Y.append(np.array(2))
                            except:
                                pass
                        if lucro <= 0 or historico[ind] =="VENDA":
                            try:
                                X.append(X_temp[ind])
                                Y.append(np.array(0))
                                X.append(batch[-batch_size:])
                                Y.append(np.array(0))
                            except:
                                pass 

 
                        historico[ind] = "VENDA" 

        try:
            X_0 = np.array(X)
            X0 = X_0.reshape(len(Y),-1)
            y = np.array(Y)  


 
        except:
            pass

        if epoch % 50 == 0 and epoch > 0:
 

             svm.fit(X0,y)
             joblib.dump(svm, "modelo-"+str(epoch)+".pkl", compress=3)
             print("--*--* Modelo Salvo - modelo-"+str(epoch)+".pkl")
        print("Batch Total", len(batch))
        print("Epoch - ", str(epoch))
        plt.pause(intervalo)


volta = 1
while True:
    print("--------------------------- ")
    print("Tickers - ", volta)
    volta += 1 
    try:
        get_tickers()
    except:
        print("Erro no servidor - aguarde 5 segundos.")
        time.sleep(5)
        pass 
    try:
        main()
    except:
        print("- - ENCERRANDO --")
        exit()  
