import pandas as pd
import numpy as np
import math

import matplotlib.pyplot as plt

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

import yfinance as yf

from datetime import date

# Variáveis/Objetos locais
Today = date.today()

# Get Price Data
Price_Data = yf.download("SPY ^BVSP", start="2001-01-01", end=Today.strftime("%Y-%m-%d"))
Close_Price = Price_Data['Close']

################### SMA Moving Avgs Trend Function ###################
def SMA_Mov(dataFrame, colName, shortSMA=22, longSMA=66, printReturn=False):
    base_DF = pd.DataFrame(dataFrame[colName]).dropna()

    base_DF[f'SMA_{shortSMA}'] = base_DF[colName].rolling(shortSMA).mean()
    base_DF[f'SMA_{longSMA}'] = base_DF[colName].rolling(longSMA).mean()

    # Signal when Short Mov. Avg crosses Long Mov. Avg
    base_DF['Signal'] = np.where(base_DF[f'SMA_{shortSMA}']>=base_DF[f'SMA_{longSMA}'], 1, -1)

    posChange_listTuples = list(enumerate(np.where(base_DF['Signal'].shift(1)!=base_DF['Signal'], -1, 0)))
    posChange_list = [item[0] for item in posChange_listTuples if item[1]==-1]

    # Adjust position 
    # Change in position happens 1D after trend change
    base_DF['Position'] = base_DF['Signal']
    base_DF.iloc[:posChange_list[1], base_DF.columns.get_loc('Position')] = 0

    base_DF['Position'] = base_DF['Position'].shift(1)
    base_DF.iloc[0, base_DF.columns.get_loc('Position')] = 0

    Prof_DF = base_DF.loc[base_DF['Position']!=0][[colName, 'Position']].copy()
    Prof_DF['1D_Return'] = Prof_DF[colName].pct_change()
    Prof_DF['1D_Log_Return'] = np.log(1+Prof_DF['1D_Return'])

    if printReturn:
        print(f"""
            Buy long return: {np.exp(Prof_DF['1D_Log_Return'].sum())-1}
            SMA trend return: {np.exp((Prof_DF['1D_Log_Return']*Prof_DF['Position']).sum())-1}
        """
        )

    return base_DF


# Variáveis locais
shortSMA = 22
longSMA = 66

SMA = SMA_Mov(dataFrame=Close_Price, colName='SPY')


# Plotly Chart
fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(go.Scatter(x=SMA.index, y=SMA['SPY'], name="SPY", line=dict(color="#1f77b4")), secondary_y=False)
fig.add_trace(go.Scatter(x=SMA.index, y=SMA[f'SMA_{shortSMA}'], name="Short SMA SPY", line=dict(color="#ff7f0e")), secondary_y=False)
fig.add_trace(go.Scatter(x=SMA.index, y=SMA[f'SMA_{longSMA}'], name="Long SMA SPY", line=dict(color="#e377c2")), secondary_y=False)
fig.add_trace(go.Scatter(x=SMA.index, y=SMA['Position'], name="Position", line=dict(color="#7f7f7f")), secondary_y=True)
fig.show();


# plot_DF = SMA.tail(252)

# fig, axs = plt.subplots(2, 1)
# axs[0].plot(plot_DF.index, plot_DF[['SPY', 'SMA_22', 'SMA_66']])
# axs[1].plot(plot_DF.index, plot_DF['Signal'])
# fig.show();

# figura = px.line(title = f'SMA')
# figura.add_scatter(x=SMA.index, y=SMA['SPY'], name='USDBRL', mode='lines')
# figura.add_scatter(x=SMA.index, y=SMA['SMA_22'], name='SMA_22', line_color='#ff7f0e', line_dash="dash")
# figura.add_scatter(x=SMA.index, y=SMA['SMA_66'], name='SMA_66', line_color='#2ca02c', line_dash="dash")
# figura.show();
