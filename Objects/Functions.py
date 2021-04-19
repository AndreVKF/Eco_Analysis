from Objects.Generic import Generic
from Objects.Queries import Queries

import pandas as pd
import numpy as np

from datetime import datetime
from bizdays import *
from dateutil.relativedelta import relativedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

class Main(Generic):
    ''' Constructor '''
    def __init__(self, Refdate=int(datetime.today().strftime("%Y%m%d"))):
        ''' Init Arguments '''
        Generic.__init__(self)
        pd.set_option('mode.chained_assignment', None)

        # Attributes
        self.Refdate = Refdate
        self.dtRefdate = pd.to_datetime(str(self.Refdate), format="%Y%m%d")
        self.Queries = Queries()
        
        self.Future_Months = Future_Months = {
            '1': 'F',
            '2': 'G',
            '3': 'H',
            '4': 'J',
            '5': 'K',
            '6': 'M',
            '7': 'N',
            '8': 'Q',
            '9': 'U',
            '10': 'V',
            '11': 'X',
            '12': 'Z'
            }
        
        # Create Calendar
        self.DF_Feriados_BRA = self.AP_Connection.getData(query = self.Queries.QFeriados_BRA())
        self.Create_Calendar()

        # DataFrames from DB
        self.DF_Currencies = self.AP_Connection.getData(query=self.Queries.currenciesDF())
        self.DF_Instruments = self.AP_Connection.getData(query=self.Queries.instrumentsDF())
        self.DF_Products = self.AP_Connection.getData(query=self.Queries.getProducts(), dtparse=['Expiration', 'Valuation', 'First_Trade_Date'])
        self.DF_Indexes = self.AP_Connection.getData(query=self.Queries.indexesDF())
        self.DF_ValueType = self.AP_Connection.getData(query=self.Queries.valueType())
           

    '''
    ##################################### CALC FUNCTIONS #####################################
    '''
    def InterpolationByDuration(self, Refdate, Instrument, InterpolaDuration):
        """
            Function to get interpolated value using duration
        """
        Instrument_Row = self.DF_Instruments.loc[self.DF_Instruments['Name']==Instrument]

        viewName = Instrument_Row['View_Name'].values[0]
        fieldValueName = self.DF_ValueType.loc[self.DF_ValueType['Id']==Instrument_Row['Id_ValueType'].values[0]]['Name'].values[0]
        Id_CalculationType = Instrument_Row['Id_CalculationType'].values[0]

        # Get view data
        View_DF = self.AP_Connection.getData(query=self.Queries.getViewTable(refdate=Refdate, viewName=viewName, fieldValueName=fieldValueName, duration=True, securityType='all'), dtparse=['Valuation']) 

        # Last/First Interpola Rows
        Last_Row = View_DF.iloc[-1, :]
        First_Row = View_DF.iloc[0, :]

        # ''' Caso ponto esteja a frente da curva '''
        if InterpolaDuration > Last_Row['Duration']:
            # Realiza regressão para estender a curva (4 grau)
            poly = PolynomialFeatures(degree=3)
            Duration_poly = poly.fit_transform(View_DF['Duration'].values.reshape(-1, 1))

            # Regressão linear
            regressor = LinearRegression()
            regressor.fit(Duration_poly, View_DF[fieldValueName])

            return regressor.predict(poly.fit_transform(np.array(InterpolaDuration).reshape(1, -1)))[0]

        # ''' Caso ponto esteja antes do inicio da curva '''
        elif InterpolaDuration < First_Row['Duration']:
            return None

        # ''' Interpolação baseada na não arbitração de pontos entre vencimentos de contratos '''
        else:
            End_Row = View_DF.loc[View_DF['Duration']>=InterpolaDuration].sort_values(by=['Duration'], ascending=True).iloc[0, :]
            Base_Row = View_DF.loc[View_DF['Duration']<=InterpolaDuration].sort_values(by=['Duration'], ascending=False).iloc[0, :]

            # Interpol Arguments
            Base_Dur = Base_Row['Duration']
            Base_Value = Base_Row[fieldValueName]

            End_Dur = End_Row['Duration']
            End_Value = End_Row[fieldValueName]

            # Interpolação no ponto
            if Base_Dur==End_Dur:
                return Base_Row[fieldValueName]

            else:

                return (End_Value - Base_Value) * (InterpolaDuration - Base_Dur) / (End_Dur - Base_Dur) + Base_Value


    def InterpolationByValuationDate(self, Refdate, Instrument, InterpolaDate):
        """
            Function to get interpolated value from Base_Valuation to End_Valuation
        """
        Instrument_Row = self.DF_Instruments.loc[self.DF_Instruments['Name']==Instrument]

        # Arguments
        strRefdate = str(Refdate)[0:4] + "-" + str(Refdate)[4:6] + "-" + str(Refdate)[6:8]
        dtRefdate = datetime.strptime(strRefdate, "%Y-%m-%d")
        
        strInterpolaDate = str(InterpolaDate)[0:4] + "-" + str(InterpolaDate)[4:6] + "-" + str(InterpolaDate)[6:8]
        dtInterpolaDate = datetime.strptime(strInterpolaDate, "%Y-%m-%d")
        
        viewName = Instrument_Row['View_Name'].values[0]
        fieldValueName = self.DF_ValueType.loc[self.DF_ValueType['Id']==Instrument_Row['Id_ValueType'].values[0]]['Name'].values[0]
        Id_CalculationType = Instrument_Row['Id_CalculationType'].values[0]

        # Get view data
        View_DF = self.AP_Connection.getData(query=self.Queries.getViewTable(refdate=Refdate, viewName=viewName, fieldValueName=fieldValueName, securityType='all'), dtparse=['Valuation']) 

        # Last Interpola Date
        Last_Row = View_DF.iloc[-1, :]
        First_Row = View_DF.iloc[0, :]

        # ''' Caso ponto esteja a frente da curva '''
        if dtInterpolaDate > Last_Row['Valuation']:
            # Realiza regressão para estender a curva (4 grau)
            NDays = (dtInterpolaDate - dtRefdate).days
            View_DF.loc[:, 'NumberDays'] =  (View_DF['Valuation'] - dtRefdate).dt.days

            poly = PolynomialFeatures(degree=3)
            NumberDays_poly = poly.fit_transform(View_DF['NumberDays'].values.reshape(-1, 1))

            # Regressão linear
            regressor = LinearRegression()
            regressor.fit(NumberDays_poly, View_DF[fieldValueName])

            return regressor.predict(poly.fit_transform(np.array(NDays).reshape(1, -1)))[0]

        # ''' Caso ponto esteja antes do inicio da curva '''
        elif dtInterpolaDate < First_Row['Valuation']:
            return None

        # ''' Interpolação baseada na não arbitração de pontos entre vencimentos de contratos '''
        else:
            End_Row = View_DF.loc[View_DF['Valuation']>=datetime.strptime(str(InterpolaDate), "%Y%m%d")].sort_values(by=['Valuation'], ascending=True).iloc[0, :]
            Base_Row = View_DF.loc[View_DF['Valuation']<=datetime.strptime(str(InterpolaDate), "%Y%m%d")].sort_values(by=['Valuation'], ascending=False).iloc[0, :]

            # Case interpolação no ponto
            if End_Row['Valuation'] == Base_Row['Valuation']:
                print(InterpolaDate)
                return Base_Row[fieldValueName]

            # Interpola (Valor interpolado = (Base_DU + Periodo de Interpolação))
            # BZ Compounding Workdays 252
            if Id_CalculationType==1:
                # Arguments
                Base_DU = self.cal.bizdays(strRefdate ,Base_Row['Valuation'].strftime("%Y-%m-%d"))
                Interpola_DU = self.cal.bizdays(strRefdate ,strInterpolaDate)
                End_DU = self.cal.bizdays(strRefdate ,End_Row['Valuation'].strftime("%Y-%m-%d"))

                Base_Diarizado = (1 + Base_Row[fieldValueName]/100) ** (Base_DU/252)
                End_Diarizado = (1 + End_Row[fieldValueName]/100) ** (End_DU/252)

                Interpolado_Periodo = (End_Diarizado/Base_Diarizado) ** ((Interpola_DU - Base_DU)/(End_DU - Base_DU))

                return (((Base_Diarizado*Interpolado_Periodo) ** (252/Interpola_DU))-1) * 100

            # Days 360
            elif Id_CalculationType==2:
                # Arguments
                Base_D360 = self.days360(dtRefdate, Base_Row['Valuation'])
                Interpola_D360 = self.days360(dtRefdate, dtInterpolaDate)
                End_D360 = self.days360(dtRefdate, End_Row['Valuation'])

                Base_Diarizado = (Base_Row[fieldValueName]/100) * Base_D360/360
                End_Diarizado = (End_Row[fieldValueName]/100) * End_D360/360

                Interpolado_Periodo = (End_Diarizado - Base_Diarizado) * ((Interpola_D360 - Base_D360) / (End_D360 - Base_D360))

                # Valor Interpolado
                return ((Base_Diarizado + Interpolado_Periodo) * (360/Interpola_D360 )) * 100


    '''
    ##################################### AUXILIAR FUNCTIONS #####################################
    '''
    def Create_Calendar(self):
        """
            Function to create self.calendar base
        """
        self.DF_Feriados_BRA['Data'].to_csv('Objects\Holidays.csv', header=False, index=None)
        self.holidays = load_holidays('Objects\Holidays.csv')

        self.cal = Calendar(self.holidays, ['Sunday', 'Saturday'], name='Brazil')

    def days360(self, start_date, end_date, method_eu=False):
        '''
            Function to calculate diff with days 360
        '''
        start_day = start_date.day
        start_month = start_date.month
        start_year = start_date.year
        end_day = end_date.day
        end_month = end_date.month
        end_year = end_date.year

        if (
            start_day == 31 or
            (
                method_eu is False and
                start_month == 2 and (
                    start_day == 29 or (
                        start_day == 28 and
                        start_date.is_leap_year is False
                    )
                )
            )
        ):
            start_day = 30

        if end_day == 31:
            if method_eu is False and start_day != 30:
                end_day = 1

                if end_month == 12:
                    end_year += 1
                    end_month = 1
                else:
                    end_month += 1
            else:
                end_day = 30

        return (
            end_day + end_month * 30 + end_year * 360 -
            start_day - start_month * 30 - start_year * 360)