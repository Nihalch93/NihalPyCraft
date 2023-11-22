import time 

def getCurrentPrice(fyers,symbol):
    try:
        data = {
        "symbols":f"NSE:NIFTY50-INDEX"
        }
        response = fyers.quotes(data=data)
        last_traded_price = response["d"][0]["v"]["lp"]
        return last_traded_price
        time.sleep(5)
    except Exception as e:
        print(f"ERROR: exception while fetching current price for {symbol}:: {e} ")
        
    