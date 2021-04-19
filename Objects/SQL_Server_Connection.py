# coding=utf-8
import pyodbc
import sqlalchemy
import pandas as pd
import datetime as dt
import numpy as np


class SQL_Server_Connection():

    # Inicialização
    def __init__(self, database):

        # SQL Server Connection
        self.connStr = "DRIVER={SQL SERVER};server=osaot001\\octsqlexpress;database=%s;uid=sa;pwd=octante01;Trusted_Connection" % database
        self.connSqlAlchemy = 'mssql+pyodbc://sa:octante01@osaot001\octsqlexpress/%s?driver=SQL+Server+Native+Client+11.0' % database

        # Inicia Conexão
        try:
            self.conn = pyodbc.connect(self.connStr, autocommit=True)
            print("Connection with pyodbc to SQL Server successuful: %s." % database)
            self.connSqlAlchemy = sqlalchemy.create_engine(self.connSqlAlchemy)
            print("Connection with sqlalchemy to SQL Server successuful: %s." % database)
        except:
            print("Connection to SQL Server failed.")

    # Retrieve Data and return as Data Frame
    def getData(self, query, dtparse=None):
        # Query from DB
        df = pd.read_sql(query, self.conn, parse_dates=dtparse)

        return df

    # Query para append DataFrames ao BD
    def insertDataFrame(self, tableDB, df):
        if not df.empty:
            try:
                df.to_sql(name=tableDB, con=self.connSqlAlchemy, if_exists='append', index=False)
                print('Successuful appended DataFrame to Table %s !' % tableDB)
            except:
                print('Error in appending DataFrame to Table %s.' % tableDB)
        else:
            print('Empty DataFrame. Not appended to Table %s.' % tableDB)

    # Execute Query
    def execQuery(self, query):
        engine = self.conn
        cursor = engine.cursor()

        try:
            cursor.execute(query)
            return True
        except:
            print("Error while executing query %s." % query)
            raise
            return False

     # Return Value
    def getValue(self, query, vlType="str"):
        # Query from Database
        vl = pd.read_sql(query, self.conn)

        # Types
        # 1 => int
        # 2 => float
        # 3 => datetime
        # 4 => str

        # Case value type
        try:
            if vlType == "int":
                ret = int(vl.iloc[0, 0])
                return ret

            elif vlType == "float":
                ret = float(vl.iloc[0, 0])
                return ret

            elif vlType == "datetime":
                ret = str(vl.iloc[0, 0])
                ret = dt.datetime.strptime(ret, "%Y-%m-%d")
                return ret

            elif vlType == "str":
                ret = str(vl.iloc[0, 0])
                return ret
        except:
            return 0

    def __str__(self):
        return self.connStr

    # Close Connection
    def __exit__(self, *args):
        self.conn.close()
