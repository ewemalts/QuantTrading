import numpy as np
import pandas as pd
import requests
import datetime
import time
import re

def load_prices(pos_list, dates):
    # pos_list is a list of tickers
    # dates is a list of two dates in order from earliest to latest (mm/dd/yyyy)
    # returns an array of prices and dates with same index as pos_list

    # convert to unix time and verify dates
    valid_dates = np.array([int(date.strip('\n')) for date in list(open('Valid Dates', 'r'))])
    # resume here, pick the nearest date in valid dates to the date provided....
    timestamps = [int(time.mktime(datetime.datetime.strptime(date, "%m/%d/%Y").timetuple())) for date in dates]
    assert (len(timestamps) == 2 and timestamps[1] - timestamps[0] > 0), \
        'Incorrect number of dates, or dates are not in order.'

    # for each pos in the pos_list, pull the data from yahoo finance over the date range
    for pos in pos_list:
        # first get the cookie and crumb
        pos_url = "https://finance.yahoo.com/quote/%s/?p=%s" % (pos, pos)
        r = requests.get(pos_url)
        cookie = {'B': r.cookies['B']}
        lines = r.content.decode('unicode-escape').strip().replace('}', '\n').split('\n')
        for l in lines:
            if re.findall(r'CrumbStore', l):
                crumb = l.split(':')[2].strip('"')

        # download the pos.csv
        filename = '%s.csv' % pos
        data_url = 'https://query1.finance.yahoo.com/v7/finance/download/%s?period1=%s&period2=' \
                   '%s&interval=1d&events=history&crumb=%s' % (pos, str(dates[0]), str(dates[1]), crumb)
        #response = requests.get(data_url, cookies=cookie)
        #with open(filename, 'wb') as handle:
            #for block in response.iter_content(1024):
                #handle.write(block)



load_prices(['DGAZ'], ['01/09/2011', '01/09/2012'])

