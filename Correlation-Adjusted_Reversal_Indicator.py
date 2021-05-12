import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import yfinance as yf

from datetime import date

# Variáveis/Objetos locais
Today = date.today()

Price_Data = yf.download("SPY ^BVSP", start="2001-01-01", end=Today.strftime("%Y-%m-%d"))

Index = 'SPY'
Px_Data = pd.DataFrame({
        "Px_Last": Price_Data['Adj Close'][Index]}
        ,index=Price_Data.index)

n_periods = 6
corr_window = 10

# Price changes up to n periods
for i in range(1, n_periods+1):
    Px_Data[f'{i}D_Change'] = Px_Data['Px_Last'] - Px_Data['Px_Last'].shift(i)

# List of columns with price changes
colChanges = [x for x in Px_Data.columns.to_list() if x != "Px_Last"]

# Calculate mean of price changes
Px_Data['Mean_Days_Change'] = Px_Data[colChanges].mean(axis=1)

Px_Data['Corr_Px_Mean_Change'] = Px_Data['Px_Last'].rolling(corr_window).corr(Px_Data['Mean_Days_Change'])

Index_To_Zero = Px_Data.loc[(Px_Data['Corr_Px_Mean_Change']<0.75) & (Px_Data['Corr_Px_Mean_Change']>-0.75)].index


Px_Data.loc[Index_To_Zero, 'Mean_Days_Change'] = 0

Px_Data['Mean_Days_Change'].iloc[-252:].plot()