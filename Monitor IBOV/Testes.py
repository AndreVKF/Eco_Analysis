import pandas as pd
import numpy as np

import yfinance as yf

from datetime import date

from Backend.yFinance_Wrapper import yFinance_Wrapper

yFinance_Wrapper = yFinance_Wrapper()
Ibov_Price_Data = yFinance_Wrapper.getIbovEquitiesLastUpdate()

pd.set_option('display.max_rows', len(Ibov_Price_Data))
Ibov_Price_Data.style.bar(subset=['DTD_Change', 'MTD_Change', 'YTD_Change', '12M_Change'], align='mid', color=['darkred', 'darkgreen']).applymap(yFinance_Wrapper.color_negative_red, subset=['1D_Delta'])
Ibov_Price_Data
pd.reset_option('display.max_rows')