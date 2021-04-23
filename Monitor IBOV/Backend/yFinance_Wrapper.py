import pandas as pd
import numpy as np

import yfinance as yf

import plotly.graph_objects as go

from datetime import date

class yFinance_Wrapper:
    def __init__(self, Refdate=date.today()):
        self.Refdate = Refdate

        # Variables
        self.Ibov_Stocks_Description_Columns = [
            "Yahoo_Ticker"
            ,"Name"
            ,"GICS_Sector"
            ,"GICS_Industry"
        ]

        # Stocks Table
        # Make Request and Adjust Response DataFrame
        self.Ibov_Stocks = pd.read_csv("Csv/Acoes_IBOV.csv", sep=";")
        self.Ibov_Stocks['Yahoo_Ticker'] = self.Ibov_Stocks['Ticker'].apply(lambda x: str(x).split(sep=" ")[0]+".SA").to_list()
        self.Price_Data = yf.download(self.Ibov_Stocks['Yahoo_Ticker'].to_list(), period="max")

        # IBOV data 
        self.Ibov_Data = yf.download('^BVSP', period='max')


    def update(self):
        """Update Prices
        """        
        # Update Prices
        self.Price_Data = yf.download(self.Ibov_Stocks['Yahoo_Ticker'].to_list(), period="max")
        self.Ibov_Data = yf.download('^BVSP', period='max')

    def ibovStocksDes(self):
        """Show Stocks Description Info
        """
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        print(self.Ibov_Stocks[self.Ibov_Stocks_Description_Columns].sort_values("Yahoo_Ticker"))   

        pd.reset_option('display.max_rows')
        pd.reset_option('display.max_columns')


    def getIbovEquitiesLastUpdate(self):
        """Generate updated DataFrame with price change
            for stocks in the IBOV index.

        Returns:
            [pd.DataFrame]: [DataFrame with price changes]
        """        
        Price_Data = self.Price_Data.copy()

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
            "12M_Open": Price_Data.loc[(Price_Data.index.date>=date(Base_Year-1, Base_Month, Base_Day))].iloc[0, :]['Open'],
        }, index=Price_Data.iloc[-1]['Open'].index)

        # Calculate price change / percent change
        Price_DF['1D_Delta'] = Price_DF['Px_Last'] - Price_DF['Open']

        Price_DF['DTD_Change'] = Price_DF['Px_Last']/Price_DF["Open"] - 1
        Price_DF['MTD_Change'] = Price_DF['Px_Last']/Price_DF["MTD_Open"] - 1
        Price_DF['YTD_Change'] = Price_DF['Px_Last']/Price_DF["YTD_Open"] - 1
        Price_DF['12M_Change'] = Price_DF['Px_Last']/Price_DF["12M_Open"] - 1

        # Adjust with GICS Sector
        Price_DF = Price_DF.merge(self.Ibov_Stocks[['Yahoo_Ticker', 'GICS_Sector']], how='left', left_index=True, right_on=['Yahoo_Ticker'])
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

    def priceHistoryChart(self, ticker=False, period=8):
        """Function to generate ohlc history price chart

        Args:
            ticker (str): Name of the ticker. Defaults to False.
            period (int): Number of years to get history. Defaults to 8.
        """
        # Check arguments
        if not ticker:
            return

        # Data Frame with Price Data
        Plot_DF = pd.DataFrame({"Open": self.Price_Data["Open"][ticker]
            ,"Close": self.Price_Data["Close"][ticker]
            ,"High": self.Price_Data["High"][ticker]
            ,"Low": self.Price_Data["Low"][ticker]
            ,"Volume": self.Price_Data["Volume"][ticker]
        }, self.Price_Data.index).dropna()

        Plot_DF = Plot_DF.iloc[-252*period:]

        # Plotly object
        fig = go.Figure(data=go.Ohlc(
            x=Plot_DF.index
            ,open=Plot_DF['Open']
            ,high=Plot_DF['High']
            ,low=Plot_DF['Low']
            ,close=Plot_DF['Close']
        ))
        fig.update_layout(
            title=f"Price History OHLC"
            ,yaxis_title=f"{ticker}"
        )
        fig.update(layout_xaxis_rangeslider_visible=False)
        fig.show()
        

    

####################### Format Options #######################
def color_negative_red(value):
    """
    Colors elements in a dateframe
    green if positive and red if
    negative. Does not color NaN
    values.
    """

    if value < 0:
        color = '#FF6666'
    elif value > 0:
        color = 'lightgreen'
    else:
        color = 'white'

    return 'color: %s' % color