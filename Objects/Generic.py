from Objects.API_BBG import API_BBG
from Objects.SQL_Server_Connection import SQL_Server_Connection

class Generic():
    def __init__(self):
        super().__init__()

        self.API_BBG = API_BBG()
        self.AP_Connection = SQL_Server_Connection(database='Asset_Pricing')