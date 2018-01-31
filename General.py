import numpy as np
import pandas as pd
import requests
import datetime
import time
import re


def get_prices(pos_list, dates):
    """
    :param:
    pos_list: list of tickers
    dates is a list of two dates in order from earliest to latest (mm/dd/yyyy)
    Ex. load_prices(['DGAZ'], ['12/12/2011', '12/21/2014'])

    :return:
    array of prices and dates with same index as pos_list
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


def load_pos_data(pos_list, format):
    """
    Loads csvs.

    :param:
    pos_list: list of of tickers you want to load from local (must have the data pre-downloaded)
    format: "df" (for pandas dataframe), "arr" (for numpy array).

    :return:
    list:
        |7 arrays: [Pos, Date, Open, High, Low, Close, Adj Close, Volume]|,
        |dataframe: Date, Open, High, Low, Close, Adj Close, Volume|
    """

    # load the data into pandas for each pos and append to data
    data = []
    for pos in pos_list:
        df = pd.read_csv('%s.csv' % pos)
        df.name = pos

        if format == 'arr':
            # transpose the values so each row is a column from the spreadsheet
            values = df.values.T
            date, opn, high, low, close, adjc, volume = values[0], values[1], values[2], values[3], values[4], \
                                                        values[5], values[6]
            data.append([pos, date, opn, high, low, close, adjc, volume])

        else:
            data.append(df)
    return data


class HistoricTechnicals:
    """
    Supports pandas dataframes. Contains many functions for technical analysis.
    Many of these functions won't work with live data. Will either make a new class
    for instantaneous updates or redo this and backload the work of figuring out
    proper inputs.
    Indicators:
        * CCI

    :param:
    data: dataframe format from load_pos_data(..., format='df')

    :return:
    1D numpy array of transformed data.
    """
    def __init__(self, data):
        self.data = data

    # commodity channel index
    def cci(self, roll_window):
        """
        :param:
        roll_window: size of the window for calculating rolling_mean and rolling_std.

        :return:
        cci transform array
        """
        tp = (self.data['High'] + self.data['Low'] + self.data['Close']) / 3
        cci = pd.Series((tp - tp.rolling(roll_window).mean()) / (0.015 * tp.rolling(roll_window).std()))
        return np.array(cci)

    # simple moving average
    def sma(self, roll_window):
        """
        :param:
        roll_window: size of the window for calculating rolling_mean and rolling_std.

        :return:
        sma transform array
        """
        return np.array(self.data['Close'].rolling(roll_window).mean())

    # exponentially-weighted moving average
    def ewma(self, roll_window):
        """
        :param:
        roll_window: size of the convolution window

        :return:
        ewma transform array
        """
        return np.array(pd.ewma(self.data['Close'], span=roll_window, min_periods=roll_window - 1))

    def rate(self, dt):
        """
        :param:
        dt: time differential over which the change is calculated

        :return:
        rate of change array
        """
        n = self.data['Close'].diff(dt)
        d = self.data['Close'].shift(dt)

        return np.array(n/d)

    def bollingers(self, roll_window):
        """
        :param:
        roll_window: size of the convolution window

        :return:
        2xDates array, [0] = Upper Band, [1] = Lower Band
        """
        mean = self.data['Close'].rolling(roll_window).mean()
        std = self.data['Close'].rolling(roll_window).std()
        upper = mean + (2*std)
        lower = mean - (2*std)
        return np.array([upper, lower])

    def force_ix(self, dt):
        """
        :param:
        dt: time differential over which the change is calculated

        :return:
        force_index numpy array
        """
        return np.array(self.data['Close'].diff(dt) * self.data['Volume'])

    def macd(self):
        """
        :param:
        None. :D

        :return:
        macd numpy array
        """
        return self.ewma(12) - self.ewma(26)
