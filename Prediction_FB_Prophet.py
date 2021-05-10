import pandas as pd
import numpy as np
import math

import matplotlib.pyplot as plt

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

import yfinance as yf

from datetime import date

from fbprophet import Prophet

# Variáveis/Objetos locais
Today = date.today()

# Get Price Data
Price_Data = yf.download("SPY ^BVSP", start="2001-01-01", end=Today.strftime("%Y-%m-%d"))

Equity = "^BVSP"
data = pd.DataFrame(
    {"ds":Price_Data['Close'][Equity].index
    ,"y":Price_Data['Close'][Equity].values}
)

# Adjust model to parameters
m = Prophet(daily_seasonality = True) # the Prophet class (model)
m.fit(data) # fit the model using all data

# Specify the number of days in future to predict
future = m.make_future_dataframe(periods=365)

############# Plot Prediction #############
prediction = m.predict(future)
m.plot(prediction)
plt.title(f"Prediction Stock Price using the Prophet")
plt.xlabel("Date")
plt.ylabel(f"{Equity}")
plt.show()

############# Plot Components Trend #############
m.plot_components(prediction)
plt.show()