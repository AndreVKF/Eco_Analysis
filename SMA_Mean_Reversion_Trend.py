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

################### SMA Moving with Bollinger Bands ###################
def SMA_Bollinger_Bands(dataFrame, colName, smaPeriod=44, nStdDev=2):
    base_DF = pd.DataFrame(dataFrame[colName]).dropna()

    # Add Simple Moving Avg
    base_DF['SMA'] = base_DF[colName].rolling(smaPeriod).mean()
    # Add Rolling Std Dev
    base_DF['Std_Dev'] = base_DF[colName].rolling(smaPeriod).std()

    # Add Bollinger Bands
    base_DF['Upper Band'] = base_DF['SMA'] + (nStdDev * base_DF['Std_Dev'])
    base_DF['Lower Band'] = base_DF['SMA'] - (nStdDev * base_DF['Std_Dev'])

    # Add Cross Bands
    base_DF['Cross Upper Band'] = np.where(base_DF[colName]>base_DF['Upper Band'], 1, 0)
    base_DF['Cross Lower Band'] = np.where(base_DF[colName]<base_DF['Lower Band'], 1, 0)

    base_DF['Position'] = 0

    # Adjust Sell Position
    lastBaseDate = date(1900, 1, 1)
    for index, row in base_DF.loc[base_DF['Cross Upper Band']==1].iterrows():
        # Check if last base date already been stablished with position
        if lastBaseDate>index:
            continue
        
        # Second row starting from index where there is crossing on the Bollinger
        slice_DF = base_DF.loc[index:].iloc[1:]
        # Get moment when normalize value
        slice_DF['Cross SMA'] = np.where(slice_DF[colName]<slice_DF['SMA'], 1, 0)
        # Sliced DatraFrame where crosses avg
        cross_DF = slice_DF.loc[slice_DF['Cross SMA']==1]

        baseIndex = slice_DF.head(1).index.date[0]

        # Check if normalize occurs
        if cross_DF.empty:
            base_DF.loc[baseIndex:, 'Position'] = -1
            break
        else:
            # Get index where normalize happens
            endIndex = cross_DF.head(1).index.date[0]
            base_DF.loc[baseIndex:endIndex, 'Position'] = -1

            
    # Adjust Buy Position
    lastBaseDate = date(1900, 1, 1)
    for index, row in base_DF.loc[base_DF['Cross Lower Band']==1].iterrows():
        # Check if last base date already been stablished with position
        if lastBaseDate>index:
            continue
        
        # Second row starting from index where there is crossing on the Bollinger
        slice_DF = base_DF.loc[index:].iloc[1:]
        # Get moment when normalize value
        slice_DF['Cross SMA'] = np.where(slice_DF[colName]>slice_DF['SMA'], 1, 0)
        # Sliced DatraFrame where crosses avg
        cross_DF = slice_DF.loc[slice_DF['Cross SMA']==1]

        baseIndex = slice_DF.head(1).index.date[0]

        # Check if normalize occurs
        if cross_DF.empty:
            base_DF.loc[baseIndex:, 'Position'] = +1
            break
        else:
            # Get index where normalize happens
            endIndex = cross_DF.head(1).index.date[0]
            base_DF.loc[baseIndex:endIndex, 'Position'] = +1

    return base_DF

colName = "SPY"
base_DF = SMA_Bollinger_Bands(Close_Price, colName=colName, smaPeriod=44, nStdDev=2)

fig = make_subplots(specs=[[{"secondary_y": True}]])

# Chart with SMA and Price Data
fig.add_trace(go.Scatter(x=base_DF.index, y=base_DF[colName], mode='lines', name=colName), secondary_y=False)
fig.add_trace(go.Scatter(x=base_DF.index, y=base_DF["SMA"], mode='lines', name='SMA'), secondary_y=False)
fig.add_trace(go.Scatter(x=base_DF.index, y=base_DF["Upper Band"], mode='lines', line=dict(color="#bcbd22"), name='Upper Band'), secondary_y=False)
fig.add_trace(go.Scatter(x=base_DF.index, y=base_DF["Lower Band"], mode='lines', line=dict(color="#bcbd22"), name='Lower Band'), secondary_y=False)

# Chart with position
fig.add_trace(go.Scatter(x=base_DF.index, y=base_DF["Position"], mode='lines', line=dict(color="#7f7f7f"), name='Position'), secondary_y=True)

fig.update_layout(
    title="Bollinger Bands Retrace Strat"
    ,xaxis_title="Refdate"
)

fig.update_yaxes(title_text="<b>Price</b>", secondary_y=False)
fig.update_yaxes(title_text="<b>Position</b>", secondary_y=True)

fig.show();

############### Calculate returns ###############
Return_DF = base_DF.dropna()
Return_DF['Daily_Return'] = np.log(Return_DF[colName]/Return_DF[colName].shift(1))
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