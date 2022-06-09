import yfinance as yf
import datetime as dt

#Set the cryptocurrency tickers to get the data
crypto = 'BTC-USD'

#Define the start and end date for the historical data
today = dt.datetime.now()
start = dt.datetime(2018, 1, 1,)
end = dt.date(today.year, today.month, today.day)

#Fetch bitcoin data using yfinance download function.
data = yf.download(tickers=crypto, start=start, end=end, interval='1d',)

data.rename(columns={'Adj Close':'Adj_Close'}, inplace=True)
data = data.reset_index()
data['Year'] = data['Date'].dt.year

# print(data.tail())