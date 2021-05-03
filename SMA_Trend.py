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

stock = '^BVSP'
SMA = SMA_Mov(dataFrame=Close_Price, colName=stock)

# Plotly Chart
fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(go.Scatter(x=SMA.index, y=SMA[stock], name=stock, line=dict(color="#1f77b4")), secondary_y=False)
fig.add_trace(go.Scatter(x=SMA.index, y=SMA[f'SMA_{shortSMA}'], name="Short SMA SPY", line=dict(color="#ff7f0e")), secondary_y=False)
fig.add_trace(go.Scatter(x=SMA.index, y=SMA[f'SMA_{longSMA}'], name="Long SMA SPY", line=dict(color="#e377c2")), secondary_y=False)
fig.add_trace(go.Scatter(x=SMA.index, y=SMA['Position'], name="Position", line=dict(color="#7f7f7f")), secondary_y=True)
fig.show();

# Calculate returns
# Slice Dataframe
IniDate="2010-01-01"
Return_DF = SMA.loc[SMA.index>=IniDate].dropna()
Return_DF['Daily_Return'] = np.log(Return_DF[stock]/Return_DF[stock].shift(1))

fig = px.histogram(Return_DF, x='Daily_Return', nbins=35)
fig.show()

Return_DF['Daily_Return_Strategy'] = Return_DF['Position'] * Return_DF['Daily_Return']

# Strat Return X Long only return
# Profit
Return_DF[['Daily_Return', 'Daily_Return_Strategy']].sum().apply(np.exp)
# Annualized mid return
np.exp(Return_DF[['Daily_Return', 'Daily_Return_Strategy']].mean() * 252) - 1
# Volatility
(Return_DF[['Daily_Return', 'Daily_Return_Strategy']].apply(np.exp) - 1).std() * 252 ** 0.5

Plot_DF = Return_DF[['Daily_Return', 'Daily_Return_Strategy']].cumsum().apply(np.exp)

fig = go.Figure()
fig.add_trace(go.Scatter(x=Plot_DF.index, y=Plot_DF['Daily_Return'], mode='lines', name="Return"))
fig.add_trace(go.Scatter(x=Plot_DF.index, y=Plot_DF['Daily_Return_Strategy'], mode='lines', name="Strat Return"))

fig.update_layout(
    title="Return X Strat Return"
    ,xaxis_title="Refdate"
    ,yaxis_title="(%)"
)

fig.show();