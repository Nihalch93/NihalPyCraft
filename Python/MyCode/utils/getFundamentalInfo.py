'''
This module fetches star rating data from https://ticker.finology.in
'''

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import os
import datetime
from tqdm import tqdm
import json

def getFundamentalInfo(NiftyStocks):
    try:
        if not os.path.exists(f"MyCode/ticker/finticker_{datetime.datetime.now().isoformat()[0:10]}.txt"):
            print("Creating a new file::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            driver = webdriver.Chrome(options=chrome_options)
            ticval = {}
            for symbol in tqdm(NiftyStocks, desc="Fetching Data..."):
                try:
                    if symbol == 'M&M':
                        driver.get(f"https://ticker.finology.in/company/SCRIP-100520")
                    elif symbol == 'M&MFIN':
                        driver.get(f"https://ticker.finology.in/company/SCRIP-132720")
                    if symbol == 'L&TFH':
                        driver.get(f"https://ticker.finology.in/company/SCRIP-220350")
                    else:
                        driver.get(f"https://ticker.finology.in/company/{symbol}")
                    time.sleep(1)
                    ratings = driver.find_element(By.XPATH, "//*[@id='mainContent_ValuationRating']").get_attribute('outerHTML').split("--rating:")[1].split(";")[0]
                    ticval[symbol] = ratings
                except Exception as e:
                    ticval[symbol] = "NA"
            driver.close()
            with open(f"MyCode/ticker/finticker_{datetime.datetime.now().isoformat()[0:10]}.txt", "w") as f:
                    f.write(json.dumps(ticval))
        else:
            print("reading from existing file...")
            with open(f"MyCode/ticker/finticker_{datetime.datetime.now().isoformat()[0:10]}.txt", "r") as f:
                ticval = json.loads(f.read())
        failedlist = {i for i in ticval if ticval[i]=="NA"}
        print(f"*FAILED* ticker stocks:: {failedlist}")
        print("Complete.")
        return ticval
    except Exception as e:
        print(f"Error:: Exception occured while reading ticker website {e}")