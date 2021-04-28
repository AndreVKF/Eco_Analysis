import pandas as pd
import numpy as np

import yfinance as yf

from datetime import date

from Backend.yFinance_Wrapper import *

yFinance_Wrapper = yFinance_Wrapper()
Ibov_Price_Data = yFinance_Wrapper.getIbovEquitiesLastUpdate()

yFinance_Wrapper.Ibov_Stocks
yFinance_Wrapper.Price_Data.columns.get_level_values(0).unique()

ticker = "ABEV3.SA"
yFinance_Wrapper.priceHistoryChart(ticker=ticker)

# Show Ibov Stocks Update Table
pd.set_option('display.max_rows', len(Ibov_Price_Data))
format_dict = {"Px_Last": "{:.2f}"
    ,"1D_Delta": "{:+.2f}"
    ,"DTD_Change": "{:.2%}"
    ,"MTD_Change": "{:.2%}"
    ,"YTD_Change": "{:.2%}"
    ,"12M_Change": "{:.2%}"}
Ibov_Price_Data.style.format(format_dict).bar(subset=['DTD_Change', 'MTD_Change', 'YTD_Change', '12M_Change'], align='mid', color=['darkred', 'darkgreen']).applymap(color_negative_red, subset=['1D_Delta'])
pd.reset_option('display.max_rows')


yFinance_Wrapper.Ibov_Stocks.to_json(index=False)