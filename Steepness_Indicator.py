import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import yfinance as yf

from datetime import date

# Variáveis/Objetos locais
Today = date.today()

Price_Data = yf.download("SPY ^BVSP", start="2001-01-01", end=Today.strftime("%Y-%m-%d"))
Close_Price = Price_Data['Close']

################### Steepness Indicator ###################
def SteepIndicator_pd(df, col_name, steep_SMA=22, steep_period=3, n_points_chart=False, return_df=False):
    raw = pd.DataFrame(df[col_name]).dropna()

    # Cria DataFrame com Slope
    raw[f'SMA_{steep_SMA}'] = raw[col_name].rolling(steep_SMA).mean()
    raw[f'Slope_{steep_period}'] = (raw[f'SMA_{steep_SMA}'] - raw[f'SMA_{steep_SMA}'].shift(steep_period))/steep_period

    # Cria Chart
    plot_df = raw.copy()
    
    if type(n_points_chart)==int:
        plot_df = plot_df.iloc[n_points_chart:,:]

    fig, axs = plt.subplots(2, 1, figsize=(15, 15))
    axs[0].plot(plot_df.index, plot_df[f'SMA_{steep_SMA}'], 'tab:blue')
    axs[0].set_title(f'SMA_{col_name}_{steep_SMA}')
    axs[0].grid()

    axs[1].plot(plot_df.index, plot_df[f'Slope_{steep_period}'], 'tab:red')
    axs[1].set_title(f'Steepness Indicator({col_name}, {steep_SMA}, {steep_period})')
    axs[1].axhline(y=0, linewidth=2, color='black')
    axs[1].grid()
    plt.show;

    # Return DataFrame
    if return_df:
        return raw


steep_SMA = 8
steep_period=3

SY_Px_Steep = SteepIndicator_pd(df=Close_Price, col_name='SPY', steep_SMA=steep_SMA, steep_period=steep_period, n_points_chart=-252, return_df=True)
IBOV_Px_Steep = SteepIndicator_pd(df=Close_Price, col_name='^BVSP', steep_SMA=steep_SMA, steep_period=steep_period, n_points_chart=-252, return_df=True)
