from Objects.API_BBG import API_BBG
from Objects.SQL_Server_Connection import SQL_Server_Connection

from sklearn.svm import SVR
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.impute import KNNImputer

import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns

import pandas as pd
import numpy as np

from datetime import datetime

import sys
from Objects.Functions import Main

####### Get data #######
AP = Main()
API_BBG = API_BBG()

tickers = ['USDBRL Curncy'
    ,'GD1 Curncy'
    ,'OD1 Comdty'
    # ,'OD10 Comdty'
    # ,'OD15 Comdty'
    ,'DXY Curncy'
    ,'IBOV Index'
    ,'CBRZ1U5 CBIN Curncy' # CDS BZ 5Y
    ,'SPX Index']
fields = ['PX_LAST']
startDate = 20120101
endDate = int(datetime.today().strftime('%Y%m%d'))

Raw_Data = API_BBG.BBG_POST(bbg_request='BDH'
    ,tickers=tickers
    ,fields=fields
    ,date_start=startDate
    ,date_end=endDate)

Raw_Data['Refdate'] = pd.to_datetime(Raw_Data['Refdate'])

# Pivot Table with Refdate as Index
Pivot_Data = pd.pivot_table(Raw_Data, values='PX_LAST', index='Refdate', columns='Ticker')

# Add OD10Y Interpolated
def getOD10(row):
    base_date = int(row.name.strftime("%Y%m%d"))
    strBase_date = str(base_date)[0:4] + "-" + str(base_date)[4:6] + "-" + str(base_date)[6:8]
    try:
        return AP.InterpolationByValuationDate(base_date, 'BMF DI1 Future (OD)', int(AP.cal.offset(strBase_date, 252*10).strftime("%Y%m%d")))
        
    except:
        print(base_date, 'BMF DI1 Future (OD)', int(AP.cal.offset(strBase_date, 252*10).strftime("%Y%m%d")))
        return np.nan
    # print(int(row.name.strftime("%Y%m%d")), 'BMF DI1 Future (OD)', int(AP.cal.offset(row.name.strftime("%Y-%m-%d"), 252*10).strftime("%Y%m%d")))
    # AP.InterpolationByValuationDate(20190812, 'BMF DI1 Future (OD)', 20290821)
    # return AP.InterpolationByValuationDate(int(row.index.strftime("%Y%m%d")), 'BMF DI1 Future (OD)', int(AP.cal.offset('2021-03-11', 252*10).strftime("%Y%m%d")))

Pivot_Data['OD10Y'] = Pivot_Data.apply(getOD10, axis=1)

# Check na data
# sns.heatmap(pd.pivot_table(Raw_Data, values='PX_LAST', index='Refdate', columns='Ticker').isna(), cmap='inferno')
sns.heatmap(Pivot_Data.isna(), cmap='inferno')
####### Data Frame Adjustments #######
Pivot_Data.dropna(inplace=True)

# Change order
Columns = tickers
Columns.append('OD10Y')
Pivot_Data = Pivot_Data[tickers]

# Pivot_Data.drop(columns=['GD1 Curncy'], inplace=True)

# Clear outliers
Dt_Remove = ['2011-04-27'
    ,'2020-03-25'
    ,'2020-03-26'
    ,'2020-03-27'
    ,'2019-05-16'
    ,'2019-05-15'
    ,'2019-04-03'
    ,'2019-06-05']
Pivot_Data = Pivot_Data.loc[~Pivot_Data.index.isin(Dt_Remove)]

# Correlation map
Pivot_Data.corr()

# DataFrame to np.values
y = Pivot_Data.iloc[:, 0:1].values
x = Pivot_Data.iloc[:, 1:].values

######################## Split Dados Escalonados ########################
scaler_x = StandardScaler()
x_scaled = scaler_x.fit_transform(x)

scaler_y = StandardScaler()
y_scaled = scaler_y.fit_transform(y)

# Split
x_sc_treinamento, x_sc_teste, y_sc_treinamento, y_sc_teste = train_test_split(x_scaled
    ,y_scaled
    ,test_size=0.6
    ,random_state=101)

######################## Evaluate SVR Model ########################
geoSpace = np.geomspace(start=1e-3, stop=1e4, num=8)

################ Loop through Gamma/C ################
arrayResult = []

fig, axs = plt.subplots(len(geoSpace), len(geoSpace), figsize=(60, 46))

for index_i, i in enumerate(geoSpace, start=0):
    for index_j, j in enumerate(geoSpace, start=0):
        # Call Regressor
        regressor_SVM = SVR(kernel='rbf', C=i, gamma=j)
        regressor_SVM.fit(X=x_sc_treinamento, y=y_sc_treinamento)

        # Append Results
        arrayResult.append([i
            ,j
            ,regressor_SVM.score(x_sc_treinamento, y_sc_treinamento)
            ,regressor_SVM.score(x_sc_teste, y_sc_teste)
            ,regressor_SVM.score(x_scaled, y_scaled)])

        # axs[index_i, index_j].plot([1,2,3], [1,2,3])

        n_toPlot = -252
        # axs[index_i, index_j].text(0.5, 0.5, str((index_i, index_j)), fontsize=18, ha='center')
        axs[index_i, index_j].scatter(Pivot_Data.index[n_toPlot:], Pivot_Data['USDBRL Curncy'].values[n_toPlot:], s=5, c="b", label="USDBRL Curncy")
        axs[index_i, index_j].plot(Pivot_Data.index[n_toPlot:], scaler_y.inverse_transform(regressor_SVM.predict(x_scaled))[n_toPlot:], c="r", label="Estimado")
        axs[index_i, index_j].set_title(f'SVM USDBRL Model C={i} Gamma={j}')

fig.savefig("Tests_USDBRL_Fixed_C_Gamma.png")

# Array Results to DataFrame
Result_DF = pd.DataFrame(data=arrayResult, columns=['C', 'Gamma', 'Score_Treino', 'Score_Teste', 'Score_Tudo'])

Result_DF.sort_values(by='Score_Teste', ascending=False).head(10)
Result_DF.sort_values(by='Score_Tudo', ascending=False).head(10)


################ Loop only using C ################
fig, axs = plt.subplots(int(len(geoSpace)/2), 2, figsize=(40, 30))

for index, i in enumerate(geoSpace, start=0):
    regressor_SVM = SVR(kernel='rbf', C=i)
    regressor_SVM.fit(X=x_sc_treinamento, y=y_sc_treinamento)

    n_toPlot = -252
    # axs[index_i, index_j].text(0.5, 0.5, str((index_i, index_j)), fontsize=18, ha='center')
    # Gambiarra index
    if index<=3:
        index_i = index
        index_j = 0
    else:
        index_i = index-4
        index_j = 1

    # print(index_i, index_j)

    axs[index_i, index_j].scatter(Pivot_Data.index[n_toPlot:], Pivot_Data['USDBRL Curncy'].values[n_toPlot:], s=5, c="b", label="USDBRL Curncy")
    axs[index_i, index_j].plot(Pivot_Data.index[n_toPlot:], scaler_y.inverse_transform(regressor_SVM.predict(x_scaled))[n_toPlot:], c="r", label="Estimado")
    axs[index_i, index_j].set_title(f'SVM USDBRL Model C={i} Gamma=Default')


fig.savefig("Tests_USDBRL_Fixed_C_Default_Gamma.png")

######################## Model Testing ########################
# Model with default values (C=1, gamma=default)
md_1 = SVR(kernel='rbf')
md_1.fit(X=x_sc_treinamento, y=y_sc_treinamento)

prediction_array = scaler_y.inverse_transform(md_1.predict(x_scaled))

DF_1 = pd.DataFrame({
    "USDBRL": Pivot_Data['USDBRL Curncy'].values
    ,"Prediction": prediction_array
    }, 
    index=Pivot_Data.index)

figura = px.line(title = 'SVR RBF Model C=1.0 Gamma=Default')
for i in DF_1.columns:
    figura.add_scatter(x=DF_1.index, y=DF_1[i], name=i)
figura.show()

# Model with default values (C=0.05, gamma=default)
c = 0.05
md_2 = SVR(kernel='rbf', C=c)
md_2.fit(X=x_sc_treinamento, y=y_sc_treinamento)

prediction_array = scaler_y.inverse_transform(md_2.predict(x_scaled))

DF_2 = pd.DataFrame({
    "USDBRL": Pivot_Data['USDBRL Curncy'].values
    ,"Prediction": prediction_array
    }, 
    index=Pivot_Data.index)

DF_2['Avg_30D'] = DF_2['USDBRL'].rolling(window=30).mean()
DF_2['Std_30D'] = DF_2['USDBRL'].rolling(window=30).std()

# 2x Std Bandas
DF_2['Avg_30D_Upper_Band'] = DF_2['Avg_30D'] + 2*DF_2['Std_30D']
DF_2['Avg_30D_Lower_Band'] = DF_2['Avg_30D'] - 2*DF_2['Std_30D']

# Drop Std Column
DF_2.drop(columns=['Std_30D'], inplace=True)

figura = px.line(title = f'SVR RBF Model C={c} Gamma=Default')
figura.add_scatter(x=DF_2.index, y=DF_2['USDBRL'], name='USDBRL', mode='lines')
figura.add_scatter(x=DF_2.index, y=DF_2['Prediction'], name='Prediction', mode='lines')
figura.add_scatter(x=DF_2.index, y=DF_2['Avg_30D_Upper_Band'], name='Avg_30D_Upper_Band', line_color='#7f7f7f', line_dash="dash")
figura.add_scatter(x=DF_2.index, y=DF_2['Avg_30D_Lower_Band'], name='Avg_30D_Lower_Band', line_color='#7f7f7f', line_dash="dash")
# figura.add_scatter(x=DF_2.index, y=DF_2['Avg_30D'], name='Avg_30D', line_color="#bcbd22", line_dash="solid")
figura.show()

md_2.score(x_sc_teste, y_sc_teste)
