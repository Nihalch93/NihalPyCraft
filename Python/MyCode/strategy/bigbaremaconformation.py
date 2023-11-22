"""
Module tracks big bar candle in 15 mins with conformation from 200 ema in 5 mins candle
"""

def bigbaremaconformation(NiftyStocks,):
    
for symbol in NiftyStocks:
    data_15min = {
        "symbol":f"NSE:{symbol}-EQ",
        "resolution":"15",
        "date_format":"1",
        "range_from":f"{range_from}",
        "range_to":f"{range_to}",
        "cont_flag":"1"
    }
    try:
        response_15min = fyers.history(data=data_15min)
        exit()
        df_15min= pd.DataFrame(response_15min["candles"], columns=['date','open','high','low','close','volume'])
        df_15min['date'] =df_15min['date']+19800 
        df_15min['date'] = pd.to_datetime(df_15min['date'], unit='s')
        df_15min['ema9'] = talib.EMA(df_15min["close"], timeperiod=9)
        df_15min = sql(f"select *,  row_number() over (partition by substr(date,1,10) order by date) as candle_num from df_15min")
            
        bigbardf = pd.concat([bigbardf,sql(f"""select '{symbol}' as symbol,date,candle_num from df_15min where substr(date,1,10)='{todaysDate}'
                and abs(open-close)>low*0.007 and abs(open-close)<low*0.015 and candle_num<=22""")])
    except Exception as e:
        print(f"ERROR:::  Skipped {symbol} error message ***{e}*** in api response :: ''''''''''''''''''''''{response_15min}''''''''''''''''''''''")

        
print(bigbardf)
print("next*********************")


for index, row in bigbardf.iterrows():
    symbol = row["symbol"]
    date = row["date"]
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
                
                print(f"{symbol} has a BULLISH sentiment with big bar at time :: {date}")
        if sql(f"select count(*) from df_5min where substr(date,1,10)='{yesterdays_date}' and high>=ema200").values[0] == 0:
            if sql(f"select count(*) from (select avg(ema200-high) as highema,avg(ema200)*0.0004 emapercent from df_5min where substr(date,1,10)='{yesterdays_date}') where highema>emapercent").values[0] == 1:
                print(f"{symbol} has a BEARISH sentiment with big bar at time :: {date}")
    except Exception as e:
        print(f"ERROR:::  Skipped {symbol} error message ***{e}*** in api response :: ''''''''''''''''''''''{response_5min}''''''''''''''''''''''")
        break

