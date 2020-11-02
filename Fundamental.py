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

    for f in functions:
        params = {'function': f,
            'symbol': symbol,
            'apikey': APIKey}
        response = requests.get(base_url, params=params)
        response_dict = response.json()
        print("AlphaVantage Limites the rate of the API call to once every 5 sec")
        if(f == 'OVERVIEW'):
            overview_data = {}
            overview_data["EBITDA"] = response_dict['EBITDA']
            overview_data["PriceToBookRatio"] = response_dict['PriceToBookRatio']
            overview_data["EVToEBITDA"] = response_dict['EVToEBITDA']

            relevant_data[symbol + '_overview'] = overview_data
        elif(f == 'INCOME_STATEMENT'):
            latest_report = response_dict['annualReports'][0]
            relevant_data[symbol + '_report'] = latest_report
        elif(f == 'BALANCE_SHEET'):
            #print("Balance lol")
            latest_report = response_dict['annualReports'][0]
            print(latest_report)
            relevant_data[symbol + '_report'] = latest_report
        time.sleep(5)
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

def getData(symbol, APIKey):
    relevant_data = {}
    filename = symbol + '.txt'
    if os.path.isfile(filename):
        print("File exists for ", symbol)
        relevant_data = readJsonFromFile("data/" + symbol)
    else:
        print("no file exists, creating file for ", symbol)
        relevant_data = getDataFromAPI(symbol, APIKey)
        writeDataToFile(json.dumps(relevant_data), "data/" + symbol)
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

    today = time.strftime("%Y-%m-%d", time.localtime())
    last_update = readDataFromFile("data/" + "Last_update")

    moreThanOneYear = (int(today[:4]) - int(last_update[:4]) > 0)
    moreThanOneMonth = (int(today[5:7]) - int(last_update[5:7]) > 0)
    moreThanTenDays = (int(today[8:]) - int(last_update[8:]) > 10)
    shouldUpdate = moreThanOneYear or moreThanOneMonth or moreThanTenDays

    if(not shouldUpdate):
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

def main():
    APIKey = getKey("APIkey.txt")

    getCurrentSymbols(APIKey) # update or do nothing

    df, markets = getMarkets()

    #selectedMarket = getMarketInput(markets)
    selectedMarket = markets[3]
    symbols = getSymbols(df, selectedMarket) # all relevant symbols    
    
    print("There is {n} symbols in the selected market ({m})".format(n = len(symbols), m = selectedMarket))

    data = getData(symbols[0], APIKey)



#Convert to pandas dataframe
#df = pd.DataFrame.from_dict(response_dict, orient='index')
#print(df)


if __name__ == '__main__':
    main()