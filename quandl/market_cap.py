import pandas
import os
import quandl
import time
import datetime
import numpy

# I/O file for mktv table, written as a Pandas data frame.
table_path = os.path.join(os.getcwd(), "mktv.table")

# Input file containing the Quandl auth token, this is downloaded
# from the Quandl dashboard and requires a (free) account.
auth_path = os.path.join(os.getcwd(), "auth.txt")

# Name of the Quandl table dataset.
table='ZACKS/MKTV'

# Seperator used to read/write the data frame from/to files.
sep='\t'

# Lookup of semantic keys to actual column names
columns = {
    'date': 'per_end_date',
    'market_cap': 'mkt_val',
    'name': 'comp_name'
}

# Get the data
try:
    data = pandas.read_csv(table_path, sep=sep)
except IOError:
    # TODO(beeps): better exception handling
    with open(auth_path) as f:
        token = f.read().strip()
    print 'STEP: writing table %s into %s' % (table, table_path)
    data = quandl.get_table(table, api_key=token)
    data.to_csv(table_path, sep='\t')

# Rank by market cap
data[columns['date']] = pandas.to_datetime(data[columns['date']])
if data[columns['date']].dt.year.max() < datetime.datetime.now().year:
    print 'WARNING: data source is outdated...'

avg_func = lambda x: (x.groupby(columns['name'])
        .aggregate(numpy.average)
        .sort_values(columns['market_cap'], ascending=False)
        .head(5))

annual_index = data.groupby([data[columns['date']].map(lambda x: x.year)])
mktv = annual_index.apply(avg_func)[columns['market_cap']]

print mktv
