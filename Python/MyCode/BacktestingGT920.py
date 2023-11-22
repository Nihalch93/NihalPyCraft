import datetime
import os
from fyers_api import fyersModel
import pandas as pd
from pandasql import sqldf as sql
import talib
import easygui
from cryptography.fernet import Fernet
from utils.getFundamentalInfo import *
from utils.get_access_token import *
from utils.getCurrentPrice import *
from utils.backtestingforGT import *
from utils.fiveConsolidationCandle import *

key = easygui.enterbox("Enter encryption key")
fernet = Fernet(key)
client_id = fernet.decrypt(b'gAAAAABkw-u26FsHgsMZPbjpKF5WwQVYIUYcyXnyGTJeflPGhe3dVyhXpuz2GbJsB3vZaIwCfAerEO_ZSRPsIdMHMsogq6z1pw==').decode()
secret_key = fernet.decrypt(b'gAAAAABkw-u2qoKRLDf6uzyuz1DyXsQWKmRxos1c66iGaCU3wm4XSPrMWNlbBP8ARE56kPgX5cXFLx-6oLE4oqPiPF07Egy9uQ==').decode()
redirect_uri = "https://www.google.com/"
response_type = "code"
state = "Login Successful"
grant_type = "authorization_code"
fyers = fyersModel.FyersModel(client_id=client_id, token=get_access_token(client_id,secret_key,redirect_uri,response_type,grant_type), log_path=f"MyCode/logs/")
file1 = open("myfile.txt", "w")
for minusdays in range(0,365):
    try:
        file1.write("\n")
        file1.write("\n")

        #easygui.enterbox("Enter Timedelta *For current date enter 0====*")
        current_date = datetime.datetime.now()- datetime.timedelta(days = int(minusdays))  #"2023-07-26 19:14:18.192989" type- datetime.datetime
        #todaysDate = str(current_date.year)+str(current_date.month)+str(current_date.day)
        todaysDate = (current_date - datetime.timedelta(days = 0)).isoformat()[0:10]
        
        range_from = (current_date - datetime.timedelta(days = 30)).isoformat()[0:10]
        range_to= todaysDate
        file1.write("current_date is ::"+str(current_date))
        file1.write("\n")
        try:
            yesterdays_date = (current_date - datetime.timedelta(days = 1)).isoformat()[0:10]
            lastdaydata = {
                    "symbol":f"NSE:NIFTYBANK-INDEX",
                    "resolution":"5",
                    "date_format":"1",
                    "range_from":f"{yesterdays_date}",
                    "range_to":f"{yesterdays_date}",
                    "cont_flag":"1"
            }
            lastdayclose = fyers.history(data=lastdaydata)
            df_forclose= pd.DataFrame(lastdayclose["candles"], columns=['date','open','high','low','close','volume'])
            yesterdayclose = sql("""select close from df_forclose order by date desc limit 1""").values[0][0]
        except:
            yesterdays_date = (current_date - datetime.timedelta(days = 3)).isoformat()[0:10]
            print(yesterdays_date)

            lastdaydata = {
                    "symbol":f"NSE:NIFTYBANK-INDEX",
                    "resolution":"5",
                    "date_format":"1",
                    "range_from":f"{yesterdays_date}",
                    "range_to":f"{yesterdays_date}",
                    "cont_flag":"1"
            }
            print(lastdayclose)
            lastdayclose = fyers.history(data=lastdaydata)
            df_forclose= pd.DataFrame(lastdayclose["candles"], columns=['date','open','high','low','close','volume'])
            yesterdayclose = sql("""select close from df_forclose order by date desc limit 1""").values[0][0]


        data_5min = {
                "symbol":f"NSE:NIFTYBANK-INDEX",
                "resolution":"5",
                "date_format":"1",
                "range_from":f"{range_to}",
                "range_to":f"{range_to}",
                "cont_flag":"1"
        }

        try:
            response_5min = fyers.history(data=data_5min)
            df_5min= pd.DataFrame(response_5min["candles"], columns=['date','open','high','low','close','volume'])
            df_5min['date'] =df_5min['date']+19800 
            df_5min['date'] = pd.to_datetime(df_5min['date'], unit='s')
            df_5min = sql(f"""select * from (select *, row_number() over (partition by substr(date,1,10) order by date) as candle_num from df_5min) where candle_num<=7""")

            firstHigh = sql("""select high from df_5min where candle_num = 1""").values[0][0]
            firstLow = sql("""select low from df_5min where candle_num = 1""").values[0][0]
            triggerList = sql(f"""select * from df_5min where high>{firstHigh} or low<{firstLow} order by candle_num limit 1""")
            triggerhigh = triggerList.values[0][2]
            triggerlow = triggerList.values[0][3]
            candle_num = triggerList.values[0][6]
            todaysopen = sql("""select open from df_5min order by date limit 1""").values[0][0]
            if abs(todaysopen-yesterdayclose)<250:
                if triggerhigh > firstHigh:
                    if abs(triggerhigh - round(triggerhigh,-3)) >33:
                        date = datetime.datetime.strptime(str(triggerList.values[0][0])[0:19],"%Y-%m-%d %H:%M:%S")
                        type_b_s = "b"
                        target=firstHigh+(firstHigh-firstLow)
                        stoploss = firstLow
                        file1.write(f"buy order with target:: {target} on candle {candle_num} result:: "+backtestingforGT(fyers,buytime=date,type_b_s=type_b_s ,target=target,stoploss=stoploss))

                elif triggerlow < firstLow:
                    if abs(triggerlow - round(triggerlow,-3)) >33:
                        date = datetime.datetime.strptime(str(triggerList.values[0][0])[0:19],"%Y-%m-%d %H:%M:%S")
                        target=firstLow-(firstHigh-firstLow)
                        stoploss = firstHigh
                        type_b_s = "s"
                        file1.write(f"sell order with target:: {target} on candle {candle_num} result:: "+backtestingforGT(fyers,buytime=date,type_b_s=type_b_s ,target=target,stoploss=stoploss))
            else:
                print("No order")


        except Exception as e:
            print(f"ERROR:::  {e}")
    except:
        continue
            