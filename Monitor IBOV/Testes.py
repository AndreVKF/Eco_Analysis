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



yFinance_Wrapper.priceHistoryChart(ticker='IBOV')

yFinance_Wrapper.Ibov_Data
yFinance_Wrapper.Price_Data

yFinance_Wrapper.update()
yFinance_Wrapper.ibovStocksDes()
yFinance_Wrapper.getIbovEquitiesLastUpdate()


stock = 'ABEV3.SA'

SMA_Short = 22
SMA_Long = 88

Price_Data =  pd.DataFrame(yFinance_Wrapper.Price_Data['Close'][stock].dropna())
Price_Data['SMA Short'] = Price_Data[stock].rolling(SMA_Short).mean()
Price_Data['SMA Long'] = Price_Data[stock].rolling(SMA_Long).mean()

# pd.reset_option('display.max_rows')