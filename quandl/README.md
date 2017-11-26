# Quandl stock API

A typical query
```console
https://www.quandl.com/api/v3/datatables/ZACKS/MKTV.json?qopts.columns=per_end_date,per_type,mkt_val,ep_val\&ticker=AAPL\&api_key=emqe_JCJbwo6--VqWaLg
```

A typical query from python
```python
In[1]: data = quandl.get_table(
    'ZACKS/MKTV',
    paginate=True,
    ticker=['AAPL', 'MSFT'],
    per_end_date={'gte': '2015-01-01'},
    qopts={'columns':['ticker', 'per_end_date', 'per_type', 'mkt_val']},
    api_key=token)

...

In [2]: type(data)
Out[2]: pandas.core.frame.DataFrame
```

Top 5 NASDAQ companies by market cap (NB: facebook and Google aren't part of the public dataset):
```console
per_end_date  comp_name
2015          APPLE INC          664453.345000
              MICROSOFT CORP     370235.147500
              EXXON MOBIL CRP    334618.625000
              JOHNSON & JOHNS    273133.315000
              GENL ELECTRIC      266341.420000

2016          APPLE INC          582588.735000
              MICROSOFT CORP     441172.390000
              EXXON MOBIL CRP    367955.555000
              JOHNSON & JOHNS    317181.907500
              GENL ELECTRIC      282407.827500

2017          APPLE INC          766893.376667
              MICROSOFT CORP     538302.470000
              JOHNSON & JOHNS    347651.866667
              EXXON MOBIL CRP    345708.033333
              JPMORGAN CHASE     324448.270000
```

Top 5 Indian companies by share trade volume:
```console
TODO
```

