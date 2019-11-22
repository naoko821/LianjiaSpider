# -*- coding: utf-8 -*-
from common import read, plot
import pandas as pd
import sys
import os
def plotArea(city, area):
    df = read(city)
    df = df.dropna(subset = ['小区'])
    df = df.loc[df['小区'].str.contains(area)]
    print('data count:', len(df))
    gp = df.groupby(['成交时间'])['成交价(元/平)']
    res=pd.DataFrame({"volume":gp.size(),"median_price":gp.median(), "mean_price":gp.mean()})
    res = res.iloc[:len(res),:]
    city = 'default'
    MA = True
    start_date = None
    force = True
    keep_all = True
    for ma_length in [1, 30, 60, 90]:
        title = '%s-%d日均线'%(area, ma_length)
        plot(res, city, title, MA, ma_length, start_date, force, keep_all)
if __name__ == '__main__':
    if len(sys.argv) == 3:
        city = sys.argv[1]
        area = sys.argv[2]
        plotArea(city, area)
    else:
        print("usage: python3 plotAreaFromData.py [city] [area]")
