from API_BBG import API_BBG
from SQL_Server_Connection import SQL_Server_Connection

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from datetime import date

API_BBG = API_BBG()
PM_Connection = SQL_Server_Connection(database='PM')

# Variáveis/Objetos locais
query = f"""
SELECT 
	Date
    ,RiskFactor.Name
	,Value 
FROM 
	IndexesValue 
LEFT JOIN RiskFactor ON RiskFactor.Id=IndexesValue.Id_RiskFactor
WHERE 
	Id_RiskFactor IN (734, 735, 89)
    AND Date>='20180101'
    AND Date NOT IN ('20180115', '20180219', '20180309', '20181005', '20181123', '20181231', '20190822', '20180627', '20180706', '20180716')
ORDER BY
	Date"""

PM_Connection = SQL_Server_Connection(database='PM')
Raw_Index = PM_Connection.getData(query=query, dtparse=['Date'])

Pivot_Data = Raw_Index.pivot_table(values=['Value'], columns=['Name'], index=['Date'])


# Function to genererate outstrech values
def Outstretched_Indicator(df, name_col, momentum_lookback=3, avg_lookback=3, n_points_chart=False, return_df=False):
    # DataFrame Manipular
    Raw_DF = pd.DataFrame(df['Value'][name_col]).dropna()

    Raw_DF[f'{momentum_lookback}D_Change'] = (Raw_DF - Raw_DF.shift(momentum_lookback))
    Raw_DF[f'{momentum_lookback}D_Change_Side'] = np.where(Raw_DF[f'{momentum_lookback}D_Change']>0, 1, -1)

    Raw_Outstretch = []
    
    # Loop to get oustretch
    for index, row in Raw_DF.iterrows():
        if Raw_DF.index.get_loc(index)<momentum_lookback:
            Raw_Outstretch.append(np.nan)
            
        else:
            # Positive Outstretch
            Pos_Out_DF = Raw_DF.loc[:index].loc[(Raw_DF[f'{momentum_lookback}D_Change'].notna()) & (Raw_DF[f'{momentum_lookback}D_Change_Side']==1)]
            Neg_Out_DF = Raw_DF.loc[:index].loc[(Raw_DF[f'{momentum_lookback}D_Change'].notna()) & (Raw_DF[f'{momentum_lookback}D_Change_Side']==-1)]

            # Check if has 3 Pos and 3 Neg Values
            if len(Pos_Out_DF)>=3 and len(Neg_Out_DF)>=3:
                Outstretch = Pos_Out_DF.tail(3)[f'{momentum_lookback}D_Change'].sum() + Neg_Out_DF.tail(3)[f'{momentum_lookback}D_Change'].sum()
            else:
                Outstretch = np.nan

            Raw_Outstretch.append(Outstretch)

    # Insert Outstrech Data into DataFrame
    Raw_DF['Raw_Outstretch'] = np.array(Raw_Outstretch)
    Raw_DF['Outstretch_Indicator'] = Raw_DF['Raw_Outstretch'].ewm(span=avg_lookback, adjust=False).mean()

    # Cria Chart
    plot_df = Raw_DF.copy()
    
    if type(n_points_chart)==int:
        plot_df = plot_df.iloc[n_points_chart:,:]

    fig, axs = plt.subplots(2, 1, figsize=(15, 15))
    axs[0].plot(plot_df.index, plot_df[name_col], 'tab:blue')
    axs[0].set_title(name_col)
    axs[0].grid()

    axs[1].plot(plot_df.index, plot_df[f'Outstretch_Indicator'], 'tab:red')
    axs[1].set_title(f'Outstretch_Indicator_{name_col}')
    axs[1].axhline(y=0, linewidth=2, color='black')
    axs[1].grid()
    plt.show;

    if return_df:
        return Raw_DF

SP_Outstretch = Outstretched_Indicator(df=Pivot_Data, name_col='S&P500', momentum_lookback=3, avg_lookback=3, return_df=True)
Bonds_Px = Outstretched_Indicator(df=Pivot_Data, name_col='Octante LATAM Bonds Price Index', momentum_lookback=3, avg_lookback=3, n_points_chart=-252, return_df=True)
Bonds_Z_Spread = Outstretched_Indicator(df=Pivot_Data, name_col='Octante LATAM Bonds Z-Spread Index', momentum_lookback=3, avg_lookback=3, n_points_chart=-252, return_df=True)

Outstretched_Indicator(df=Pivot_Data, name_col='Octante LATAM Bonds Price Index', momentum_lookback=3, avg_lookback=3, n_points_chart=-252)

Pivot_Data.head(15)

len(Pivot_Data.loc[:'2010-01-14'].loc[(Pivot_Data['3D_Change'].notna()) & (Pivot_Data['3D_Change_Side']==1)]) 

SP_Outstretch.to_excel('SP_Outstretch.xlsx')
Bonds_Px.to_excel('Bonds_Px_Outstretch.xlsx')
Bonds_Z_Spread.to_excel('Bonds_Z_Spread_Outstretch.xlsx')

import numpy as np
import matplotlib.pyplot as plt

xs = np.linspace(-np.pi, np.pi, 30)
ys = np.sin(xs)
markers_on = [12, 17, 18, 19]
plt.plot(xs, ys, '-gD', markevery=markers_on)
plt.show()