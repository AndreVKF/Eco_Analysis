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

def Correlation_Adjusted_Reversal_Indicator(priceDF, colName, n_periods=6, corr_window=10):
    """Generate and Returns DataFrame with the Correlation Adjusted Reversal Indicator

    Args:
        priceDF (pd.DataFrame): DataFrame with historic price data
        colName (string): Asset to be used
        n_periods (int, optional): Number of previous periods deltas. Defaults to 6.
        corr_window (int, optional): Rolling correlation period. Defaults to 10.
    """    

    Px_Data = pd.DataFrame({
            "Px_Last": Price_Data['Adj Close'][colName]}
            ,index=Price_Data.index)


    # Price changes up to n periods
    for i in range(1, n_periods+1):
        Px_Data[f'{i}D_Change'] = Px_Data['Px_Last'] - Px_Data['Px_Last'].shift(i)

    # List of columns with price changes
    colChanges = [x for x in Px_Data.columns.to_list() if x != "Px_Last"]

    # Calculate mean of price changes
    Px_Data['Mean_Days_Change'] = Px_Data[colChanges].mean(axis=1)

    # Correlation between Px_Last and Mean_Days_Change
    Px_Data['Corr_Px_Mean_Change'] = Px_Data['Px_Last'].rolling(corr_window).corr(Px_Data['Mean_Days_Change'])

    # Set threshold for Correlation
    Index_To_Zero = Px_Data.loc[(Px_Data['Corr_Px_Mean_Change']<0.75) & (Px_Data['Corr_Px_Mean_Change']>-0.75)].index
    Px_Data.loc[Index_To_Zero, 'Mean_Days_Change'] = 0

    return Px_Data.dropna()


colName = "SPY"
Corr_Adj_DF = Correlation_Adjusted_Reversal_Indicator(priceDF=Price_Data, colName=colName)

periodToPlot = -252
plotDF = Corr_Adj_DF.iloc[periodToPlot:]

# PLot Correlation Data
fig = make_subplots(rows=2, cols=1
    , subplot_titles=(f"Px_Last {colName}", "Adjuste Corr. Px_Last Mean"))

fig.add_trace(
    go.Scatter(x=plotDF.index,
        y=plotDF['Px_Last'].values,
        mode='lines',
        name=f"{colName}")
    ,row=1, col=1
)

fig.add_trace(
    go.Scatter(x=plotDF.index,
        y=plotDF['Mean_Days_Change'].values,
        mode='lines',
        name="Mean Px Last Corr. Adj.")
    ,row=2, col=1
)

fig.update_layout(title_text="Correlation Adjusted Reversal Indicator")
fig.show();