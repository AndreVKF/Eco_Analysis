import pandas as pd
import numpy as np

import yfinance as yf

# List of Stocks from Ibovespa
Stocks = pd.read_csv("Csv/Acoes_IBOV.csv", sep=";")

List_Stocks = Stocks['Ticker'].apply(lambda x: str(x).split(sep=" ")[0]+".SA").to_list()

Price_Data = yf.download(List_Stocks, period="1D")

# Pivot Data
Price_Data = Price_Data[['Open', 'Close']]
Price_DF = Price_Data['Open'].T.rename(columns={Price_Data['Open'].T.columns[0]: 'Open'}).merge(Price_Data['Close'].T.rename(columns={Price_Data['Close'].T.columns[0]: "Px_last"}), how='left', left_index=True, right_index=True)