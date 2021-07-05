import pandas as pd
import numpy as np

import yfinance as yf

from datetime import date

from Backend.yFinance_Wrapper import *

yFinance_Wrapper = yFinance_Wrapper()
yFinance_Wrapper.update()
yFinance_Wrapper.getIbovEquitiesLastUpdate(GICS_Segment="Industry")

ibovEquitiesData = yFinance_Wrapper.getIbovEquitiesLastUpdate(GICS_Segment="Industry")
ibovEquitiesData.data.to_csv("C:\\Users\\André Viniciu\\OneDrive\\Pasta\\Documentos\\IBOV Data\\LastData.csv")

ticker = "BRFS3.SA"
yFinance_Wrapper.priceHistoryOLHCChart(ticker=ticker)

# Show Ibov Stocks Update Table
yFinance_Wrapper.getIbovEquitiesLastUpdate()

yFinance_Wrapper.update()

# Boxplot
Des_DF = yFinance_Wrapper.ibovStocksDes()
Fin_Tickers = Des_DF.loc[Des_DF['GICS_Sector']=='Materials']['Yahoo_Ticker'].to_list()

yFinance_Wrapper.priceHistoryBoxPlot(tickers=Fin_Tickers)

# Equities KPIs
yFinance_Wrapper.equitiesKPIData()
