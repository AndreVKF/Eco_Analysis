import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import yfinance as yf

from datetime import date

from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Variáveis/Objetos locais
Today = date.today()

Price_Data = yf.download("SPY ^BVSP", start="2001-01-01", end=Today.strftime("%Y-%m-%d"))
Close_Price = Price_Data['Close']

# Function to genererate outstrech values
def MACD_Indicator(df, name_col, short_period_EMA=12, long_period_EMA=26, signal_period=9):
    """Function to add columns with short EMA, long EMA, MACD and MACD Signal
       Based on the df[name_col] data

    Args:
        df (pandas.DataFrame): Base DataFrame
        name_col (string): Column name to get values on the Base DataFrame
        short_period_EMA (int, optional): Short period EMA. Defaults to 12.
        long_period_EMA (int, optional): Long period EMA. Defaults to 26.
        signal_period (int, optional): Signato EMA from the MACD. Defaults to 9.
    """

    # Local variables/arguments
    Base_DF = df.copy()

    Base_DF['Short_EMA'] = Base_DF[name_col].ewm(span=short_period_EMA, min_periods=short_period_EMA, adjust=False).mean()
    Base_DF['Long_EMA'] = Base_DF[name_col].ewm(span=long_period_EMA, min_periods=long_period_EMA, adjust=False).mean()

    Base_DF['MACD'] = Base_DF['Short_EMA'] - Base_DF['Long_EMA']

    Base_DF['MACD_Signal'] = Base_DF['MACD'].ewm(span=signal_period, min_periods=signal_period, adjust=False).mean()

    # Drop na
    Base_DF.dropna(inplace=True)

    # Insert marker Buy/Sell positions
    Base_DF['Delta_MACD_Signal'] = Base_DF['MACD'] - Base_DF['MACD_Signal']
    Base_DF['BS_Signal'] = 0
    Base_DF['Position'] = 0

    BS_Signal_List = []
    BS_Current_Signal = 0
    
    # Loop through dataframe to check Buy/Sell position
    for row_number, (index, row) in enumerate(Base_DF.iterrows()):
        # Get initial BS_Signal
        if BS_Current_Signal==0:
            if row['Delta_MACD_Signal']==0:
                # Ini position equal zero
                continue
            else:
                BS_Current_Signal = 1 if row['Delta_MACD_Signal'] > 0 else -1

        # Check change in current signal
        Current_Delta = 1 if row['Delta_MACD_Signal'] > 0 else -1

        # Case current delta equal current signal position
        if Current_Delta==BS_Current_Signal:
            continue
        else:
            # Update BS_Current_Signal
            BS_Current_Signal = 1 if row['Delta_MACD_Signal'] > 0 else -1

            # Append data to Index List e BS_Position Change and Current Position
            BS_Signal_List.append([index ,BS_Current_Signal])

    # Change Position List
    Buy_Position_Index = [row[0] for row in BS_Signal_List if row[1]==1]
    Sell_Position_Index = [row[0] for row in BS_Signal_List if row[1]==-1]

    # Open Buy/Sell Position
    Base_DF.loc[(Base_DF.index.isin(Buy_Position_Index)), 'BS_Signal'] = 1
    Base_DF.loc[(Base_DF.index.isin(Sell_Position_Index)), 'BS_Signal'] = -1

    # Adjust Position Accordingly to Signals
    Update_Position_List = Base_DF.loc[(Base_DF["BS_Signal"]!=0)]
    Base_DF['Position'] = 0.0

    # Loop to adjust positions
    for i in range(0, len(Update_Position_List)+1):
        # Adjust first row
        if i==0:
            dateEnd = Update_Position_List.iloc[i].name
            Base_DF.loc[:dateEnd].iloc[:-1]['Position'] = 0
        elif i==(len(Update_Position_List)):
            dateIni = Update_Position_List.iloc[i-1].name
            position = Update_Position_List.iloc[i-1]['BS_Signal']

            Base_DF.loc[dateIni:, 'Position'] = position
        
        else:
            dateIni = Update_Position_List.iloc[i-1].name
            dateEnd = Update_Position_List.iloc[i].name
            position = Update_Position_List.iloc[i-1]['BS_Signal']

            Base_DF.loc[dateIni:dateEnd].iloc[:-1]['Position'] = position

    # One day lag to change position side
    Base_DF['Position'] = Base_DF['Position'].shift(1)
    Base_DF.dropna(inplace=True)

    # Cumulate Return Long X MACD Strat
    Base_DF['DTD_Profit'] = np.nan
    Base_DF['DTD_Profit'] = np.log(Base_DF[name_col]/Base_DF[name_col].shift(1))

    Base_DF = Base_DF.loc[Base_DF['Position']!=0].copy()
    Base_DF['Profit'] = np.nan
    Base_DF['Strat_Profit'] = np.nan

    Base_DF['Profit'] = np.exp(Base_DF['DTD_Profit'].cumsum())-1
    Base_DF['Strat_Profit'] = np.exp((Base_DF['DTD_Profit']*Base_DF['Position']).cumsum())-1

    return Base_DF


name_col = '^BVSP'
MACD_DF = MACD_Indicator(df=pd.DataFrame(Close_Price[name_col]), name_col=name_col)

################ Charts ################
nPoints = 0
Plot_DF = MACD_DF.iloc[nPoints:]

##### Price Evolution/Position/Signal #####
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.1)

fig.add_trace(go.Scatter(
    x=Plot_DF.index
    ,y=Plot_DF[name_col].values
    ,name=name_col
    ,mode="lines"
    ,line=dict(color='#1f77b4')
), row=1, col=1
)

fig.add_trace(go.Scatter(
    x=Plot_DF.loc[Plot_DF["BS_Signal"]==1].index
    ,y=Plot_DF.loc[Plot_DF["BS_Signal"]==1][name_col].values
    ,mode="markers"
    ,marker_symbol="triangle-up"
    ,marker_color="#bcbd22"
    ,name="Buy"
), row=1, col=1
)

fig.add_trace(go.Scatter(
    x=Plot_DF.loc[Plot_DF["BS_Signal"]==-1].index
    ,y=Plot_DF.loc[Plot_DF["BS_Signal"]==-1][name_col].values
    ,mode="markers"
    ,marker_symbol="triangle-down"
    ,marker_color="#d62728"
    ,name="Sell"
), row=1, col=1
)

fig.add_trace(go.Scatter(
    x=Plot_DF.index
    ,y=Plot_DF['Position'].values
    ,name="Position"
    ,mode="lines"
    ,line=dict(color='#7f7f7f')
), row=2, col=1
)


fig.add_trace(go.Scatter(
    x=Plot_DF.index
    ,y=Plot_DF["MACD"].values
    ,name=f"{name_col} MACD"
    ,mode="lines"
    ,line=dict(color='#ff7f0e')
), row=3, col=1
)

fig.add_trace(go.Scatter(
    x=Plot_DF.index
    ,y=Plot_DF["MACD_Signal"].values
    ,name="MACD_Signal"
    ,mode="lines"
    ,line=dict(color='#2ca02c')
), row=3, col=1
)


fig.update_layout(
    title=f"{name_col} MACD & MACD Signal"
    ,width=1000
    ,height=750
    ,autosize=False
)

fig.show();

##### Price history / MACD #####
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.2)

fig.add_trace(go.Scatter(
    x=Plot_DF.index
    ,y=Plot_DF[name_col].values
    ,name=name_col
    ,mode="lines"
    ,line=dict(color="#1f77b4")
), row=1, col=1)

fig.add_trace(go.Scatter(
    x=Plot_DF.index
    ,y=Plot_DF["MACD"].values
    ,name=f"{name_col} MACD"
    ,mode="lines"
    ,line=dict(color="#ff7f0e")
), row=2, col=1)

fig.update_layout(
    title=f"{name_col} MACD"
)

fig.show();

##### Long Profit X Strat Profit #####
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=Plot_DF.index
    ,y=Plot_DF['Profit'].values
    ,name="Long Return"
    ,mode="lines"
    ,line=dict(color="#1f77b4")
))

fig.add_trace(go.Scatter(
    x=Plot_DF.index
    ,y=Plot_DF['Strat_Profit'].values
    ,name="Strat Return"
    ,mode="lines"
    ,line=dict(color="#d62728")
))

fig.update_layout(
    title=f"{name_col} Long Return X MACD Signal"
)

fig.show();