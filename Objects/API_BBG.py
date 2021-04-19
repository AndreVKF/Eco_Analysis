import requests
import json
import pandas as pd
from pandas.io.json import json_normalize


# Function para realizar pedidos de post da API BBG
# BBG_Request = ["BDP", "BDH"]
# Ticker = List<Tickers>
# Fields = Field
# Return Data Frame with request

class API_BBG():

    def BBG_POST(self, bbg_request, tickers, fields, date_start=None, date_end=None, overrides=None):

        # Variaveis BDP ou BDH
        if bbg_request == "BDP":
            url = "http://10.1.1.31:8099/App_BBG_Request/BDP/"
            data_post = {
                "tickers": tickers,
                "fields": fields,
                "overrides": overrides
            }

            # Make Requests
            r = requests.post(url=url, data=json.dumps(data_post))

            return pd.read_json(r.json(), orient='index')

        elif bbg_request == "BDH":
            url = "http://10.1.1.31:8099/App_BBG_Request/BDH/"
            data_post = {
                "tickers": tickers,
                "fields": fields,
                "date_start": date_start,
                "date_end": date_end,
                "overrides": overrides
            }

            # Make Requests
            r = requests.post(url=url, data=json.dumps(data_post))

            # Empty dataframe
            newDF = pd.DataFrame()
            # Serializa response
            data = eval(r.json())

            for key in data:
                df = pd.read_json(data[key], orient='index')
                df['Ticker'] = key
                df = df.reset_index()
                df.rename(columns={'index': 'Refdate'}, inplace=True)

                newDF = newDF.append(df, ignore_index=True, sort=True)

            """
            for key in data:
                df = pd.read_json(data[key], orient='index')
                df['Ticker'] = key

                df = df.set_index(keys=['Ticker'], drop=True)
                del df.index.name

                newDF = newDF.append(df, ignore_index=False, sort=True)"""

            return newDF