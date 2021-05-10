import pandas as pd
import numpy as np

import yfinance as yf

from datetime import date

from Backend.yFinance_Wrapper import *

yFinance_Wrapper = yFinance_Wrapper()
yFinance_Wrapper.update()
Ibov_Price_Data = yFinance_Wrapper.getIbovEquitiesLastUpdate()

ticker = "BRFS3.SA"
yFinance_Wrapper.priceHistoryOLHCChart(ticker=ticker)

# Show Ibov Stocks Update Table
yFinance_Wrapper.getIbovEquitiesLastUpdate()

yFinance_Wrapper.update()

# Financials Equities
Des_DF = yFinance_Wrapper.ibovStocksDes()
Fin_Tickers = Des_DF.loc[Des_DF['GICS_Sector']=='Financials']['Yahoo_Ticker'].to_list()

yFinance_Wrapper.priceHistoryBoxPlot(tickers=Fin_Tickers)