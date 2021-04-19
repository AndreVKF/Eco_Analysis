import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import yfinance as yf

from datetime import date

# Variáveis/Objetos locais
Today = date.today()

Price_Data = yf.download("SPY ^BVSP", start="2001-01-01", end=Today.strftime("%Y-%m-%d"))
Close_Price = Price_Data['Close']

# Function to genererate outstrech values
def Outstretched_Indicator(df, name_col, momentum_lookback=3, avg_lookback=3, n_points_chart=False, return_df=False):
    # DataFrame Manipular
    Raw_DF = pd.DataFrame(df[name_col]).dropna()

    Raw_DF[f'{momentum_lookback}D_Change'] = (Raw_DF - Raw_DF.shift(momentum_lookback))
    Raw_DF[f'{momentum_lookback}D_Change_Side'] = np.where(Raw_DF[f'{momentum_lookback}D_Change']>0, 1, -1)

    Raw_Outstretch = []
    
    # Loop to get oustretch
    for index, row in Raw_DF.iterrows():
        if Raw_DF.index.get_loc(index)<momentum_lookback:
            Raw_Outstretch.append(np.nan)
            
        else:
            # Positive Outstretch
            Pos_Out_DF = Raw_DF.loc[:index].loc[(Raw_DF[f'{momentum_lookback}D_Change'].notna()) & (Raw_DF[f'{momentum_lookback}D_Change_Side']==1)]
            Neg_Out_DF = Raw_DF.loc[:index].loc[(Raw_DF[f'{momentum_lookback}D_Change'].notna()) & (Raw_DF[f'{momentum_lookback}D_Change_Side']==-1)]

            # Check if has 3 Pos and 3 Neg Values
            if len(Pos_Out_DF)>=3 and len(Neg_Out_DF)>=3:
                Outstretch = Pos_Out_DF.tail(3)[f'{momentum_lookback}D_Change'].sum() + Neg_Out_DF.tail(3)[f'{momentum_lookback}D_Change'].sum()
            else:
                Outstretch = np.nan

            Raw_Outstretch.append(Outstretch)

    # Insert Outstrech Data into DataFrame
    Raw_DF['Raw_Outstretch'] = np.array(Raw_Outstretch)
    Raw_DF['Outstretch_Indicator'] = Raw_DF['Raw_Outstretch'].ewm(span=avg_lookback, adjust=False).mean()

    # Cria Chart
    plot_df = Raw_DF.copy()
    
    if type(n_points_chart)==int:
        plot_df = plot_df.iloc[n_points_chart:,:]

    fig, axs = plt.subplots(2, 1, figsize=(15, 15))
    axs[0].plot(plot_df.index, plot_df[name_col], 'tab:blue')
    axs[0].set_title(name_col)
    axs[0].grid()

    axs[1].plot(plot_df.index, plot_df[f'Outstretch_Indicator'], 'tab:red')
    axs[1].set_title(f'Outstretch_Indicator_{name_col}')
    axs[1].axhline(y=0, linewidth=2, color='black')
    axs[1].grid()
    plt.show;

    if return_df:
        return Raw_DF

SP_Outstretch = Outstretched_Indicator(df=Close_Price, name_col='SPY', momentum_lookback=3, avg_lookback=3, return_df=True)
IBOV_Outstretch = Outstretched_Indicator(df=Close_Price, name_col='^BVSP', momentum_lookback=3, avg_lookback=3, return_df=True)