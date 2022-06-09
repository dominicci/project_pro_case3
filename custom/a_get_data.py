import yfinance as yf
import datetime as dt

#Set the cryptocurrency tickers to get the data
crypto = 'BTC-USD'

#Define the start and end date for the historical data
today = dt.datetime.now()
start = dt.datetime(2018, 1, 1,)
end = dt.date(today.year, today.month, today.day)

#Fetch bitcoin data using yfinance download function.
btc_df = yf.download(tickers=crypto, start=start, end=end, interval='1d',)
