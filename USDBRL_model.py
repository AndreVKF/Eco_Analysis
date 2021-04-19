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
import seaborn as sns

import pandas as pd
import numpy as np

from datetime import datetime

####### Get data #######
API_BBG = API_BBG()

tickers = ['USDBRL Curncy'
    ,'GD1 Curncy'
    ,'OD1 Comdty'
    ,'OD5 Comdty'
    ,'OD10 Comdty'
    ,'OD15 Comdty'
    ,'DXY Curncy'
    ,'IBOV Index'
    ,'CBRZ1U5 CBIN Curncy' # CDS BZ 5Y
    ,'SPX Index']
fields = ['PX_LAST']
startDate = 20100101
endDate = int(datetime.today().strftime('%Y%m%d'))

Raw_Data = API_BBG.BBG_POST(bbg_request='BDH'
    ,tickers=tickers
    ,fields=fields
    ,date_start=startDate
    ,date_end=endDate)

# Pivot Table with Refdate as Index
Pivot_Data = pd.pivot_table(Raw_Data, values='PX_LAST', index='Refdate', columns='Ticker')
Pivot_Data.dropna(inplace=True)

# Data Heatmap
sns.heatmap(pd.pivot_table(Raw_Data, values='PX_LAST', index='Refdate', columns='Ticker').isna(), cmap='inferno')

Pivot_Data = Pivot_Data[tickers]

# Clear outliers
Dt_Remove = ['2011-04-27'
    ,'2020-03-25'
    ,'2020-03-26'
    ,'2020-03-27']
Pivot_Data = Pivot_Data.loc[~Pivot_Data.index.isin(Dt_Remove)]

# Correlation heatmap
Pivot_Data.corr()

# DataFrame to np.values
y = Pivot_Data.iloc[:, 0:1].values
x = Pivot_Data.iloc[:, 1:].values

# Split
x_treinamento, x_teste, y_treinamento, y_teste = train_test_split(x
    ,y
    ,test_size=0.2
    ,random_state=0)

######################## Escalonamento Dados ########################
scaler_x = StandardScaler()
x_scaled = scaler_x.fit_transform(x)

scaler_y = StandardScaler()
y_scaled = scaler_y.fit_transform(y)

# Split
x_sc_treinamento, x_sc_teste, y_sc_treinamento, y_sc_teste = train_test_split(x_scaled
    ,y_scaled
    ,test_size=0.5
    ,random_state=101)

######################## SVR ########################
regressor_SVM = SVR(kernel='rbf', C=100)
regressor_SVM.fit(x_treinamento, y_treinamento)

regressor_SVM.score(x_treinamento, y_treinamento)
regressor_SVM.score(x_teste, y_teste)

previsao = regressor_SVM.predict(x_teste)

n_toPlot = -365

plt.scatter(Pivot_Data.index[n_toPlot:], Pivot_Data['USDBRL Curncy'].values[n_toPlot:], s=5, c="b", label="USDBRL Curncy")
plt.plot(Pivot_Data.index[n_toPlot:], regressor_SVM.predict(x)[n_toPlot:], c="r", label="Estimado")
plt.legend(loc='best')
plt.show()

######################## SVR Scaled Data ########################
SVM_Data = Pivot_Data

regressor_SVM = SVR(kernel='rbf')
regressor_SVM.fit(x_sc_treinamento, y_sc_treinamento)

SVM_Data['Prediction'] = scaler_y.inverse_transform(regressor_SVM.predict(x_scaled))

regressor_SVM.score(x_sc_treinamento, y_sc_treinamento)
regressor_SVM.score(x_sc_teste, y_sc_teste)

previsao = scaler_y.inverse_transform(regressor_SVM.predict(x_sc_teste)) 

n_toPlot = -400

plt.figure(figsize=(16, 6))
plt.scatter(Pivot_Data.index[n_toPlot:], Pivot_Data['USDBRL Curncy'].values[n_toPlot:], s=5, c="b", label="USDBRL Curncy")
plt.plot(Pivot_Data.index[n_toPlot:], scaler_y.inverse_transform(regressor_SVM.predict(x_scaled))[n_toPlot:], c="r", label="Estimado")
plt.legend(loc='best')
plt.show()

######################## NN Scaled ########################
regressor_NN = MLPRegressor(verbose=True
    ,activation='relu'
    ,hidden_layer_sizes=(5, 5))

regressor_NN.fit(x_sc_treinamento, y_sc_treinamento)

regressor_NN.score(x_sc_treinamento, y_sc_treinamento)
regressor_NN.score(x_sc_teste, y_sc_teste)

n_toPlot = -400

plt.figure(figsize=(16, 6))
plt.scatter(Pivot_Data.index[n_toPlot:], Pivot_Data['USDBRL Curncy'].values[n_toPlot:], s=5, c="b", label="USDBRL Curncy")
plt.plot(Pivot_Data.index[n_toPlot:], scaler_y.inverse_transform(regressor_NN.predict(x_scaled))[n_toPlot:], c="r", label="Estimado")
plt.legend(loc='best')
plt.show()

######################## Tests ########################
Test_DF = SVM_Data.loc[(SVM_Data.index>'2011-01-01') & (SVM_Data.index<'2012-01-01')]
Test_DF.loc[(Test_DF['Prediction']==Test_DF['Prediction'].max())]
