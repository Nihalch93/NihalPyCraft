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
from utils.notification import *


key = easygui.enterbox("Enter encryption key")
fernet = Fernet(key)
client_id = fernet.decrypt(b'gAAAAABkw-u26FsHgsMZPbjpKF5WwQVYIUYcyXnyGTJeflPGhe3dVyhXpuz2GbJsB3vZaIwCfAerEO_ZSRPsIdMHMsogq6z1pw==').decode()
secret_key = fernet.decrypt(b'gAAAAABkw-u2qoKRLDf6uzyuz1DyXsQWKmRxos1c66iGaCU3wm4XSPrMWNlbBP8ARE56kPgX5cXFLx-6oLE4oqPiPF07Egy9uQ==').decode()
redirect_uri = "https://www.google.com/"
response_type = "code"
state = "Login Successful"
grant_type = "authorization_code"
fyers = fyersModel.FyersModel(client_id=client_id, token=get_access_token(client_id,secret_key,redirect_uri,response_type,grant_type), log_path=f"MyCode/logs/")
while True:
    minusdays =14#easygui.enterbox("Enter Timedelta *For current date enter 0====*")
    current_date = datetime.datetime.now()- datetime.timedelta(days = int(minusdays))  #"2023-07-26 19:14:18.192989" type- datetime.datetime
    #todaysDate = str(current_date.year)+str(current_date.month)+str(current_date.day)
    todaysDate = (current_date - datetime.timedelta(days = 0)).isoformat()[0:10]
    yesterdays_date = (current_date - datetime.timedelta(days = 1)).isoformat()[0:10]
    range_from = (current_date - datetime.timedelta(days = 30)).isoformat()[0:10]
    range_to= todaysDate
    bigbardf = pd.DataFrame(columns = ['symbol', 'date', 'candle_num','sizefactor','ema9','open','close','high','low'])
    #print("todaysDate is ::"+todaysDate)
    #print("yesterdays_date is ::"+yesterdays_date)

    NiftyStocks = pd.read_csv("https://archives.nseindia.com/content/indices/ind_nifty200list.csv")["Symbol"]


    """
    symbol = "SBIN"
    buytime="2023-07-28 12:37:51"#2023-07-28 13:37:51.792564
    type_b_s = "b"
    target=617
    stoploss=400

    i=0
    while 1<2:
        i+=1
        print(str(getCurrentPrice(fyers,symbol))+"   ::" +str(i))
    buytime = datetime.datetime.strptime(buytime,"%Y-%m-%d %H:%M:%S")
    easygui.msgbox(backtesting(fyers,symbol,buytime=buytime,type_b_s=type_b_s ,target=target,stoploss=stoploss))

    consolidatedDf = fiveConsolidationCandle(fyers,NiftyStocks,range_to)
    print(consolidatedDf)
    exit()
    """
    #"symbol":f"NSE:NIFTYBANK-INDEX",NSE:NIFTY50-INDEX,NSE:{symbol}-EQ
    print(str(current_date))
    bigbardf = ""
    iter = 0
    while True:
        iter = iter+1
        time.sleep(5)
        symbol = "NIFTY"
        data_15min = {
            "symbol":f"NSE:NIFTY50-INDEX",
            "resolution":"5",
            "date_format":"1",
            "range_from":f"{range_from}",
            "range_to":f"{range_to}",
            "cont_flag":"1"
        }
        try:
            response_15min = fyers.history(data=data_15min)
            df_15min= pd.DataFrame(response_15min["candles"], columns=['date','open','high','low','close','volume'])
            #add live data will be one min greator than latest candle
            df_15min = pd.concat([df_15min,sql(f"""select date+60 as date,close as open, 0 as high, 0 as low,{getCurrentPrice(fyers,symbol)} as close, 0 as volume  from df_15min where date = (select max(date) from df_15min)""")])
            df_15min['date'] =df_15min['date']+19800 
            df_15min['date'] = pd.to_datetime(df_15min['date'], unit='s')
            df_15min['ema9'] = talib.EMA(df_15min["close"], timeperiod=9)
            df_15min['bodysize'] = (df_15min['open'] - df_15min['close']).abs()
            df_15min['bodysma'] = talib.SMA(df_15min["bodysize"], timeperiod=21)#21 body sma 

            df_15min = sql(f"""select *,  CASE WHEN bodysize>=bodysma*2 THEN 'YES' ELSE 'NO' END AS isbigbar, round(bodysize/bodysma,1) as sizefactor, 
                        row_number() over (partition by substr(date,1,10) order by date) as candle_num from df_15min""")
            '''bigbardf = pd.concat([bigbardf,sql(f"""select '{symbol}' as symbol,date,candle_num from df_15min where substr(date,1,10)='{todaysDate}'
                    and abs(open-close)>low*0.007 and abs(open-close)<low*0.015 and candle_num<=22""")])'''
            dfNewData = sql(f"""select '{symbol}' as symbol,date,candle_num,sizefactor,ema9,open,close,high,low from df_15min 
                                            where substr(date,1,10)='{todaysDate}' 
                                            and upper(isbigbar)='YES' and candle_num<=2200 and candle_num>1""").to_string()
            if dfNewData != bigbardf:
                print(dfNewData)
                bigbardf = dfNewData
                notification(f"""got a big bar
                             {dfNewData}""") 

        except Exception as e:
            print(f"ERROR:::  Skipped {symbol} error message ***{e}*** in api response")

exit()


for index, row in bigbardf.iterrows():
    symbol = row["symbol"]
    date = row["date"]
    sizefactor = row["sizefactor"]
    #print(f"Checking EMA validity for:: {symbol}")
    data_5min = {
        "symbol":f"NSE:{symbol}-EQ",
        "resolution":"5",
        "date_format":"1",
        "range_from":f"{range_from}",
        "range_to":f"{range_to}",
        "cont_flag":"1"
    }

    try:
        response_5min = fyers.history(data=data_5min)
        df_5min= pd.DataFrame(response_5min["candles"], columns=['date','open','high','low','close','volume'])
        df_5min['date'] =df_5min['date']+19800 
        df_5min['date'] = pd.to_datetime(df_5min['date'], unit='s')
        df_5min['ema200'] = talib.EMA(df_5min["close"], timeperiod=200)
        try:
            rating = tickerval[symbol]
        except:
            rating = "NA"
        if sql(f"select count(*) from df_5min where substr(date,1,10)='{yesterdays_date}' and low<=ema200").values[0] == 0:
            if sql(f"select count(*) from (select avg(low-ema200) as lowema,avg(ema200)*0.0004 emapercent from df_5min where substr(date,1,10)='{yesterdays_date}') where lowema>emapercent").values[0] == 1:   
                print(f"{symbol} has a BULLISH sentiment with big bar at time :: {date} Rating:: {rating} sizefactor:: {sizefactor}")
        if sql(f"select count(*) from df_5min where substr(date,1,10)='{yesterdays_date}' and high>=ema200").values[0] == 0:
            if sql(f"select count(*) from (select avg(ema200-high) as highema,avg(ema200)*0.0004 emapercent from df_5min where substr(date,1,10)='{yesterdays_date}') where highema>emapercent").values[0] == 1:
                print(f"{symbol} has a BEARISH sentiment with big bar at time :: {date} Rating:: {rating} sizefactor:: {sizefactor}")
    except Exception as e:
        print(f"ERROR:::  Skipped {symbol} error message ***{e}*** in api response :: ''''''''''''''''''''''{response_5min}''''''''''''''''''''''")
        break

