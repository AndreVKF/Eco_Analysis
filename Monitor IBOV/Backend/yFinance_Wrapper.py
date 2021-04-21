import pandas as pd
import numpy as np

import yfinance as yf

from datetime import date

class yFinance_Wrapper:
    def __init__(self, Refdate=date.today()):
        self.Refdate = Refdate

    def getIbovEquitiesLastUpdate(self):
        """Generate updated DataFrame with price change
            for stocks in the IBOV index.

        Returns:
            [pd.DataFrame]: [DataFrame with price changes]
        """        

        # Make Request and Adjust Response DataFrame
        Ibov_Stocks = pd.read_csv("Csv/Acoes_IBOV.csv", sep=";")
        Ibov_Stocks['Yahoo_Ticker'] = Ibov_Stocks['Ticker'].apply(lambda x: str(x).split(sep=" ")[0]+".SA").to_list()
        Price_Data = yf.download(Ibov_Stocks['Yahoo_Ticker'].to_list(), period="1Y")

        # Base Dates
        Base_Year = Price_Data.index[-1].year
        Base_Month = Price_Data.index[-1].month
        Base_Day = Price_Data.index[-1].day

        # Price Evolution Data Frame
        Price_DF = pd.DataFrame({
            "Px_Last": Price_Data.iloc[-1]['Close'].values,
            "Open": Price_Data.iloc[-1]['Open'].values,
            "MTD_Open": Price_Data.loc[(Price_Data.index.date>=date(Base_Year, Base_Month, 1))].iloc[0, :]['Open'],
            "YTD_Open": Price_Data.loc[(Price_Data.index.date>=date(Base_Year, 1, 1))].iloc[0, :]['Open'],
            "12M_Open": Price_Data.iloc[0]['Open'].values,
        }, index=Price_Data.iloc[-1]['Open'].index)

        # Calculate price change / percent change
        Price_DF['1D_Delta'] = Price_DF['Px_Last'] - Price_DF['Open']

        Price_DF['DTD_Change'] = Price_DF['Px_Last']/Price_DF["Open"] - 1
        Price_DF['MTD_Change'] = Price_DF['Px_Last']/Price_DF["MTD_Open"] - 1
        Price_DF['YTD_Change'] = Price_DF['Px_Last']/Price_DF["YTD_Open"] - 1
        Price_DF['12M_Change'] = Price_DF['Px_Last']/Price_DF["12M_Open"] - 1

        # Adjust with GICS Sector
        Price_DF = Price_DF.merge(Ibov_Stocks[['Yahoo_Ticker', 'GICS_Sector']], how='left', left_index=True, right_on=['Yahoo_Ticker'])
        Price_DF.set_index(['GICS_Sector', 'Yahoo_Ticker'], inplace=True)

        Price_DF = Price_DF.groupby(level=[0, 1]).sum()

        # Return DF
        Res_DF = Price_DF[[
            "Px_Last",
            "1D_Delta",
            "DTD_Change",
            "MTD_Change",
            "YTD_Change",
            "12M_Change"]]

        return Res_DF