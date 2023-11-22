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
from utils.backtesting import *
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

minusdays =0#easygui.enterbox("Enter Timedelta *For current date enter 0====*")
current_date = datetime.datetime.now()- datetime.timedelta(days = int(minusdays))  #"2023-07-26 19:14:18.192989" type- datetime.datetime
#todaysDate = str(current_date.year)+str(current_date.month)+str(current_date.day)
todaysDate = (current_date - datetime.timedelta(days = 0)).isoformat()[0:10]
yesterdays_date = (current_date - datetime.timedelta(days = 1)).isoformat()[0:10]
range_from = (current_date - datetime.timedelta(days = 20)).isoformat()[0:10]
range_to= todaysDate
bigbardf = pd.DataFrame(columns = ['symbol', 'date', 'candle_num','sizefactor','ema9','open','close','high','low'])
print("current_date is ::"+str(current_date))
#print("todaysDate is ::"+todaysDate)
#print("yesterdays_date is ::"+yesterdays_date)
print("Procesing is happening from :: "+range_from+" to "+range_to)

NiftyStocks = pd.read_csv("https://archives.nseindia.com/content/indices/ind_nifty200list.csv")["Symbol"]

goodVolumeDF = pd.DataFrame(columns = ["symbol","latestVolume"])

for symbol in tqdm(NiftyStocks, desc="Fetching Data:::"):
    errorvar = ""
    data_1Day = {
        "symbol":f"NSE:{symbol}-EQ",
        "resolution":"1",
        "date_format":"1",
        "range_from":f"{range_from}",
        "range_to":f"{range_to}",
        "cont_flag":"1"
    }
    try:
        response_1Day = fyers.history(data=data_1Day)
        df_1Day= pd.DataFrame(response_1Day["candles"], columns=['date','open','high','low','close','volume'])
        #add live data will be one min greator than latest candle
        #df_15min = pd.concat([df_15min,sql(f"""select date+60 as date,close as open, 0 as high, 0 as low,{getCurrentPrice(fyers,symbol)} as close, 0 as volume  from df_15min where date = (select max(date) from df_15min)""")])
        df_1Day['date'] =df_1Day['date']+19800 
        df_1Day['date'] = pd.to_datetime(df_1Day['date'], unit='s')
        df_1Day = sql("""select date,sum(volume) as volume from (select volume,substr(date,1,10) as date from df_1Day) group by date""")
        df_1Day['VolSma10inc'] = (talib.SMA(df_1Day["volume"], timeperiod=10))*1.3
        df_1Day['voldiffpercentage'] = round((df_1Day['volume']/df_1Day['VolSma10inc']),2)
        df_1Day = sql("""select *,row_number() over (order by date desc) as candle_num from df_1Day""")

        latestVolume = sql("""select voldiffpercentage from df_1Day where candle_num = 1""").values[0][0]

        if sql("""select count(*) from df_1Day where candle_num=1 and volume>=VolSma10inc""").values[0][0]>0:
            data = [[symbol,latestVolume]]
            goodVolumeDF = pd.concat([goodVolumeDF,pd.DataFrame(data, columns=["symbol","latestVolume"])])
    except Exception as e:  
        errorvar=errorvar+f"ERROR:::  Skipped {symbol} error message ***{e}*** in api response\n"


print(errorvar)
print(goodVolumeDF.sort_values(by=['latestVolume'], ascending=False).to_string())

