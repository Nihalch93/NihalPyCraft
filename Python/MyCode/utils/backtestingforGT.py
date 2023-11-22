import pandas as pd
from pandasql import sqldf as sql
import datetime
from pandasql import sqldf as sql
import time


def backtestingforGT(fyers,buytime,type_b_s,target,stoploss):
    p='%Y-%m-%d %H:%M:%S' 
    epochbytime = int(time.mktime(time.strptime(str(buytime)[0:19],p)))+19740#ideally should be 19800 but that was filtering the candle on which buy order was placed 
    data_1min = {
        "symbol":f"NSE:NIFTYBANK-INDEX",
        "resolution":"1",
        "date_format":"1",
        "range_from":f"{buytime.isoformat()[0:10]}",
        "range_to":f"{buytime.isoformat()[0:10]}",
        "cont_flag":"1"
    }

    try:
        response_1min = fyers.history(data=data_1min)
        df_1min= pd.DataFrame(response_1min["candles"], columns=['date','open','high','low','close','volume'])
        df_1min['date'] =df_1min['date']+19800
        df_1min['daytime'] = pd.to_datetime(df_1min['date'], unit='s')
        if type_b_s == "b":
            result = sql(f"""
                    SELECT 
            result 
            FROM 
            (
                SELECT 
                *, 
                '{target}', 
                '{stoploss}', 
                CASE WHEN low < Cast('{stoploss}' AS INT) THEN 'loss' WHEN high > Cast('{target}' AS INT) THEN 'win' END AS result 
                FROM 
                df_1min 
                WHERE 
                date >= {epochbytime}
            ) 
            WHERE 
            result IN ('win', 'loss') 
            ORDER BY 
            date 
            limit 
            1
            """).values[0][0]
        elif type_b_s == "s":
            result = sql(f"""
                    SELECT 
            result 
            FROM 
            (
                SELECT 
                *, 
                '{target}', 
                '{stoploss}', 
                CASE WHEN high > Cast('{stoploss}' AS INT) THEN 'loss' WHEN low < Cast('{target}' AS INT) THEN 'win'  END AS result 
                FROM 
                df_1min 
                WHERE 
                date >= {epochbytime}
            ) 
            WHERE 
            result IN ('win', 'loss') 
            ORDER BY 
            date 
            limit 
            1
            """).values[0][0]
        else:
            result = "incorrect argument"
             
    except:
        return "ERROR"
    return result
