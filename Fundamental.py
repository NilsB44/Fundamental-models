import os
import time
import json
import requests
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
        print("   COLLECTING RELEVANT DATA   ")
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
        time.sleep(1)
    return relevant_data

def writeDataToFile(data, symbol):
    filename = symbol + '.txt'
    print("Writing to file ", filename)
    with open(filename, 'w') as file:
        file.write(json.dumps(data))

def readDataFromFile(symbol):
    filename = symbol + '.txt'
    with open(filename, "r") as stockfile:
        raw = stockfile.read()
    data = json.loads(raw)
    stockfile.close()
    return data

def getData(symbols, APIKey):
    relevant_data = {}
    for symbol in symbols:
        if os.path.isfile(filename):
            print("has file")
            data = readDataFromFile(symbol)
        else:
            data = getDataFromAPI(symbol, APIKey)
            writeDataToFile(data, symbol)


def main():
    APIKey = getKey("APIkey.txt")
    #symbols = getSymbols("DJ") # market here?
    #print(APIKey)
    #print(symbols)

    print("Testing read")
    data = readDataFromFile("IBM")
    print(data["Test"])
    print("OK")






#Convert to pandas dataframe
#df = pd.DataFrame.from_dict(response_dict, orient='index')
#print(df)

#data, meta_data = ts.get_intraday(symbol='MSFT',interval='1min')
#data = ts.get_overview(symbol='MSFT')
#print(data.head())
#data['4. close'].plot()
#plt.title('Intraday Times Series for the MSFT stock (1 min)')
#plt.show()

if __name__ == '__main__':
    main()