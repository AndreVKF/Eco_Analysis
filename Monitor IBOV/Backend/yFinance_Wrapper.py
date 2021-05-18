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
        return self.Ibov_Stocks[self.Ibov_Stocks_Description_Columns].sort_values("Yahoo_Ticker")

        pd.reset_option('display.max_rows')
        pd.reset_option('display.max_columns')


    def getIbovEquitiesLastUpdate(self, GICS_Segment="Industry"):
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

        # Adjust with GICS Segment
        Price_DF = Price_DF.merge(self.Ibov_Stocks[['Yahoo_Ticker', f'GICS_{GICS_Segment}']], how='left', left_index=True, right_on=['Yahoo_Ticker'])
        Price_DF.set_index([f'GICS_{GICS_Segment}', 'Yahoo_Ticker'], inplace=True)

        Price_DF = Price_DF.groupby(level=[0, 1]).sum()

        # Return DF
        Res_DF = Price_DF[[
            "Px_Last",
            "1D_Delta",
            "DTD_Change",
            "MTD_Change",
            "YTD_Change",
            "12M_Change"]]

        # DataFrame Style
        pd.set_option('display.max_rows', len(Res_DF))
        format_dict = {"Px_Last": "{:.2f}"
            ,"1D_Delta": "{:+.2f}"
            ,"DTD_Change": "{:.2%}"
            ,"MTD_Change": "{:.2%}"
            ,"YTD_Change": "{:.2%}"
            ,"12M_Change": "{:.2%}"}
        
        return Res_DF.style.format(format_dict).bar(subset=['DTD_Change', 'MTD_Change', 'YTD_Change', '12M_Change'], align='mid', color=['darkred', 'darkgreen']).applymap(color_negative_red, subset=['1D_Delta'])

    def equitiesKPIData(self, GICS_Segment="Industry"):
        """Function to generate DataFrame with some KPIs Index for equities

        Args:
            GICS_Segment (str, optional): Segmentation by GICS_Segment. Defaults to "Industry".
        """ 
        # List of tickers 
        Tickers_DF = self.ibovStocksDes()
        Tickers_List = Tickers_DF['Yahoo_Ticker'].to_list()

        # Name of fields
        colNames = ["previousClose",
            "marketCap",           
            "beta",
            "trailingAnnualDividendYield",
            "trailingAnnualDividendRate",
            "payoutRatio",
            "dividendRate",
            "trailingPE",
            "forwardPE",
            "dividendYield",
            "enterpriseToRevenue",
            "enterpriseToEbitda",
            "bookValue",
            "trailingEps",
            "forwardEps",
            "priceToBook"]

        Return_DF = pd.DataFrame(columns=colNames)

        # Loop thourgh tickers
        for Ticker in Tickers_List:
            # Request data
            RequestInfo = yf.Ticker(Ticker)
            EquityInfo = RequestInfo.info

            # Json to DataFrame
            Equity_DF = pd.DataFrame.from_dict(EquityInfo, orient="index", columns=[Ticker])

            # Concat Result DataFrame
            Return_DF = pd.concat([Return_DF, Equity_DF.loc[Equity_DF.index.isin(colNames)].T])


        # Adjust with GICS Segment
        Return_DF = Return_DF.merge(self.Ibov_Stocks[['Yahoo_Ticker', f'GICS_{GICS_Segment}']], how='left', left_index=True, right_on=['Yahoo_Ticker'])
        Return_DF.set_index([f'GICS_{GICS_Segment}', 'Yahoo_Ticker'], inplace=True)

        Return_DF = Return_DF.groupby(level=[0, 1]).sum()

        # Adjust Market Cap to million
        Return_DF['marketCap'] = Return_DF['marketCap']/1000000

        # Style DataFrame
        Format_DF = Return_DF
        Format_DF = Format_DF.style.background_gradient(cmap='coolwarm_r', subset=[x for x in colNames if x != "previousClose"])
        Format_DF = Format_DF.set_properties(**{'font-size': '11pt'})

        return Format_DF


    def priceHistoryOLHCChart(self, ticker=False, period=8):
        """Function to generate ohlc history price chart

        Args:
            ticker (str): Name of the ticker. Defaults to False.
            period (int): Number of years to get history. Defaults to 8.
        """
        # Check arguments
        if not ticker:
            return

        elif ticker=='IBOV':
            # Data Frame with Price Data
            Plot_DF = pd.DataFrame({"Open": self.Ibov_Data["Open"]
                ,"Close": self.Ibov_Data["Close"]
                ,"High": self.Ibov_Data["High"]
                ,"Low": self.Ibov_Data["Low"]
                ,"Volume": self.Ibov_Data["Volume"]
            }, self.Ibov_Data.index).dropna()

        else:
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

    def priceHistorySMAChart(self, ticker=False, period=8, sma_short=22, sma_long=88):
        """Function to generate history price chart

        Args:
            ticker (str): Name of the ticker. Defaults to False.
            period (int): Number of years to get history. Defaults to 8.
            sma_short (int): Short simple moving avg. period
            sma_long (int): Long simple moving avg. period
        """

         # Check arguments
        if not ticker:
            return
        # Price DataFrame
        elif ticker=='IBOV':
            Price_Data =  pd.DataFrame(self.Ibov_Data['Close'].dropna())
            Price_Data.rename(columns={'Close': 'IBOV'})
        else:
            Price_Data =  pd.DataFrame(self.Price_Data['Close'][ticker].dropna())

        # Add moving avgs
        Price_Data['SMA Short'] = Price_Data[ticker].rolling(sma_short).mean()
        Price_Data['SMA Long'] = Price_Data[ticker].rolling(sma_long).mean()

        # Remove na
        Price_Data.dropna(inplace=True)
        # Slice DataFrame
        Price_Data = Price_Data.iloc[-252*period:]

        # Create chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=Price_Data.index
            ,y=Price_Data[ticker]
            ,mode="lines"
            ,line=dict(color="#1f77b4")
            ,name=ticker))

        fig.add_trace(go.Scatter(x=Price_Data.index
            ,y=Price_Data['SMA Short']
            ,mode="lines"
            ,line=dict(color="#2ca02c")
            ,name="Short SMA"))

        fig.add_trace(go.Scatter(x=Price_Data.index
            ,y=Price_Data['SMA Long']
            ,mode="lines"
            ,line=dict(color="#d62728")
            ,name="Long SMA"))

        fig.update_layout(
            title=f"Price History {ticker}"
            ,yaxis_title=f"PX_Last"
        )

        fig.show()

    def priceHistoryBoxPlot(self, tickers, years=3):
        """Function to generate boxplot chart of tickers

        Args:
            tickers (list): [list of strings of tickers]
            years (int, optional): [number of years of price history]. Defaults to 3.

        Returns:
            boxplot chart
        """

        # DataFrame Historic Prices
        Price_DF = self.Price_Data['Close'].iloc[-252*years:]

        # Current Price Data
        Price_DF.iloc[-1:][tickers].columns

        # Initiate figure object
        fig = go.Figure()

        # Loop through tickers to add to boxplot chart
        for ticker in tickers:
            fig.add_trace(go.Box(y=Price_DF[ticker].dropna().values, name=ticker, boxmean=True))

        # Add last data point
        fig.add_trace(go.Scatter(x=Price_DF.iloc[-1:][tickers].columns.to_list(), y=Price_DF.iloc[-1:][tickers].values.tolist()[0], mode="markers", marker_symbol="x-dot", marker_color="black", name="LAST PRICE"))
        fig.show();
    

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