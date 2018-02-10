import General
import numpy as np
import pandas as pd

pos_list = ['DGAZ', 'UGAZ', 'DSLV', 'USLV', 'DGLD', 'UGLD', 'SCO', 'UCO']
General.get_prices(pos_list, ['12/12/2012', '2/7/2018'])
data = General.load_pos_data(pos_list, 'ls')

close_prices = np.array([len(pos[5]) for pos in data])
dates = [list(pos[1]) for pos in data]
# print(dates)

for pos in dates:
    for date in pos:
        for i in range(len(dates)):
            if date not in dates[i]:
                print(pos_list[i], date)