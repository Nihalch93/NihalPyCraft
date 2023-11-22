import pandas as pd
from utils.getCurrentPrice import *
from pandasql import sqldf as sql
from tqdm import tqdm


def fiveConsolidationCandle(fyers,NiftyStocks,range_to):
    errorvar = ""
    consolidatedDf = pd.DataFrame(columns = ['symbol', 'percent'])
    for symbol in tqdm(NiftyStocks, desc="Fetching Data:::"):
        data_15min = {
            "symbol":f"NSE:{symbol}-EQ",
            "resolution":"15",
            "date_format":"1",
            "range_from":f"{range_to}",
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
            df_15min = sql(f"""select *, row_number() over (order by date) as candle_num from df_15min""")
            firstHigh = sql("""select high from df_15min where candle_num = 1""").values[0][0]
            firstLow = sql("""select low from df_15min where candle_num = 1""").values[0][0]
            if sql(f"""select count(*) from df_15min where high<={firstHigh} and low>={firstLow} and candle_num<=6""").values[0][0]>5:
                percentconsoliation = round((firstHigh-firstLow)*100/firstLow,2)
                data = [[symbol,percentconsoliation]]
                consolidatedDf = pd.concat([consolidatedDf,pd.DataFrame(data, columns=["symbol","percent"])])
        except Exception as e:
            errorvar=errorvar+f"ERROR:::  Skipped {symbol} error message ***{e}*** in api response\n"
    print(errorvar)
    return consolidatedDf.sort_values(by=['percent'])