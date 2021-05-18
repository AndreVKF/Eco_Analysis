import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import yfinance as yf

from datetime import date

from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Variáveis/Objetos locais
Today = date.today()

Price_Data = yf.download("SPY ^BVSP", start="2001-01-01", end=Today.strftime("%Y-%m-%d"))
Close_Price = Price_Data['Close']

# Function to genererate outstrech values
def MACD_Indicator(df, name_col, short_period_EMA=12, long_period_EMA=26, signal_period=9):
    """Function to add columns with short EMA, long EMA, MACD and MACD Signal
       Based on the df[name_col] data

    Args:
        df (pandas.DataFrame): Base DataFrame
        name_col (string): Column name to get values on the Base DataFrame
        short_period_EMA (int, optional): Short period EMA. Defaults to 12.
        long_period_EMA (int, optional): Long period EMA. Defaults to 26.
        signal_period (int, optional): Signato EMA from the MACD. Defaults to 9.
    """

    # Local variables/arguments
    Base_DF = df.copy()

    Base_DF['Short_EMA'] = Base_DF[name_col].ewm(span=short_period_EMA, min_periods=short_period_EMA, adjust=False).mean()
    Base_DF['Long_EMA'] = Base_DF[name_col].ewm(span=long_period_EMA, min_periods=long_period_EMA, adjust=False).mean()

    Base_DF['MACD'] = Base_DF['Short_EMA'] - Base_DF['Long_EMA']

    Base_DF['MACD_Signal'] = Base_DF['MACD'].ewm(span=signal_period, adjust=False).mean()

    return Base_DF.dropna()

ticker = 'SPY'
MACD_DF = MACD_Indicator(df=pd.DataFrame(Close_Price[ticker]), name_col='SPY')

# MACD Charts
fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(go.Scatter(
    x=MACD_DF.index
    ,y=MACD_DF[ticker].values
    ,name=ticker
    ,mode="lines"
    ,line=dict(color='#1f77b4')
), secondary_y=False
)

fig.add_trace(go.Scatter(
    x=MACD_DF.index
    ,y=MACD_DF["MACD"].values
    ,name=f"{ticker} MACD"
    ,mode="lines"
    ,line=dict(color='#ff7f0e')
), secondary_y=True
)

fig.add_trace(go.Scatter(
    x=MACD_DF.index
    ,y=MACD_DF["MACD_Signal"].values
    ,name="MACD_Signal"
    ,mode="lines"
    ,line=dict(color='#2ca02c')
), secondary_y=True
)

fig.update_layout(
    title=f"{ticker} MACD & MACD Signal"
)

fig.show();


fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.2)

fig.add_trace(go.Scatter(
    x=MACD_DF.index
    ,y=MACD_DF[ticker].values
    ,name=ticker
    ,mode="lines"
    ,line=dict(color="#1f77b4")
), row=1, col=1)

fig.add_trace(go.Scatter(
    x=MACD_DF.index
    ,y=MACD_DF["MACD"].values
    ,name=f"{ticker} MACD"
    ,mode="lines"
    ,line=dict(color="#ff7f0e")
), row=2, col=1)

fig.update_layout(
    title=f"{ticker} MACD"
)

fig.show();

