import pandas as pd
import numpy as np

import yfinance as yf

from datetime import date

from Backend.yFinance_Wrapper import yFinance_Wrapper

yFinance_Wrapper = yFinance_Wrapper()
Ibov_Price_Data = yFinance_Wrapper.getIbovEquitiesLastUpdate()

print(Ibov_Price_Data)

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

pd.set_option('display.max_rows', len(Ibov_Price_Data))
Ibov_Price_Data.style.bar(subset=['DTD_Change', 'MTD_Change', 'YTD_Change', '12M_Change'], align='mid', color=['darkred', 'darkgreen']).applymap(color_negative_red, subset=['1D_Delta'])
Ibov_Price_Data
pd.reset_option('display.max_rows')