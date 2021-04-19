from API_BBG import API_BBG
from SQL_Server_Connection import SQL_Server_Connection

import pandas as pd

import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns

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

# fig = px.line(Octante_Bonds_Px_Index, x=Octante_Bonds_Px_Index.index, y='Value')
# fig.show();

Octante_Bonds_Px_Index = pd.DataFrame(Pivot_Data['Value']['Octante LATAM Bonds Price Index']).dropna()
Octante_Bonds_Spread_Index = pd.DataFrame(Pivot_Data['Value']['Octante LATAM Bonds Z-Spread Index']).dropna()
SP_Index = pd.DataFrame(Pivot_Data['Value']['S&P500']).dropna()

################### Price Analysis ###################
# Add SMA to DF
Short_SMA = 22
Octante_Bonds_Px_Index[f'SMA_{Short_SMA}'] = Octante_Bonds_Px_Index['Octante LATAM Bonds Price Index'].rolling(Short_SMA).mean()

Long_SMA = 66
Octante_Bonds_Px_Index[f'SMA_{Long_SMA}'] = Octante_Bonds_Px_Index['Octante LATAM Bonds Price Index'].rolling(Long_SMA).mean()

# Gráfico de Média Móveis
fig = go.Figure()
fig.add_trace(go.Scatter(x=Octante_Bonds_Px_Index.index, y=Octante_Bonds_Px_Index['Octante LATAM Bonds Price Index'], mode='lines', name='Px'))
fig.add_trace(go.Scatter(x=Octante_Bonds_Px_Index.index, y=Octante_Bonds_Px_Index[f'SMA_{Short_SMA}'], mode='lines', name=f'SMA_{Short_SMA}', line=dict(dash='dash')))
fig.add_trace(go.Scatter(x=Octante_Bonds_Px_Index.index, y=Octante_Bonds_Px_Index[f'SMA_{Long_SMA}'], mode='lines', name=f'SMA_{Long_SMA}', line=dict(dash='dash')))
fig.show()

################### Steepness Indicator ###################
def SteepIndicator_pd(df, col_name, steep_SMA=22, steep_period=3, n_points_chart=False, return_df=False):
    raw = pd.DataFrame(df['Value'][col_name]).dropna()

    # Cria DataFrame com Slope
    raw[f'SMA_{steep_SMA}'] = raw[col_name].rolling(steep_SMA).mean()
    raw[f'Slope_{steep_period}'] = (raw[f'SMA_{steep_SMA}'] - raw[f'SMA_{steep_SMA}'].shift(steep_period))/steep_period

    # Cria Chart
    plot_df = raw.copy()
    
    if type(n_points_chart)==int:
        plot_df = plot_df.iloc[n_points_chart:,:]

    fig, axs = plt.subplots(2, 1, figsize=(15, 15))
    axs[0].plot(plot_df.index, plot_df[f'SMA_{steep_SMA}'], 'tab:blue')
    axs[0].set_title(f'SMA_{col_name}_{steep_SMA}')
    axs[0].grid()

    axs[1].plot(plot_df.index, plot_df[f'Slope_{steep_period}'], 'tab:red')
    axs[1].set_title(f'Steepness Indicator({col_name}, {steep_SMA}, {steep_period})')
    axs[1].axhline(y=0, linewidth=2, color='black')
    axs[1].grid()
    plt.show;

    # Return DataFrame
    if return_df:
        return raw


steep_SMA = 8
steep_period=3

LATAM_Bonds_Px_Steep = SteepIndicator_pd(df=Pivot_Data, col_name='Octante LATAM Bonds Price Index', steep_SMA=steep_SMA, steep_period=steep_period, n_points_chart=-252, return_df=True)
LATAM_Bonds_Spread_Steep = SteepIndicator_pd(df=Pivot_Data, col_name='Octante LATAM Bonds Z-Spread Index', steep_SMA=steep_SMA, steep_period=steep_period, n_points_chart=-252, return_df=True)
SP_Steep = SteepIndicator_pd(df=Pivot_Data, col_name='S&P500', steep_SMA=steep_SMA, steep_period=steep_period, n_points_chart=-252, return_df=True)

SP_Steep.to_excel("SP_Steep_Indicator.xlsx")
LATAM_Bonds_Px_Steep.to_excel("LATAM_Bonds_Px_Steep.xlsx")
LATAM_Bonds_Spread_Steep.to_excel("LATAM_Bonds_Spread_Steep.xlsx")