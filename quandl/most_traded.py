import pandas
import os
import quandl
import time
import datetime
import numpy

# Input file for NSE tickers, use to retrieve individual company stock data.
ticker_path = os.path.join(os.getcwd(), "tickers.csv")

# Output file for stock aggregates, written as a Pandas data frame.
table_path = os.path.join(os.getcwd(), "annual_stock.csv")

# Input file containing the Quandl auth token, this is downloaded
# from the Quandl dashboard and requires a (free) account.
auth_path = os.path.join(os.getcwd(), "auth.txt")

# Seperator used to read/write the data frame from/to files.
sep=','

# Lookup of semantic keys to actual column names
columns = {
    'ticker': 'Ticker',
    'date': 'Date',
    'ttq' : 'Total Trade Quantity'
}

# Get the data
import pudb; pudb.set_trace()
data = pandas.DataFrame()
try:
    data = pandas.read_csv(table_path, sep=sep)
except IOError:
    # TODO(beeps): better exception handling
    companies = pandas.read_csv(ticker_path, sep=sep, names=["ticker", "name"])
    with open(auth_path) as f:
        token = f.read().strip()
    for ticker in companies.ticker.tolist()[:5]:
        try:
            print 'STEP: indexing ticker %s' % ticker
            ticker_data = data.append(quandl.get(
                ticker, authtoken=token, transform="cumul", collapse="annual"))
            ticker_data[columns['ticker']] = ticker
            data = data.append(ticker_data)
        except:
            print 'WARNING: failed to retrieve %s' % ticker
    data.to_csv(table_path, sep='\t')

# Rank by traded volume
print data
