import numpy as np
import pandas as pd
import requests
import datetime
import time
import re


def load_prices(pos_list, dates):
    """
    pos_list is a list of tickers
    dates is a list of two dates in order from earliest to latest (mm/dd/yyyy)
    returns an array of prices and dates with same index as pos_list
    Ex. load_prices(['DGAZ'], ['12/12/2011', '12/21/2014'])
    """

    # convert to unix time and verify dates
    valid_dates = np.array([int(date.strip('\n')) for date in list(open('Valid Dates', 'r'))])
    unix_dates = [int(time.mktime(datetime.datetime.strptime(date, "%m/%d/%Y").timetuple())) for date in dates]
    assert (len(unix_dates) == 2 and unix_dates[1] - unix_dates[0] > 0), \
        'Incorrect number of dates, or dates are not in order.'

    # pick the nearest trading days to the dates specified
    date_distances = np.abs([valid_dates - date for date in unix_dates])
    min_distances = np.min(date_distances, axis=1)
    nearest_date_ixs = np.where(date_distances[0] == min_distances[0])[0][0], \
                       np.where(date_distances[1] == min_distances[1])[0][0]
    valid_unix_dates = [valid_dates[ix] for ix in nearest_date_ixs]

    # for each pos in the pos_list, pull the data from yahoo finance over the date range and download history
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
                   '%s&interval=1d&events=history&crumb=%s' % \
                   (pos, str(valid_unix_dates[0]), str(valid_unix_dates[1]), crumb)
        response = requests.get(data_url, cookies=cookie)
        assert ('error' not in response.text), 'Dates are out of range for this pos.'

        with open(filename, 'wb') as handle:
            for block in response.iter_content(1024):
                handle.write(block)





