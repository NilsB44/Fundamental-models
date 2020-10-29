import os
import time
import requests
import pandas as pd
import matplotlib.pyplot as plt


myKey = "C5V82ZCI87R2RXFF"

base_url = 'https://www.alphavantage.co/query?'

relevant_data = {}

functions = ['OVERVIEW', 'INCOME_STATEMENT', 'BALANCE_SHEET']

symbols = []
print("Input all symbols, type done when finished")

sym = ""
while(sym != "done"):
    sym = input()
    symbols.append(sym)
symbols = symbols[:-1] # remove 'done'

for symbol in symbols:
    for f in functions:
        params = {'function': f,
            'symbol': symbol,
            'apikey': myKey}
        response = requests.get(base_url, params=params)
        response_dict = response.json()
        print("   RELEVANT DATA   ")
        if(f == 'OVERVIEW'):
            print("Symbol: ", response_dict['Symbol'])
            print("EBITDA: ", response_dict['EBITDA'])
            print("PriceToBookRatio: ", response_dict['PriceToBookRatio'])
            print("EVToEBITDA: ", response_dict['EVToEBITDA'])
        elif(f == 'INCOME_STATEMENT'):
            print(response_dict['annualReports'])
        elif(f == 'BALANCE_SHEET'):
            print("Balance lol")
            #print(response_dict)
        time.sleep(0.2)
    time.sleep(0.5)






#Convert to pandas dataframe
#df = pd.DataFrame.from_dict(response_dict, orient='index')
#print(df)

#data, meta_data = ts.get_intraday(symbol='MSFT',interval='1min')
#data = ts.get_overview(symbol='MSFT')
#print(data.head())
#data['4. close'].plot()
#plt.title('Intraday Times Series for the MSFT stock (1 min)')
#plt.show()

