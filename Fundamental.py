import os
import csv
import time
import json
import requests
import datetime as datetime
import pandas as pd
import matplotlib.pyplot as plt

def getKey(myKeyFile):
    keyFile = open(myKeyFile, "r") # file with API key
    myKey = keyFile.read()
    return myKey

def getSymbols(market):
    print(market)
    symbols = []
    print("Input all symbols, type done when finished")
    sym = ""
    while(sym != "done"): # check if in market?!
        sym = input()
        symbols.append(sym)
    symbols = symbols[:-1] # remove 'done'
    return symbols

def getDataFromAPI(symbol, APIKey):
    relevant_data = {}
    base_url = 'https://www.alphavantage.co/query?'
    functions = ['OVERVIEW', 'INCOME_STATEMENT', 'BALANCE_SHEET']

    print("Symbol : ", symbol)
    test = symbol + '_overview'
    print("Concatted : ", test )
    wait = 20
    for f in functions:
        params = {'function': f,
            'symbol': symbol,
            'apikey': APIKey}
        response = requests.get(base_url, params=params)
        response_dict = response.json()
        print("AlphaVantage API call (every {w} sec)".format(w = wait))
        if(f == 'OVERVIEW'):
            overview_data = {}
            overview_data["EBITDA"] = response_dict['EBITDA']
            overview_data["PriceToBookRatio"] = response_dict['PriceToBookRatio']
            overview_data["EVToEBITDA"] = response_dict['EVToEBITDA']

            relevant_data[symbol + '_overview'] = overview_data
        elif(f == 'INCOME_STATEMENT'):
            #print(response_dict)
            if(not response_dict['annualReports']): continue
            latest_report = response_dict['annualReports'][0]
            relevant_data[symbol + '_report'] = latest_report
        elif(f == 'BALANCE_SHEET'):
            #print(response_dict)
            if(not response_dict['annualReports']): continue
            #print("Balance lol")
            latest_report = response_dict['annualReports'][0]
            #print(latest_report)
            relevant_data[symbol + '_report'] = latest_report
        time.sleep(wait)
    return relevant_data

def writeDataToFile(data, name, end='.txt'):
    filename = name + end
    print("Writing to file ", filename)
    with open(filename, 'w') as file:
        file.write(data)

def readJsonFromFile(name, end='.txt'):
    filename = name + end
    with open(filename, "r") as file:
        raw = file.read()
    data = json.loads(raw)
    file.close()
    return data

def readDataFromFile(name, end='.txt'):
    filename = name + end
    with open(filename, "r") as file:
        raw = file.read()
    file.close()
    return raw

def shouldUpdate(update_file):

    today = time.strftime("%Y-%m-%d", time.localtime())
    last_update = readDataFromFile(update_file)

    moreThanOneYear = (int(today[:4]) - int(last_update[:4]) > 0)
    moreThanOneMonth = (int(today[5:7]) - int(last_update[5:7]) > 0)
    moreThanTenDays = (int(today[8:]) - int(last_update[8:]) > 10)

    return moreThanOneYear or moreThanOneMonth or moreThanTenDays

def getData(symbol, market, APIKey):
    relevant_data = {}
    filepath = "data/" + market + "/" + symbol
    if os.path.isfile(filepath + '.txt') or shouldUpdate("data/" + market): # or no recent update
        print("File exists for ", symbol)
        relevant_data = readJsonFromFile(filepath)
    else:
        print("no file exists, creating file for ", symbol)
        relevant_data = getDataFromAPI(symbol, APIKey)
        writeDataToFile(json.dumps(relevant_data), filepath)
    return relevant_data

def getMarkets():
    df = pd.read_csv("data/current_symbols.txt", sep=',')
    return df, df.exchange.unique()

def getSymbols(df, market):
    stocks = df[df.exchange == market]
    symbols = stocks.symbol

    all_sym = symbols.tolist()

    return all_sym

def getCurrentSymbols(APIKey):    
    update = shouldUpdate("data/" + "Last_update")

    if(not update):
        print("No update")
        return
    else:
        print("Updating")

    base_url = 'https://www.alphavantage.co/query?'
    params = {'function': "LISTING_STATUS",
            'apikey': APIKey}
    response = requests.get(base_url, params=params)

    filename = "current_symbols"
    writeDataToFile(response.text, "data/" + filename)
    writeDataToFile(today, "data/Last_update")

def getMarketInput(markets):
    a = ""
    while(a not in markets):
        print("Please choose a market {m}: ".format(m = markets))
        a = input()
        a = a.upper()
    return a

def rankFromSingle(symbols, APIKey, key, f):
    market = 'NYSE MKT'
    data = {}
    for symbol in symbols:
        all_data = getData(symbol, market, APIKey)
        relevant = all_data[symbol + '_' + f]
        if(relevant[key] == "None"): continue

        data[symbol] = float(relevant[key])
        print(relevant)

    return sorted(data, key=data.__getitem__, reverse=True) # first best

def main():
    APIKey = getKey("APIkey.txt")

    getCurrentSymbols(APIKey) # update or do nothing

    df, markets = getMarkets()

    #selectedMarket = getMarketInput(markets)
    selectedMarket = markets[3]
    symbols = getSymbols(df, selectedMarket) # all relevant symbols    
    
    print("There is {n} symbols in the selected market ({m})".format(n = len(symbols), m = selectedMarket))

    print("Collecting data will take as long as {n} seconds".format(n = 15*len(symbols)))
    data = {}

    #getDataFromAPI('ATNM', APIKey)

    #for symbol in symbols:
    #    data[symbol] = getData(symbol, selectedMarket, APIKey)

    
    today = time.strftime("%Y-%m-%d", time.localtime())
    writeDataToFile(today, "data/" + selectedMarket)
    print(len(data))
    
    symbols = ['AAMC', 'AAU', 'AGE', 'AIM', 'AIRI']
    print(rankFromSingle(symbols, APIKey, 'totalAssets', 'report')) # overview + 'EBITDA'


    # Fix Last_update.txt file

#Convert to pandas dataframe
#df = pd.DataFrame.from_dict(response_dict, orient='index')
#print(df)


if __name__ == '__main__':
    main()