import quandl
import datetime

quandl.ApiConfig.api_key = 'Sy2fu8Zj4etJRGWvZPUx'

stock_date_dict = {'AAPL': {'1Q18': '2018-04-19'}, 'WMT': {'3Q17': '2017-10-7'}, 'JNJ': {'3Q18': '2018-10-15'}}
data_dict = {}
today = datetime.date.today()
THREEMO = datetime.timedelta(days=91)
SIXMO = datetime.timedelta(days=182)
ONEYR = datetime.timedelta(days=365)

def get_closing_prices(ticker, fdate):
    date_as_ints = [int(x) for x in fdate.split('-')]
    date_before = datetime.date(date_as_ints[0], date_as_ints[1], date_as_ints[2])
    three_mo_aftr = date_before + THREEMO
    six_mo_aftr = date_before + SIXMO
    one_yr_aftr = date_before + ONEYR
    day_before_p =  quandl.get('WIKI/' + ticker + ".11", start_date=date_before.isoformat(), rows=1)
    three_mo_rtrn = day_before_p / quandl.get('EOD/' + ticker + ".11", start_date=three_mo_aftr.isoformat(), end_date=three_mo_aftr.isoformat(), rows=1) - 1
    six_mo_rtrn = day_before_p / quandl.get('EOD/' + ticker + ".11", start_date=six_mo_aftr.isoformat(), end_date=six_mo_aftr.isoformat(), rows=1) - 1
    one_yr_rtrn = day_before_p / quandl.get('EOD/' + ticker + ".11", start_date=one_yr_aftr.isoformat(), end_date=one_yr_aftr.isoformat(), rows=1) - 1
    print([day_before_p, three_mo_rtrn, six_mo_rtrn, one_yr_rtrn])

# for each filing, store the following:
# filing_date: date on which the 10-Q or 10-K was filed
# day_before_close: closing price day before filing. This takes time of filing
#       (pre-market or post-market) out of the equation
# three_mo_rtrn: 3 month return on day_before_close
# six_mo_rtrn: 6 month return on day_before_close
# one_yr_rtrn: 12 month return on day_before_close
for ticker, filing_dict in stock_date_dict.items():
    for filing, fdate in filing_dict.items():
        get_closing_prices(ticker, fdate)
        data_dict[ticker + '_' + filing] = {'filing_date': fdate, 'day_before_close': None, 'three_mo_rtrn': None, 'six_mo_rtrn': None, 'one_yr_rtrn': None}
